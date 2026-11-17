import { test } from 'node:test';
import assert from 'node:assert/strict';
import { startPageSummary, newSession, confirm, startExam } from '../js/rules/start-page.js';
import { exam, students } from '../js/data/mock-data.js';
import { MIN, T0 } from './helpers.js';

const studentA = students.find((s) => s.id === 's1');
const studentB = students.find((s) => s.id === 's2');

test('FR-002: start page shows rules, end time, accommodations and detected behaviors', () => {
  const summary = startPageSummary(exam, studentA, T0);
  assert.deepEqual(summary.rules, exam.rules);
  assert.equal(summary.endTime, T0 + 90 * MIN);
  assert.ok(summary.accommodations.some((a) => a.includes('50% extra time')));
  assert.equal(summary.detected.length, 4);
  assert.deepEqual(summary.detected, exam.detected);
});

test('FR-002: a student without accommodations sees "None"', () => {
  const summary = startPageSummary(exam, studentB, T0);
  assert.deepEqual(summary.accommodations, ['None']);
  assert.equal(summary.endTime, T0 + 60 * MIN);
});

test('FR-002 REQ-02: the exam does not start until the start page is confirmed', () => {
  const session = newSession(exam, studentA);
  const result = startExam(session, T0);
  assert.equal(result.ok, false);
  assert.equal(session.startedAt, null);
});

test('FR-002: after confirming, the exam starts', () => {
  const session = startExam(confirm(newSession(exam, studentA), T0), T0);
  assert.equal(session.confirmedAt, T0);
  assert.equal(session.startedAt, T0);
});
