import { test } from 'node:test';
import assert from 'node:assert/strict';
import { findGroups, applyGroups, processExamEnd } from '../js/rules/grouping.js';
import { finishExam } from '../js/rules/timer.js';
import { openQuestion, saveAnswer, versionFor } from '../js/rules/versions.js';
import { exam, students, SHARED_INCORRECT_Q2 } from '../js/data/mock-data.js';
import { stateWith, startedSession, signalsOf } from './state-fixtures.js';
import { T0, MIN } from './helpers.js';

const q2 = exam.questions[1];

function answers(map) {
  // map: { studentId: { params, value } } for q2
  const out = {};
  for (const [id, a] of Object.entries(map)) out[id] = { q2: a };
  return out;
}

function liveSessionAnswering(studentId, value, at = T0) {
  let session = startedSession(studentId, at);
  for (const q of exam.questions) session = openQuestion(session, q, at);
  return saveAnswer(session, 'q2', String(value), at + MIN);
}

test('FR-009 REQ-09: three students with the same incorrect answer form one group', () => {
  const groups = findGroups(exam, answers({
    x: { params: { a: 6, b: 7 }, value: 50 },
    y: { params: { a: 9, b: 4 }, value: 50 },
    z: { params: { a: 8, b: 5 }, value: '50' },
  }));
  assert.equal(groups.length, 1);
  assert.equal(groups[0].id, 'q2:50');
  assert.equal(groups[0].questionId, 'q2');
  assert.equal(groups[0].value, 50);
  assert.deepEqual(groups[0].studentIds, ['x', 'y', 'z']);
});

test('FR-009 REQ-09: two students with the same incorrect answer form a group', () => {
  const groups = findGroups(exam, answers({
    x: { params: { a: 6, b: 7 }, value: 50 },
    y: { params: { a: 9, b: 4 }, value: 50 },
  }));
  assert.equal(groups.length, 1);
  assert.deepEqual(groups[0].studentIds, ['x', 'y']);
});

test('FR-009: a student with an incorrect answer nobody else gave is in no group', () => {
  const groups = findGroups(exam, answers({
    x: { params: { a: 6, b: 7 }, value: 50 },
    y: { params: { a: 9, b: 4 }, value: 51 },
    z: { params: { a: 8, b: 5 }, value: 52 },
  }));
  assert.equal(groups.length, 0);
});

test('FR-009: a student whose answer is correct for their own version is not in the group', () => {
  const groups = findGroups(exam, answers({
    x: { params: { a: 6, b: 7 }, value: 48 },
    y: { params: { a: 9, b: 4 }, value: 48 },
    z: { params: { a: 6, b: 8 }, value: 48 }, // 6 * 8 = 48 is correct for z
  }));
  assert.equal(groups.length, 1);
  assert.deepEqual(groups[0].studentIds, ['x', 'y']);
});

test('FR-009: applyGroups gives every student in the group one signal, including pre-filled students', () => {
  const group = { id: 'q2:50', questionId: 'q2', value: 50, studentIds: ['s1', 's3', 's4'] };
  const state = applyGroups(stateWith({}), [group], T0);
  assert.deepEqual(state.groups, [group]);
  for (const id of ['s1', 's3', 's4']) {
    const sigs = signalsOf(state, id, 'same_incorrect_answer');
    assert.equal(sigs.length, 1, id);
    assert.equal(sigs[0].details.groupId, 'q2:50');
  }
});

test('FR-009: Finish exam then processExamEnd groups the live student with the two pre-filled students', () => {
  const s1 = finishExam(liveSessionAnswering('s1', SHARED_INCORRECT_Q2), T0 + 5 * MIN);
  const state = processExamEnd(stateWith({ s1 }), exam, students, T0 + 5 * MIN);
  assert.equal(state.groups.length, 1);
  assert.deepEqual(state.groups[0].studentIds, ['s1', 's3', 's4']);
  for (const id of ['s1', 's3', 's4']) assert.equal(signalsOf(state, id, 'same_incorrect_answer').length, 1);
  assert.equal(signalsOf(state, 's5', 'same_incorrect_answer').length, 0);
});

test('FR-009: the two pre-filled students form a group even when the live student answers differently', () => {
  const s1 = finishExam(liveSessionAnswering('s1', 51), T0 + 5 * MIN);
  const state = processExamEnd(stateWith({ s1 }), exam, students, T0 + 5 * MIN);
  assert.deepEqual(state.groups[0].studentIds, ['s3', 's4']);
  assert.equal(signalsOf(state, 's1', 'same_incorrect_answer').length, 0);
});

test('FR-009: the exam ends at the end time even with no student action', () => {
  const s1 = liveSessionAnswering('s1', SHARED_INCORRECT_Q2);
  const before = processExamEnd(stateWith({ s1 }), exam, students, T0 + 89 * MIN);
  assert.equal(before.sessions.s1.endedAt, null);
  assert.equal(before.groups.length, 0);
  const after = processExamEnd(stateWith({ s1 }), exam, students, T0 + 91 * MIN);
  assert.equal(after.sessions.s1.endedAt, T0 + 90 * MIN);
  assert.equal(after.groups.length, 1);
});

test('FR-009: running processExamEnd again, or after a reload, adds no more group signals', () => {
  const s1 = finishExam(liveSessionAnswering('s1', SHARED_INCORRECT_Q2), T0 + 5 * MIN);
  const once = processExamEnd(stateWith({ s1 }), exam, students, T0 + 5 * MIN);
  const twice = processExamEnd(once, exam, students, T0 + 6 * MIN);
  assert.deepEqual(twice, once);
  const reloaded = JSON.parse(JSON.stringify(once));
  assert.deepEqual(processExamEnd(reloaded, exam, students, T0 + 7 * MIN), once);
});

test('FR-009: a second live student with the same answer grows the group and gets the only new signal', () => {
  const s1 = finishExam(liveSessionAnswering('s1', SHARED_INCORRECT_Q2), T0 + 5 * MIN);
  let state = processExamEnd(stateWith({ s1 }), exam, students, T0 + 5 * MIN);
  const before = state.signals.length;
  state = {
    ...state,
    sessions: { ...state.sessions, s2: finishExam(liveSessionAnswering('s2', SHARED_INCORRECT_Q2), T0 + 8 * MIN) },
  };
  state = processExamEnd(state, exam, students, T0 + 8 * MIN);
  assert.deepEqual(state.groups[0].studentIds, ['s1', 's2', 's3', 's4']);
  assert.equal(state.signals.length, before + 1);
  assert.equal(signalsOf(state, 's2', 'same_incorrect_answer').length, 1);
});

test('FR-003 FR-009: the live student is graded against their own recorded version', () => {
  const params = versionFor('s1', q2);
  const correct = String(params.a * params.b);
  const s1 = finishExam(liveSessionAnswering('s1', correct), T0 + 5 * MIN);
  const state = processExamEnd(stateWith({ s1 }), exam, students, T0 + 5 * MIN);
  assert.equal(signalsOf(state, 's1', 'same_incorrect_answer').length, 0);
});
