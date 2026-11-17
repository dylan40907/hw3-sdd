// Asks for fullscreen. A refusal does not stop the exam (C1: fullscreen only, nothing is locked).
export function requestFullscreen(examEl) {
  try {
    const result = examEl.requestFullscreen?.();
    if (result && typeof result.catch === 'function') result.catch(() => {});
  } catch {
    // Fullscreen is not available; the exam continues.
  }
}

// Emits { type: 'leave' | 'return' | 'fullscreen_exit' | 'paste' | 'offline' | 'online' }.
// Returns a function that removes every listener.
export function attachExamEvents({ doc, win, onEvent }) {
  let away = false;
  const leave = () => {
    if (!away) {
      away = true;
      onEvent({ type: 'leave' });
    }
  };
  const back = () => {
    if (away) {
      away = false;
      onEvent({ type: 'return' });
    }
  };

  const listeners = [
    [doc, 'visibilitychange', () => (doc.visibilityState === 'hidden' ? leave() : back())],
    [win, 'blur', leave],
    [win, 'focus', back],
    [doc, 'fullscreenchange', () => {
      if (!doc.fullscreenElement) onEvent({ type: 'fullscreen_exit' });
    }],
    [doc, 'paste', (event) => {
      const questionId = event.target?.dataset?.questionId;
      if (questionId) onEvent({ type: 'paste', questionId });
    }],
    [win, 'offline', () => onEvent({ type: 'offline' })],
    [win, 'online', () => onEvent({ type: 'online' })],
  ];

  for (const [target, type, fn] of listeners) target.addEventListener(type, fn);
  return () => {
    for (const [target, type, fn] of listeners) target.removeEventListener(type, fn);
  };
}
