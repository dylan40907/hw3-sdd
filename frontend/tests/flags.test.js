import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  flagView, keep, dismiss, canRefer, studentFlags, requestExplanation, submitExplanation,
} from '../js/rules/flags.js';
import { recordSignal, startLeave, endLeave, submitAnswer } from '../js/rules/signals.js';
import { applyGroups } from '../js/rules/grouping.js';
import { stateWith, startedSession } from './state-fixtures.js';
import { T0, MIN } from './helpers.js';

const pauses = [{ id: 'p1', reason: 'help request', from: T0 + 5 * MIN, to: T0 + 7 * MIN }];

// One signal of each type for s1, plus group signals for s3 and s4.
function stateWithAllTypes() {
  let state = stateWith({ s1: startedSession('s1', T0, { pauses }) });
  state = recordSignal(state, 's1', 'fullscreen_exit', {}, T0 + 10 * MIN);
  state = recordSignal(state, 's1', 'paste', { questionId: 'q1' }, T0 + 11 * MIN);
  const s1 = startLeave(state.sessions.s1, T0 + 12 * MIN);
  state = endLeave({ ...state, sessions: { s1 } }, 's1', T0 + 13 * MIN);
  state = submitAnswer(state, 's1', 'q2', T0 + 13 * MIN + 12000);
  state = applyGroups(state, [{ id: 'q2:50', questionId: 'q2', value: 50, studentIds: ['s1', 's3', 's4'] }], T0 + 20 * MIN);
  return state;
}

function newFlagsOf(state) {
  return state.flags.filter((f) => !f.id.startsWith('flag-s'));
}

test('FR-012: every recorded signal becomes exactly one new flag', () => {
  const state = stateWithAllTypes();
  for (const signal of state.signals) {
    assert.equal(state.flags.filter((f) => f.signalId === signal.id).length, 1, signal.id);
  }
  for (const flag of newFlagsOf(state)) assert.equal(flag.state, 'new');
});

test('FR-012 REQ-12: a flag shows what happened, when, why and the context', () => {
  const state = stateWithAllTypes();
  const types = new Set();
  for (const flag of newFlagsOf(state).filter((f) => f.studentId === 's1')) {
    const view = flagView(flag, state);
    assert.deepEqual(Object.keys(view).sort(), ['context', 'signal', 'until', 'what', 'when', 'why']);
    assert.ok(view.what.length > 0);
    assert.ok(view.why.length > 0);
    assert.equal(typeof view.when, 'number');
    assert.equal(view.context.extraTimePct, 50);
    assert.deepEqual(view.context.pauses, [{ reason: 'help request', from: T0 + 5 * MIN, to: T0 + 7 * MIN, lengthMs: 2 * MIN }]);
    types.add(view.signal.type);
  }
  assert.equal(types.size, 5);
});

test('FR-012 FR-008: the fast-answer flag says how soon after returning it was', () => {
  const state = stateWithAllTypes();
  const flag = newFlagsOf(state).find((f) => flagView(f, state).signal.type === 'fast_answer');
  assert.match(flagView(flag, state).why, /12 s after returning to the exam page \(limit 30 s\)/);
});

test('FR-012 FR-009: a group flag lists the shared answer and the other students', () => {
  const state = stateWithAllTypes();
  const flag = newFlagsOf(state).find((f) => f.studentId === 's3');
  const view = flagView(flag, state);
  assert.equal(view.context.group.value, 50);
  assert.deepEqual(view.context.group.otherStudents, ['Student A', 'Student D']);
});

test('FR-013 REQ-13: the student cannot see a new or kept flag', () => {
  const state = stateWithAllTypes();
  assert.deepEqual(studentFlags(state.flags, 's1'), []);
  const kept = state.flags.map((f) => (f.studentId === 's1' ? keep(f) : f));
  assert.deepEqual(studentFlags(kept, 's1'), []);
});

test('FR-013: keep works only on a new flag', () => {
  const flag = newFlagsOf(stateWithAllTypes())[0];
  const kept = keep(flag);
  assert.equal(kept.state, 'kept');
  assert.equal(keep(kept).ok, false);
});

test('FR-014 REQ-14: a dismissed flag cannot be referred', () => {
  const flag = newFlagsOf(stateWithAllTypes())[0];
  for (const from of ['new', 'kept', 'explanation_requested', 'explained']) {
    const dismissed = dismiss({ ...flag, state: from, deadline: T0 });
    assert.equal(dismissed.state, 'dismissed', from);
    assert.equal(canRefer(dismissed, T0 + 10 * 86400000), false);
  }
});

test('FR-014: a dismissed flag is final', () => {
  const dismissed = dismiss(newFlagsOf(stateWithAllTypes())[0]);
  assert.equal(keep(dismissed).ok, false);
  assert.equal(dismiss(dismissed).ok, false);
});

const DAY = 86400000;

function twoKeptFlags() {
  let state = stateWith({ s1: startedSession() });
  state = recordSignal(state, 's1', 'paste', { questionId: 'q1' }, T0 + MIN);
  state = recordSignal(state, 's1', 'fullscreen_exit', {}, T0 + 2 * MIN);
  const [a, b] = newFlagsOf(state);
  return { state, a: keep(a), b: keep(b) };
}

test('FR-015: an explanation can be requested only on a kept flag, with a 3-day deadline', () => {
  const { a } = twoKeptFlags();
  const requested = requestExplanation(a, T0 + DAY);
  assert.equal(requested.state, 'explanation_requested');
  assert.equal(requested.explanationRequestedAt, T0 + DAY);
  assert.equal(requested.deadline, T0 + 4 * DAY);
  assert.equal(requestExplanation(requested, T0 + DAY).ok, false);
  assert.equal(requestExplanation({ ...a, state: 'new' }, T0).ok, false);
});

test('FR-015 REQ-15: the student sees only the flag they were asked to explain, with its deadline', () => {
  const { a, b } = twoKeptFlags();
  const requested = requestExplanation(a, T0 + DAY);
  const visible = studentFlags([requested, b], 's1');
  assert.equal(visible.length, 1);
  assert.equal(visible[0].id, a.id);
  assert.equal(visible[0].deadline, T0 + 4 * DAY);
});

test('FR-014: a flag dismissed after an explanation request is still shown, marked as dismissed', () => {
  const { a } = twoKeptFlags();
  const dismissed = dismiss(requestExplanation(a, T0 + DAY));
  const visible = studentFlags([dismissed], 's1');
  assert.equal(visible.length, 1);
  assert.equal(visible[0].dismissed, true);
});

test('FR-016 REQ-16: an explanation submitted before the deadline is shown to the instructor', () => {
  const { a } = twoKeptFlags();
  const requested = requestExplanation(a, T0 + DAY);
  const explained = submitExplanation(requested, 'My cat walked on the keyboard.', T0 + 2 * DAY);
  assert.equal(explained.state, 'explained');
  assert.deepEqual(explained.explanation, { text: 'My cat walked on the keyboard.', submittedAt: T0 + 2 * DAY });
  assert.equal(submitExplanation(requested, 'At the deadline.', T0 + 4 * DAY).state, 'explained');
});

test('FR-016: an explanation after the deadline, empty, or not requested is rejected', () => {
  const { a } = twoKeptFlags();
  const requested = requestExplanation(a, T0 + DAY);
  assert.equal(submitExplanation(requested, 'Too late.', T0 + 4 * DAY + 1).ok, false);
  assert.equal(submitExplanation(requested, '   ', T0 + 2 * DAY).ok, false);
  assert.equal(submitExplanation(a, 'Not asked.', T0 + 2 * DAY).ok, false);
});
