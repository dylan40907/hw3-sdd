export const MIN = 60000;
export const DAY = 86400000;
export const T0 = Date.UTC(2026, 10, 16, 9, 0);

export function fakeStorage() {
  const map = new Map();
  return {
    getItem: (key) => (map.has(key) ? map.get(key) : null),
    setItem: (key, value) => map.set(key, String(value)),
    removeItem: (key) => map.delete(key),
  };
}

export function fakeDoc() {
  const doc = new EventTarget();
  doc.visibilityState = 'visible';
  doc.fullscreenElement = null;
  return doc;
}

export function fakeWin() {
  return new EventTarget();
}

export function fakeExamEl({ reject = false } = {}) {
  const el = {
    calls: 0,
    reject,
    requestFullscreen() {
      el.calls += 1;
      return el.reject ? Promise.reject(new Error('denied')) : Promise.resolve();
    },
  };
  return el;
}

export function eventWithTarget(type, target) {
  const event = new Event(type);
  Object.defineProperty(event, 'target', { value: target });
  return event;
}
