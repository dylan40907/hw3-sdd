import { test } from 'node:test';
import assert from 'node:assert/strict';
import { requestFullscreen, attachExamEvents } from '../js/ui/exam-events.js';
import { fakeDoc, fakeWin, fakeExamEl, eventWithTarget } from './helpers.js';

function setup() {
  const doc = fakeDoc();
  const win = fakeWin();
  const events = [];
  const detach = attachExamEvents({ doc, win, onEvent: (e) => events.push(e) });
  return { doc, win, events, detach };
}

test('FR-005 REQ-05: starting the exam requests fullscreen', () => {
  const el = fakeExamEl();
  requestFullscreen(el);
  assert.equal(el.calls, 1);
});

test('FR-005: a refused fullscreen request does not stop the exam', async () => {
  const el = fakeExamEl({ reject: true });
  assert.doesNotThrow(() => requestFullscreen(el));
  await new Promise((r) => setTimeout(r, 0)); // no unhandled rejection
  assert.equal(el.calls, 1);
  assert.doesNotThrow(() => requestFullscreen({}));
});

test('FR-006: hidden plus blur emit one leave, and visible emits one return', () => {
  const { doc, win, events } = setup();
  doc.visibilityState = 'hidden';
  doc.dispatchEvent(new Event('visibilitychange'));
  win.dispatchEvent(new Event('blur'));
  doc.visibilityState = 'visible';
  doc.dispatchEvent(new Event('visibilitychange'));
  win.dispatchEvent(new Event('focus'));
  assert.deepEqual(events.map((e) => e.type), ['leave', 'return']);
});

test('FR-006: switching to another window (blur only) emits leave and return', () => {
  const { win, events } = setup();
  win.dispatchEvent(new Event('blur'));
  win.dispatchEvent(new Event('focus'));
  assert.deepEqual(events.map((e) => e.type), ['leave', 'return']);
});

test('FR-006: exiting fullscreen emits fullscreen_exit', () => {
  const { doc, events } = setup();
  doc.fullscreenElement = {};
  doc.dispatchEvent(new Event('fullscreenchange'));
  doc.fullscreenElement = null;
  doc.dispatchEvent(new Event('fullscreenchange'));
  assert.deepEqual(events, [{ type: 'fullscreen_exit' }]);
});

test('FR-007: pasting into an answer field emits paste with the question', () => {
  const { doc, events } = setup();
  doc.dispatchEvent(eventWithTarget('paste', { dataset: { questionId: 'q2' } }));
  doc.dispatchEvent(eventWithTarget('paste', { dataset: {} }));
  assert.deepEqual(events, [{ type: 'paste', questionId: 'q2' }]);
});

test('FR-006 FR-007: detaching removes all listeners', () => {
  const { doc, win, events, detach } = setup();
  detach();
  win.dispatchEvent(new Event('blur'));
  doc.dispatchEvent(eventWithTarget('paste', { dataset: { questionId: 'q1' } }));
  doc.dispatchEvent(new Event('fullscreenchange'));
  assert.deepEqual(events, []);
});

test('FR-021: going offline and back online emits offline and online', () => {
  const { win, events } = setup();
  win.dispatchEvent(new Event('offline'));
  win.dispatchEvent(new Event('online'));
  assert.deepEqual(events, [{ type: 'offline' }, { type: 'online' }]);
});
