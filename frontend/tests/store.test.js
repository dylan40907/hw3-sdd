import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createStore, STORAGE_KEY } from '../js/rules/store.js';
import { saveAnswer } from '../js/rules/versions.js';
import { newSession } from '../js/rules/start-page.js';
import { exam, seed, students } from '../js/data/mock-data.js';
import { fakeStorage, T0 } from './helpers.js';

test('FR-004 FR-022: load on empty storage returns a state built from the seed', () => {
  const state = createStore(fakeStorage(), seed).load();
  for (const key of ['role', 'currentStudentId', 'sessions', 'signals', 'flags', 'groups', 'referrals']) {
    assert.ok(key in state, `missing ${key}`);
  }
  assert.deepEqual(state.flags, seed.flags);
});

test('FR-004 FR-022: saved state loads back from a new store on the same storage (reload)', () => {
  const storage = fakeStorage();
  const state = createStore(storage, seed).load();
  state.role = 'instructor';
  createStore(storage, seed).save(state);
  assert.deepEqual(createStore(storage, seed).load(), state);
});

test('FR-004 REQ-04: a typed answer is still there after the page reloads', () => {
  const storage = fakeStorage();
  const state = createStore(storage, seed).load();
  state.sessions.s1 = saveAnswer(newSession(exam, students[0]), 'q1', '42', T0);
  createStore(storage, seed).save(state);
  const reloaded = createStore(storage, seed).load();
  assert.equal(reloaded.sessions.s1.answers.q1.value, '42');
});

test('FR-004: loading from the seed does not share objects with the seed', () => {
  const state = createStore(fakeStorage(), seed).load();
  state.flags[0].state = 'changed';
  assert.notEqual(seed.flags[0].state, 'changed');
});

test('FR-004: state is stored under the V2 key and not the V1 key', () => {
  const storage = fakeStorage();
  const store = createStore(storage, seed);
  store.save(store.load());
  assert.equal(STORAGE_KEY, 'fairExam.v2');
  assert.notEqual(storage.getItem('fairExam.v2'), null);
  assert.equal(storage.getItem('fairExam.v1'), null);
});
