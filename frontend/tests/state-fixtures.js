import { exam, seed, students } from '../js/data/mock-data.js';
import { newSession } from '../js/rules/start-page.js';
import { T0 } from './helpers.js';

export function freshState() {
  return JSON.parse(JSON.stringify(seed));
}

export function startedSession(studentId = 's1', at = T0, overrides = {}) {
  const student = students.find((s) => s.id === studentId);
  return { ...newSession(exam, student), confirmedAt: at, startedAt: at, ...overrides };
}

// A state where the given students have started their exams at T0.
export function stateWith(sessions) {
  const state = freshState();
  for (const [id, session] of Object.entries(sessions)) state.sessions[id] = session;
  return state;
}

export function signalsOf(state, studentId, type) {
  return state.signals.filter((s) => s.studentId === studentId && (!type || s.type === type));
}
