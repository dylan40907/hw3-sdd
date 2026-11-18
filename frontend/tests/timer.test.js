import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  baseDurationMs, endTime, remainingMs, isEnded, finishExam, openPause, closePause, pauseLog, questionsHidden,
} from '../js/rules/timer.js';
import { newSession } from '../js/rules/start-page.js';
import { exam, students } from '../js/data/mock-data.js';
import { helpFormHtml } from '../js/ui/student-view.js';
import { MIN, T0 } from './helpers.js';

const studentA = students.find((s) => s.id === 's1');

function started(student = studentA, at = T0) {
  return { ...newSession(exam, student), confirmedAt: at, startedAt: at };
}

test('FR-001: base duration applies the approved extra time', () => {
  assert.equal(baseDurationMs(60, 50), 90 * MIN);
  assert.equal(baseDurationMs(60, 0), 60 * MIN);
});

test('FR-001 REQ-01: 50% extra time on a 60-minute exam ends 90 minutes after the start', () => {
  assert.equal(endTime(started(), T0), T0 + 90 * MIN);
});

test('FR-001: remaining time counts down from the end time', () => {
  assert.equal(remainingMs(started(), T0 + 30 * MIN), 60 * MIN);
  assert.equal(remainingMs(started(), T0 + 200 * MIN), 0);
});

test('FR-009: the exam ends at the end time', () => {
  const session = started();
  assert.equal(isEnded(session, T0 + 90 * MIN - 1), false);
  assert.equal(isEnded(session, T0 + 90 * MIN), true);
});

test('FR-009: Finish exam ends the exam right away', () => {
  const finished = finishExam(started(), T0 + 10 * MIN);
  assert.equal(finished.endedAt, T0 + 10 * MIN);
  assert.equal(isEnded(finished, T0 + 10 * MIN), true);
});

test('FR-022: after a reload the timer has kept running', () => {
  const session = started();
  const reloaded = JSON.parse(JSON.stringify(session));
  assert.equal(reloaded.startedAt, session.startedAt);
  assert.equal(remainingMs(reloaded, T0 + 45 * MIN), 45 * MIN);
});

const studentB = students.find((s) => s.id === 's2');

test('FR-010 REQ-10: a 2-minute help request with 20 minutes left still leaves 20 minutes', () => {
  let session = started(studentB);
  assert.equal(remainingMs(session, T0 + 40 * MIN), 20 * MIN);
  session = openPause(session, T0 + 40 * MIN, 'Technical problem');
  assert.equal(questionsHidden(session), true, 'questions hidden while help is open');
  assert.equal(remainingMs(session, T0 + 41 * MIN), 20 * MIN, 'frozen while open');
  session = closePause(session, T0 + 42 * MIN);
  assert.equal(remainingMs(session, T0 + 42 * MIN), 20 * MIN);
  assert.equal(questionsHidden(session), false);
});

test('FR-010: only one help request can be open at a time', () => {
  const session = openPause(started(studentB), T0 + MIN, 'Technical problem');
  assert.equal(openPause(session, T0 + 2 * MIN, 'Technical problem').ok, false);
  assert.equal(closePause(started(studentB), T0 + MIN).ok, false);
});

test('FR-011 REQ-11: each pause is recorded with its reason and length', () => {
  const session = closePause(openPause(started(studentB), T0 + 40 * MIN, 'Technical problem'), T0 + 42 * MIN);
  assert.deepEqual(pauseLog(session), [
    { reason: 'Technical problem', from: T0 + 40 * MIN, to: T0 + 42 * MIN, lengthMs: 2 * MIN },
  ]);
});

test('FR-020: a help request still open at the end time moves the end time later by the pause length', () => {
  let session = openPause(started(studentB), T0 + 59 * MIN, 'Technical problem');
  assert.equal(isEnded(session, T0 + 60 * MIN), false);
  assert.equal(remainingMs(session, T0 + 64 * MIN), MIN);
  session = closePause(session, T0 + 65 * MIN);
  assert.equal(endTime(session, T0 + 65 * MIN), T0 + 66 * MIN);
  assert.equal(isEnded(session, T0 + 66 * MIN), true);
});

test('FR-010 REQ-10: a help request needs a reason; an empty or blank reason is refused', () => {
  for (const reason of ['', '   ', undefined]) {
    assert.equal(openPause(started(studentB), T0 + MIN, reason).ok, false, String(reason));
  }
});

test('FR-010 FR-011: the pause stores the trimmed reason the student gave, picked or typed', () => {
  const picked = openPause(started(studentB), T0 + MIN, exam.helpReasons[0]);
  assert.equal(pauseLog(picked)[0].reason, exam.helpReasons[0]);
  const typed = closePause(openPause(started(studentB), T0 + MIN, '  My screen froze  '), T0 + 3 * MIN);
  assert.deepEqual(pauseLog(typed), [{ reason: 'My screen froze', from: T0 + MIN, to: T0 + 3 * MIN, lengthMs: 2 * MIN }]);
});

test('FR-010: the exam offers a list of help reasons to pick from', () => {
  assert.ok(Array.isArray(exam.helpReasons));
  assert.ok(exam.helpReasons.length > 0);
  for (const reason of exam.helpReasons) assert.ok(typeof reason === 'string' && reason.trim() !== '');
});

test('FR-010: a half-typed or picked help reason is kept when the exam page is rendered again', () => {
  const draft = { studentId: 's1', picked: exam.helpReasons[1], typed: 'My screen froze' };
  // The page is rendered again (for example after a page-leave signal): the same draft goes in again.
  for (let render = 0; render < 2; render += 1) {
    const html = helpFormHtml(exam.helpReasons, draft);
    assert.ok(html.includes('value="My screen froze"'), 'typed text kept');
    assert.ok(html.includes(`<option value="${exam.helpReasons[1]}" selected>`), 'picked reason kept');
    assert.equal(html.split(' selected>').length - 1, 1, 'only the picked reason is selected');
  }
});

test('FR-010: with nothing picked or typed the help form is empty, and typed text is escaped', () => {
  const empty = helpFormHtml(exam.helpReasons, { studentId: 's1', picked: '', typed: '' });
  assert.ok(empty.includes('value=""'));
  assert.ok(!empty.includes(' selected>'));
  const escaped = helpFormHtml(exam.helpReasons, { studentId: 's1', picked: '', typed: '"><b>x' });
  assert.ok(!escaped.includes('"><b>x'));
});
