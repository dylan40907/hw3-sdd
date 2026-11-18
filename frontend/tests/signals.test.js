import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  recordSignal, startLeave, endLeave, submitAnswer, recordReload,
  recordOffline, recordOnline, technicalEvent,
} from '../js/rules/signals.js';
import { finishExam, openPause, closePause } from '../js/rules/timer.js';
import { flagView } from '../js/rules/flags.js';
import { saveAnswer } from '../js/rules/versions.js';
import { stateWith, startedSession, signalsOf } from './state-fixtures.js';
import { T0, MIN } from './helpers.js';

function leaveAndReturn(state, from, to) {
  const s1 = startLeave(state.sessions.s1, from);
  return endLeave({ ...state, sessions: { ...state.sessions, s1 } }, 's1', to);
}

test('FR-006 REQ-06: switching to another tab and back records one page-leave signal', () => {
  let state = stateWith({ s1: startedSession() });
  let s1 = startLeave(state.sessions.s1, T0 + MIN);
  s1 = startLeave(s1, T0 + MIN + 500); // blur after visibilitychange in the same leave
  state = endLeave({ ...state, sessions: { s1 } }, 's1', T0 + 2 * MIN);
  const leaves = signalsOf(state, 's1', 'page_leave');
  assert.equal(leaves.length, 1);
  assert.equal(leaves[0].at, T0 + MIN);
  assert.equal(leaves[0].until, T0 + 2 * MIN);
  assert.equal(state.sessions.s1.lastReturnAt, T0 + 2 * MIN);
});

test('FR-006: exiting fullscreen records a signal', () => {
  const state = recordSignal(stateWith({ s1: startedSession() }), 's1', 'fullscreen_exit', {}, T0 + MIN);
  assert.equal(signalsOf(state, 's1', 'fullscreen_exit').length, 1);
});

test('FR-007 REQ-07: pasting into an answer field records a signal with the question', () => {
  const state = recordSignal(stateWith({ s1: startedSession() }), 's1', 'paste', { questionId: 'q1' }, T0 + MIN);
  const pastes = signalsOf(state, 's1', 'paste');
  assert.equal(pastes.length, 1);
  assert.equal(pastes[0].details.questionId, 'q1');
});

test('FR-006 FR-007: nothing is recorded before the exam starts or after it ends', () => {
  const notStarted = stateWith({ s1: { ...startedSession(), startedAt: null } });
  assert.equal(signalsOf(recordSignal(notStarted, 's1', 'paste', {}, T0), 's1').length, 0);
  const ended = stateWith({ s1: finishExam(startedSession(), T0 + MIN) });
  assert.equal(signalsOf(recordSignal(ended, 's1', 'paste', {}, T0 + 2 * MIN), 's1').length, 0);
});

test('FR-008 REQ-08: submitting within 30 seconds of returning records a fast-answer signal', () => {
  const back = T0 + 2 * MIN;
  const state = submitAnswer(leaveAndReturn(stateWith({ s1: startedSession() }), T0 + MIN, back), 's1', 'q1', back + 30000);
  const fast = signalsOf(state, 's1', 'fast_answer');
  assert.equal(fast.length, 1);
  assert.equal(fast[0].details.questionId, 'q1');
  assert.equal(fast[0].details.secondsSinceReturn, 30);
  assert.equal(state.sessions.s1.answers.q1.submittedAt, back + 30000);
});

test('FR-008: submitting after 30 seconds, or without leaving, records no fast-answer signal', () => {
  const back = T0 + 2 * MIN;
  const late = submitAnswer(leaveAndReturn(stateWith({ s1: startedSession() }), T0 + MIN, back), 's1', 'q1', back + 30001);
  assert.equal(signalsOf(late, 's1', 'fast_answer').length, 0);
  const never = submitAnswer(stateWith({ s1: startedSession() }), 's1', 'q1', T0 + MIN);
  assert.equal(signalsOf(never, 's1', 'fast_answer').length, 0);
});

test('FR-022: a reload of a running exam records a page-leave signal marked as a reload', () => {
  const state = recordReload(stateWith({ s1: startedSession() }), 's1', T0 + MIN);
  const leaves = signalsOf(state, 's1', 'page_leave');
  assert.equal(leaves.length, 1);
  assert.equal(leaves[0].details.cause, 'reload');
});

test('FR-022: a reload before the start or after the end records nothing', () => {
  const notStarted = stateWith({ s1: { ...startedSession(), startedAt: null } });
  assert.equal(signalsOf(recordReload(notStarted, 's1', T0), 's1').length, 0);
  const ended = stateWith({ s1: finishExam(startedSession(), T0 + MIN) });
  assert.equal(signalsOf(recordReload(ended, 's1', T0 + 2 * MIN), 's1').length, 0);
});

test('FR-022: a reload after the hidden and blur events records exactly one page-leave signal', () => {
  let state = stateWith({ s1: startedSession() });
  let s1 = startLeave(state.sessions.s1, T0 + MIN);
  s1 = startLeave(s1, T0 + MIN + 10);
  state = recordReload({ ...state, sessions: { s1 } }, 's1', T0 + MIN + 900);
  const leaves = signalsOf(state, 's1', 'page_leave');
  assert.equal(leaves.length, 1);
  assert.equal(leaves[0].details.cause, 'reload');
  assert.equal(leaves[0].at, T0 + MIN);
  assert.equal(leaves[0].until, T0 + MIN + 900);
  assert.equal(state.sessions.s1.leave.to, T0 + MIN + 900);
  assert.equal(state.sessions.s1.lastReturnAt, T0 + MIN + 900);
});

test('FR-021: offline and online times are recorded as offline periods', () => {
  let s1 = recordOffline(startedSession(), T0 + MIN);
  s1 = recordOffline(s1, T0 + MIN + 100); // already offline
  s1 = recordOnline(s1, T0 + 2 * MIN);
  assert.deepEqual(s1.offlinePeriods, [{ from: T0 + MIN, to: T0 + 2 * MIN }]);
});

test('FR-021: a page leave that overlaps an offline period shows "connection lost"', () => {
  const s1 = recordOnline(recordOffline(startedSession(), T0 + MIN), T0 + 3 * MIN);
  const overlapping = { type: 'page_leave', at: T0 + 2 * MIN, until: T0 + 4 * MIN };
  const before = { type: 'page_leave', at: T0, until: T0 + 30000 };
  assert.equal(technicalEvent(overlapping, s1), 'connection lost');
  assert.equal(technicalEvent(before, s1), null);
  assert.equal(technicalEvent({ type: 'paste', at: T0 + 2 * MIN, until: null }, s1), null);
});

test('FR-021: a page leave during a period that is still offline shows "connection lost"', () => {
  const s1 = recordOffline(startedSession(), T0 + MIN);
  assert.equal(technicalEvent({ type: 'page_leave', at: T0 + 2 * MIN, until: T0 + 3 * MIN }, s1), 'connection lost');
});

function withOpenHelp(at) {
  return stateWith({ s1: startedSession('s1', T0, { pauses: [{ id: 'p1', reason: 'help request', from: at, to: null }] }) });
}

test('FR-010 REQ-10: nothing is detected while a help request is open', () => {
  let state = withOpenHelp(T0 + MIN);
  const flagsBefore = state.flags.length;
  state = recordSignal(state, 's1', 'paste', { questionId: 'q1' }, T0 + 2 * MIN);
  state = recordSignal(state, 's1', 'fullscreen_exit', {}, T0 + 2 * MIN);
  const s1 = startLeave(state.sessions.s1, T0 + 2 * MIN);
  state = endLeave({ ...state, sessions: { s1 } }, 's1', T0 + 3 * MIN);
  state = submitAnswer(state, 's1', 'q1', T0 + 3 * MIN + 1000);
  assert.equal(signalsOf(state, 's1').length, 0);
  assert.equal(state.flags.length, flagsBefore);
  assert.equal(state.sessions.s1.lastReturnAt, null);
});

test('FR-010: a page leave that started during help records nothing after help closes', () => {
  let state = withOpenHelp(T0 + MIN);
  let s1 = startLeave(state.sessions.s1, T0 + 2 * MIN);
  s1 = { ...s1, pauses: [{ ...s1.pauses[0], to: T0 + 3 * MIN }] }; // help closed while away
  state = endLeave({ ...state, sessions: { s1 } }, 's1', T0 + 4 * MIN);
  assert.equal(signalsOf(state, 's1').length, 0);
  assert.equal(state.sessions.s1.lastReturnAt, null);
  state = submitAnswer(state, 's1', 'q1', T0 + 4 * MIN + 5000);
  assert.equal(signalsOf(state, 's1', 'fast_answer').length, 0);
});

test('FR-010 FR-021: offline periods are still recorded during help', () => {
  const s1 = recordOffline(withOpenHelp(T0 + MIN).sessions.s1, T0 + 2 * MIN);
  assert.equal(s1.offlinePeriods.length, 1);
});

function flagOf(state, studentId) {
  return state.flags.find((f) => f.studentId === studentId);
}

test('FR-008 FR-021 REQ-08: after a connection loss the page leave is marked and a fast answer is not recorded', () => {
  let s1 = recordOffline(startedSession(), T0 + MIN);
  s1 = startLeave(s1, T0 + MIN + 1000);
  s1 = recordOnline(s1, T0 + 2 * MIN);
  let state = endLeave(stateWith({ s1 }), 's1', T0 + 2 * MIN + 1000);
  assert.equal(signalsOf(state, 's1', 'page_leave').length, 1);
  assert.equal(flagView(flagOf(state, 's1'), state).signals[0].technicalEvent, 'connection lost');
  assert.equal(state.sessions.s1.lastReturnAt, null);
  state = submitAnswer(state, 's1', 'q1', T0 + 2 * MIN + 6000);
  assert.equal(signalsOf(state, 's1', 'fast_answer').length, 0);
});

test('FR-008 FR-021: no fast answer when the student is still offline at the moment of return', () => {
  let s1 = recordOffline(startedSession(), T0 + MIN);
  s1 = startLeave(s1, T0 + MIN + 1000);
  let state = endLeave(stateWith({ s1 }), 's1', T0 + 2 * MIN);
  assert.equal(flagView(flagOf(state, 's1'), state).signals[0].technicalEvent, 'connection lost');
  state = submitAnswer(state, 's1', 'q1', T0 + 2 * MIN + 5000);
  assert.equal(signalsOf(state, 's1', 'fast_answer').length, 0);
});

test('FR-008 FR-006: a normal tab switch still records a fast answer (no connection loss)', () => {
  let state = leaveAndReturn(stateWith({ s1: startedSession() }), T0 + MIN, T0 + 2 * MIN);
  state = submitAnswer(state, 's1', 'q1', T0 + 2 * MIN + 5000);
  assert.equal(signalsOf(state, 's1', 'fast_answer').length, 1);
});

test('FR-008 FR-010 REQ-08: after a help request closes, a fast answer is not recorded', () => {
  let state = leaveAndReturn(stateWith({ s1: startedSession() }), T0 + MIN, T0 + 2 * MIN);
  let s1 = openPause(state.sessions.s1, T0 + 2 * MIN + 5000, 'Technical problem');
  s1 = closePause(s1, T0 + 2 * MIN + 10000);
  state = submitAnswer({ ...state, sessions: { s1 } }, 's1', 'q1', T0 + 2 * MIN + 15000);
  assert.equal(signalsOf(state, 's1', 'fast_answer').length, 0);
});

test('FR-008 FR-004: only Submit can raise the fast-answer signal; saving an answer never does', () => {
  let state = leaveAndReturn(stateWith({ s1: startedSession() }), T0 + MIN, T0 + 2 * MIN);
  const saved = saveAnswer(state.sessions.s1, 'q1', '42', T0 + 2 * MIN + 3000);
  state = { ...state, sessions: { s1: saved } };
  assert.equal(signalsOf(state, 's1', 'fast_answer').length, 0);
  state = submitAnswer(state, 's1', 'q1', T0 + 2 * MIN + 5000);
  assert.equal(signalsOf(state, 's1', 'fast_answer').length, 1);
});

test('FR-022 FR-021 FR-008: a reload during an offline period records one reload page leave and no fast answer', () => {
  let s1 = recordOffline(startedSession(), T0 + MIN);
  s1 = startLeave(s1, T0 + MIN + 1000);
  let state = recordReload(stateWith({ s1 }), 's1', T0 + 2 * MIN);
  const leaves = signalsOf(state, 's1', 'page_leave');
  assert.equal(leaves.length, 1);
  assert.equal(leaves[0].details.cause, 'reload');
  assert.equal(state.sessions.s1.lastReturnAt, null);
  state = submitAnswer(state, 's1', 'q1', T0 + 2 * MIN + 5000);
  assert.equal(signalsOf(state, 's1', 'fast_answer').length, 0);
});
