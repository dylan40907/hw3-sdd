import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  flagView, keep, dismiss, canRefer, studentFlags, requestExplanation, submitExplanation, markFlagSeen,
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

test('FR-012: two signals for one student give one flag holding both signal IDs in order', () => {
  const state = stateWithAllTypes();
  const flags = state.flags.filter((f) => f.studentId === 's1');
  assert.equal(flags.length, 1);
  const s1Signals = state.signals.filter((s) => s.studentId === 's1').map((s) => s.id);
  assert.ok(s1Signals.length >= 2);
  assert.deepEqual(flags[0].signalIds, s1Signals);
  assert.equal('signalId' in flags[0], false);
});

test('FR-012: signals for two different students give two flags', () => {
  let state = stateWith({ s1: startedSession('s1'), s2: startedSession('s2') });
  state = recordSignal(state, 's1', 'paste', { questionId: 'q1' }, T0 + MIN);
  state = recordSignal(state, 's2', 'paste', { questionId: 'q1' }, T0 + MIN);
  const flags = newFlagsOf(state);
  assert.equal(flags.length, 2);
  assert.deepEqual(flags.map((f) => f.studentId).sort(), ['s1', 's2']);
});

test('FR-012: the first signal creates a new flag with hasNewSignals false', () => {
  let state = stateWith({ s1: startedSession('s1') });
  state = recordSignal(state, 's1', 'paste', { questionId: 'q1' }, T0 + MIN);
  const [flag] = newFlagsOf(state);
  assert.equal(flag.state, 'new');
  assert.equal(flag.hasNewSignals, false);
  assert.equal(flag.signalIds.length, 1);
});

test('FR-012 REQ-12: a flag shows what happened, when, why for each signal and one context', () => {
  const state = stateWithAllTypes();
  const [flag] = newFlagsOf(state);
  const view = flagView(flag, state);
  assert.deepEqual(Object.keys(view).sort(), ['context', 'signals']);
  const types = new Set();
  for (const item of view.signals) {
    assert.ok(item.what.length > 0);
    assert.ok(item.why.length > 0);
    assert.equal(typeof item.when, 'number');
    assert.ok('technicalEvent' in item);
    types.add(item.signal.type);
  }
  assert.equal(types.size, 5);
  assert.equal(view.context.extraTimePct, 50);
  assert.deepEqual(view.context.pauses, [{ reason: 'help request', from: T0 + 5 * MIN, to: T0 + 7 * MIN, lengthMs: 2 * MIN }]);
});

test('FR-012 FR-008: the fast-answer signal says how soon after returning it was', () => {
  const state = stateWithAllTypes();
  const view = flagView(newFlagsOf(state)[0], state);
  const fast = view.signals.find((i) => i.signal.type === 'fast_answer');
  assert.match(fast.why, /12 s after returning to the exam page \(limit 30 s\)/);
});

test('FR-012 FR-009: a group signal lists the shared answer and the other students', () => {
  const state = stateWithAllTypes();
  const flag = state.flags.find((f) => f.studentId === 's3');
  const view = flagView(flag, state);
  const [group] = view.context.groups;
  assert.equal(group.value, 50);
  assert.deepEqual(group.otherStudents, ['Student A', 'Student D']);
});

test('FR-009 FR-012 REQ-09: each of the three students has one flag that shows the group as a signal', () => {
  let state = stateWith({ s1: startedSession() });
  state = recordSignal(state, 's1', 'paste', { questionId: 'q1' }, T0 + MIN);
  state = applyGroups(state, [{ id: 'q2:50', questionId: 'q2', value: 50, studentIds: ['s1', 's3', 's4'] }], T0 + 20 * MIN);
  for (const id of ['s1', 's3', 's4']) {
    const flags = state.flags.filter((f) => f.studentId === id);
    assert.equal(flags.length, 1, id);
    const view = flagView(flags[0], state);
    assert.ok(view.signals.some((i) => i.signal.type === 'same_incorrect_answer'), id);
    assert.equal(view.context.groups.length, 1);
    assert.equal(view.context.groups[0].otherStudents.length, 2);
  }
  assert.equal(flagView(state.flags.find((f) => f.studentId === 's1'), state).signals.length, 2);
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

// One student, one kept flag holding two signals.
function oneKeptFlag() {
  let state = stateWith({ s1: startedSession() });
  state = recordSignal(state, 's1', 'paste', { questionId: 'q1' }, T0 + MIN);
  state = recordSignal(state, 's1', 'fullscreen_exit', {}, T0 + 2 * MIN);
  const [flag] = newFlagsOf(state);
  return { state, a: keep(flag) };
}

test('FR-015: an explanation can be requested only on a kept flag, with a 3-day deadline', () => {
  const { a } = oneKeptFlag();
  const requested = requestExplanation(a, T0 + DAY);
  assert.equal(requested.state, 'explanation_requested');
  assert.equal(requested.explanationRequestedAt, T0 + DAY);
  assert.equal(requested.deadline, T0 + 4 * DAY);
  assert.equal(requestExplanation(requested, T0 + DAY).ok, false);
  assert.equal(requestExplanation({ ...a, state: 'new' }, T0).ok, false);
});

test('FR-015 REQ-15: the student sees the flag only after the request, with its deadline', () => {
  const { a } = oneKeptFlag();
  assert.deepEqual(studentFlags([a], 's1'), []);
  const requested = requestExplanation(a, T0 + DAY);
  const visible = studentFlags([requested], 's1');
  assert.equal(visible.length, 1);
  assert.equal(visible[0].id, a.id);
  assert.equal(visible[0].deadline, T0 + 4 * DAY);
});

test('FR-014: a flag dismissed after an explanation request is still shown, marked as dismissed', () => {
  const { a } = oneKeptFlag();
  const dismissed = dismiss(requestExplanation(a, T0 + DAY));
  const visible = studentFlags([dismissed], 's1');
  assert.equal(visible.length, 1);
  assert.equal(visible[0].dismissed, true);
});

test('FR-016 REQ-16: an explanation submitted before the deadline is shown to the instructor', () => {
  const { a } = oneKeptFlag();
  const requested = requestExplanation(a, T0 + DAY);
  const explained = submitExplanation(requested, 'My cat walked on the keyboard.', T0 + 2 * DAY);
  assert.equal(explained.state, 'explained');
  assert.deepEqual(explained.explanation, { text: 'My cat walked on the keyboard.', submittedAt: T0 + 2 * DAY });
  assert.equal(submitExplanation(requested, 'At the deadline.', T0 + 4 * DAY).state, 'explained');
});

test('FR-016: an explanation after the deadline, empty, or not requested is rejected', () => {
  const { a } = oneKeptFlag();
  const requested = requestExplanation(a, T0 + DAY);
  assert.equal(submitExplanation(requested, 'Too late.', T0 + 4 * DAY + 1).ok, false);
  assert.equal(submitExplanation(requested, '   ', T0 + 2 * DAY).ok, false);
  assert.equal(submitExplanation(a, 'Not asked.', T0 + 2 * DAY).ok, false);
});

// A state where s1 has one flag in the given review state, then gets one more signal.
function withFlagIn(flagState, extra = {}) {
  let state = stateWith({ s1: startedSession() });
  state = recordSignal(state, 's1', 'paste', { questionId: 'q1' }, T0 + MIN);
  state = {
    ...state,
    flags: state.flags.map((f) => (f.studentId === 's1' ? { ...f, state: flagState, ...extra } : f)),
  };
  return recordSignal(state, 's1', 'fullscreen_exit', {}, T0 + 3 * MIN);
}

test('FR-012: a signal added to a flag that is no longer new marks it "has new signals" and changes nothing else', () => {
  const explanation = { text: 'Because.', submittedAt: T0 + 2 * MIN };
  const cases = {
    kept: {},
    dismissed: {},
    explanation_requested: { explanationRequestedAt: T0 + 2 * MIN, deadline: T0 + 3 * DAY },
    explained: { explanationRequestedAt: T0 + 2 * MIN, deadline: T0 + 3 * DAY, explanation },
    referred: { explanationRequestedAt: T0 + 2 * MIN, deadline: T0 + 3 * DAY, explanation, referralId: 'ref-x' },
  };
  for (const [flagState, extra] of Object.entries(cases)) {
    const state = withFlagIn(flagState, extra);
    const flag = state.flags.find((f) => f.studentId === 's1');
    assert.equal(state.flags.filter((f) => f.studentId === 's1').length, 1, flagState);
    assert.equal(flag.signalIds.length, 2, flagState);
    assert.equal(flag.hasNewSignals, true, flagState);
    assert.equal(flag.state, flagState);
    assert.equal(flag.explanation, extra.explanation ?? null, flagState);
    assert.equal(flag.deadline, extra.deadline ?? null, flagState);
  }
});

test('FR-012: a signal added to a new flag does not set "has new signals"', () => {
  const state = withFlagIn('new');
  const flag = state.flags.find((f) => f.studentId === 's1');
  assert.equal(flag.signalIds.length, 2);
  assert.equal(flag.hasNewSignals, false);
});

test('FR-012: markFlagSeen clears "has new signals" and changes nothing else', () => {
  const state = withFlagIn('kept');
  const flag = state.flags.find((f) => f.studentId === 's1');
  const seen = markFlagSeen(state, flag.id);
  const after = seen.flags.find((f) => f.id === flag.id);
  assert.equal(after.hasNewSignals, false);
  assert.deepEqual({ ...after, hasNewSignals: true }, flag);
  assert.equal(markFlagSeen(seen, flag.id), seen);
});

test('FR-013: a student with a two-signal flag sees nothing while it is new or kept', () => {
  const state = withFlagIn('new');
  assert.deepEqual(studentFlags(state.flags, 's1'), []);
  const kept = withFlagIn('kept');
  assert.deepEqual(studentFlags(kept.flags, 's1'), []);
});

test('FR-014 FR-015: a flag dismissed after an explanation request stays visible with all its signals, marked dismissed', () => {
  const state = withFlagIn('dismissed', { explanationRequestedAt: T0 + 2 * MIN, deadline: T0 + 3 * DAY });
  const visible = studentFlags(state.flags, 's1');
  assert.equal(visible.length, 1);
  assert.equal(visible[0].dismissed, true);
  assert.equal(flagView(visible[0], state).signals.length, 2);
});

test('FR-014: a dismissed two-signal flag cannot be referred', () => {
  const state = withFlagIn('explained', { explanationRequestedAt: T0, deadline: T0 + 3 * DAY, explanation: { text: 'x', submittedAt: T0 } });
  const flag = state.flags.find((f) => f.studentId === 's1');
  assert.equal(canRefer(flag, T0 + MIN), true);
  assert.equal(canRefer(dismiss(flag), T0 + 10 * DAY), false);
});

test('FR-015 FR-016 REQ-15 REQ-16: a two-signal flag appears to the student only after the request and takes an explanation before the deadline', () => {
  const { a } = oneKeptFlag();
  assert.equal(a.signalIds.length, 2);
  assert.deepEqual(studentFlags([a], 's1'), []);
  const requested = requestExplanation(a, T0 + DAY);
  const [visible] = studentFlags([requested], 's1');
  assert.equal(visible.deadline, T0 + 4 * DAY);
  const explained = submitExplanation(requested, 'I copied my own notes.', T0 + 2 * DAY);
  assert.equal(explained.explanation.text, 'I copied my own notes.');
  assert.equal(submitExplanation(requested, 'Late.', T0 + 4 * DAY + 1).ok, false);
});
