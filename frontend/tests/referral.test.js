import { test } from 'node:test';
import assert from 'node:assert/strict';
import { refer, referralsForOffice, NO_EXPLANATION } from '../js/rules/referral.js';
import { keep, requestExplanation, submitExplanation, dismiss } from '../js/rules/flags.js';
import { recordSignal, addSignal } from '../js/rules/signals.js';
import { stateWith, startedSession } from './state-fixtures.js';
import { T0, MIN, DAY } from './helpers.js';

// A state with one new flag for s1 (a paste), returned with a helper to set its flag.
function base() {
  const state = recordSignal(stateWith({ s1: startedSession() }), 's1', 'paste', { questionId: 'q2' }, T0 + MIN);
  const flag = state.flags[state.flags.length - 1];
  const set = (fn) => ({ ...state, flags: state.flags.map((f) => (f.id === flag.id ? fn(f) : f)) });
  return { state, flag, set };
}

const requested = (f) => requestExplanation(keep(f), T0 + DAY);
const explained = (f) => submitExplanation(requested(f), 'I pasted my own notes from question 1.', T0 + 2 * DAY);

test('FR-017 REQ-17: an explained flag can be referred', () => {
  const { flag, set } = base();
  const next = refer(set(explained), flag.id, 'The pasted text matches a website.', T0 + 3 * DAY);
  const referred = next.flags.find((f) => f.id === flag.id);
  assert.equal(referred.state, 'referred');
  assert.equal(next.referrals.length, 1);
  assert.equal(referred.referralId, next.referrals[0].id);
});

test('FR-017 FR-023: a flag can be referred after the deadline passes without an explanation', () => {
  const { flag, set } = base();
  const next = refer(set(requested), flag.id, 'No response.', T0 + 4 * DAY + 1);
  assert.equal(next.flags.find((f) => f.id === flag.id).state, 'referred');
});

test('FR-017: referral is refused when it is not allowed', () => {
  const { flag, set } = base();
  const reason = 'Reason';
  assert.equal(refer(set(keep), flag.id, reason, T0 + 5 * DAY).ok, false, 'kept, never asked');
  assert.equal(refer(set(requested), flag.id, reason, T0 + 2 * DAY).ok, false, 'before the deadline');
  assert.equal(refer(set((f) => dismiss(explained(f))), flag.id, reason, T0 + 5 * DAY).ok, false, 'dismissed');
  assert.equal(refer(set(explained), flag.id, '  ', T0 + 3 * DAY).ok, false, 'empty reason');
  const once = refer(set(explained), flag.id, reason, T0 + 3 * DAY);
  assert.equal(refer(once, flag.id, reason, T0 + 3 * DAY).ok, false, 'already referred');
});

test('FR-018 REQ-18: the referral document has the flag, evidence, explanation and reason', () => {
  const { flag, set } = base();
  const doc = refer(set(explained), flag.id, 'The pasted text matches a website.', T0 + 3 * DAY).referrals[0];
  assert.equal(doc.flagId, flag.id);
  assert.equal(doc.studentId, 's1');
  assert.equal(doc.createdAt, T0 + 3 * DAY);
  assert.equal(doc.flag.signals.length, 1);
  assert.match(doc.flag.signals[0].what, /Pasted into the answer for question 2/);
  assert.equal(doc.flag.signals[0].when, T0 + MIN);
  assert.ok(doc.flag.signals[0].why.length > 0);
  assert.equal(doc.flag.context.extraTimePct, 50);
  assert.equal(doc.evidence.signals[0].type, 'paste');
  assert.equal(doc.evidence.signals[0].details.questionId, 'q2');
  assert.deepEqual(doc.evidence.groups, []);
  assert.equal(doc.explanation, 'I pasted my own notes from question 1.');
  assert.equal(doc.reason, 'The pasted text matches a website.');
});

test('FR-023: with no explanation the document says none was given', () => {
  const { flag, set } = base();
  const doc = refer(set(requested), flag.id, 'No response.', T0 + 5 * DAY).referrals[0];
  assert.equal(doc.explanation, NO_EXPLANATION);
  assert.equal(NO_EXPLANATION, 'No explanation was given before the deadline.');
});

test('FR-019 REQ-19: the integrity office can read the document but not edit it', () => {
  const { flag, set } = base();
  const state = refer(set(explained), flag.id, 'Reason', T0 + 3 * DAY);
  const [doc] = referralsForOffice(state);
  assert.equal(doc.reason, 'Reason');
  assert.ok(Object.isFrozen(doc));
  assert.ok(Object.isFrozen(doc.flag.context));
  assert.ok(Object.isFrozen(doc.evidence.signals[0].details));
  assert.throws(() => { doc.reason = 'changed'; }, TypeError);
  assert.equal(referralsForOffice(state)[0].reason, 'Reason');
});

test('FR-018 FR-019: later flag changes do not change the document', () => {
  const { flag, set } = base();
  const state = refer(set(explained), flag.id, 'Reason', T0 + 3 * DAY);
  const changed = {
    ...state,
    flags: state.flags.map((f) => (f.id === flag.id ? { ...f, explanation: { text: 'edited', submittedAt: 0 } } : f)),
  };
  assert.equal(referralsForOffice(changed)[0].explanation, 'I pasted my own notes from question 1.');
});

// s1 with two signals (a paste and a fullscreen exit) in one flag.
function twoSignalBase() {
  let state = recordSignal(stateWith({ s1: startedSession() }), 's1', 'paste', { questionId: 'q2' }, T0 + MIN);
  state = recordSignal(state, 's1', 'fullscreen_exit', {}, T0 + 2 * MIN);
  const flag = state.flags.find((f) => f.studentId === 's1');
  const set = (fn) => ({ ...state, flags: state.flags.map((f) => (f.id === flag.id ? fn(f) : f)) });
  return { state, flag, set };
}

test('FR-018 FR-012: the referral document lists every signal of the flag, the explanation and the reason', () => {
  const { flag, set } = twoSignalBase();
  const doc = refer(set(explained), flag.id, 'Pasted text matches a site.', T0 + 3 * DAY).referrals[0];
  assert.equal(doc.flag.signals.length, 2);
  assert.equal(doc.evidence.signals.length, 2);
  assert.deepEqual(doc.evidence.signals.map((s) => s.type), ['paste', 'fullscreen_exit']);
  assert.equal(doc.explanation, 'I pasted my own notes from question 1.');
  assert.equal(doc.reason, 'Pasted text matches a site.');
});

test('FR-017: a flag that was never sent for explanation cannot be referred, even with several signals', () => {
  const { flag, set } = twoSignalBase();
  assert.equal(refer(set(keep), flag.id, 'Reason', T0 + 10 * DAY).ok, false);
  assert.equal(refer(set((f) => f), flag.id, 'Reason', T0 + 10 * DAY).ok, false, 'new flag');
});

test('FR-019 FR-018: the document of a two-signal flag is deeply frozen', () => {
  const { flag, set } = twoSignalBase();
  const [doc] = referralsForOffice(refer(set(explained), flag.id, 'Reason', T0 + 3 * DAY));
  assert.ok(Object.isFrozen(doc.flag.signals));
  assert.ok(Object.isFrozen(doc.evidence.signals[1]));
  assert.throws(() => { doc.evidence.signals.push({}); }, TypeError);
});

test('FR-012 FR-018 FR-019: a signal added after referral marks the flag but does not change the document', () => {
  const { flag, set } = twoSignalBase();
  let state = refer(set(explained), flag.id, 'Reason', T0 + 3 * DAY);
  const before = JSON.stringify(state.referrals);
  // A late signal such as a group signal formed at exam end.
  state = addSignal(state, { studentId: 's1', type: 'same_incorrect_answer', at: T0 + 4 * DAY, details: { questionId: 'q1' } });
  const after = state.flags.find((f) => f.id === flag.id);
  assert.equal(after.state, 'referred');
  assert.equal(after.hasNewSignals, true);
  assert.equal(after.signalIds.length, 3);
  assert.equal(JSON.stringify(state.referrals), before);
});
