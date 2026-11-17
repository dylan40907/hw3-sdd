import { test } from 'node:test';
import assert from 'node:assert/strict';
import { saveAnswer, versionFor, openQuestion, correctAnswer } from '../js/rules/versions.js';
import { newSession } from '../js/rules/start-page.js';
import { exam, students } from '../js/data/mock-data.js';
import { T0 } from './helpers.js';

const studentA = students.find((s) => s.id === 's1');

test('FR-004: versionFor gives the same version for the same student and question', () => {
  for (const q of exam.questions) {
    assert.deepEqual(versionFor('s1', q), versionFor('s1', q));
    for (const [key, value] of Object.entries(versionFor('s1', q))) {
      assert.ok(q.params[key].includes(value));
    }
  }
});

test('FR-004 REQ-03: two students get their own version of each question, and each is recorded', () => {
  let a = newSession(exam, studentA);
  let b = newSession(exam, students.find((s) => s.id === 's2'));
  for (const q of exam.questions) {
    assert.notDeepEqual(versionFor('s1', q), versionFor('s2', q), `same version for ${q.id}`);
    a = openQuestion(a, q, T0);
    b = openQuestion(b, q, T0);
    assert.deepEqual(a.versions[q.id], { params: versionFor('s1', q), assignedAt: T0 });
    assert.deepEqual(b.versions[q.id], { params: versionFor('s2', q), assignedAt: T0 });
  }
});

test('FR-004: opening a question again does not change the recorded version', () => {
  const q = exam.questions[0];
  const once = openQuestion(newSession(exam, studentA), q, T0);
  const changed = { ...once, versions: { [q.id]: { params: { d: 1, t: 1 }, assignedAt: T0 } } };
  assert.deepEqual(openQuestion(changed, q, T0 + 1000).versions[q.id], changed.versions[q.id]);
});

test('FR-009: correctAnswer uses the version params', () => {
  const q2 = exam.questions[1];
  assert.equal(correctAnswer(q2, { a: 6, b: 7 }), 42);
});

test('FR-003: saveAnswer stores the value and the save time', () => {
  const session = saveAnswer(newSession(exam, studentA), 'q1', '42', T0);
  assert.equal(session.answers.q1.value, '42');
  assert.equal(session.answers.q1.savedAt, T0);
});

test('FR-003: saving again keeps an earlier submit time', () => {
  let session = saveAnswer(newSession(exam, studentA), 'q1', '42', T0);
  session = { ...session, answers: { q1: { ...session.answers.q1, submittedAt: T0 + 1 } } };
  session = saveAnswer(session, 'q1', '43', T0 + 2);
  assert.equal(session.answers.q1.submittedAt, T0 + 1);
  assert.equal(session.answers.q1.value, '43');
});
