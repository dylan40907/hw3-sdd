import { isEnded, openPauseOf } from './timer.js';
import { createFlag } from './flags.js';

export const SIGNAL_TYPES = ['page_leave', 'fullscreen_exit', 'paste', 'fast_answer', 'same_incorrect_answer'];
const DETECTED = new Set(['page_leave', 'fullscreen_exit', 'paste', 'fast_answer']);
export const FAST_ANSWER_MS = 30000;

export function isRunning(session, now) {
  return Boolean(session) && session.startedAt !== null && !isEnded(session, now);
}

function setSession(state, studentId, session) {
  return { ...state, sessions: { ...state.sessions, [studentId]: session } };
}

// Adds one signal. A student has one flag per exam: the first signal creates it, later ones join it (FR-012).
export function addSignal(state, { studentId, type, at, until = null, details = {} }) {
  const signal = { id: `sig-${state.signals.length + 1}`, studentId, type, at, until, details };
  const withSignal = { ...state, signals: [...state.signals, signal] };
  const existing = state.flags.find((f) => f.studentId === studentId);
  if (!existing) return { ...withSignal, flags: [...state.flags, createFlag(signal, withSignal)] };
  // A flag the instructor has already moved past `new` is marked, so the new signal is noticed (FR-012).
  const hasNewSignals = existing.state !== 'new' ? true : existing.hasNewSignals;
  const flags = state.flags.map((f) => (f === existing ? { ...f, signalIds: [...f.signalIds, signal.id], hasNewSignals } : f));
  return { ...withSignal, flags };
}

export function recordOffline(session, now) {
  const last = session.offlinePeriods[session.offlinePeriods.length - 1];
  if (last && last.to === null) return session;
  return { ...session, offlinePeriods: [...session.offlinePeriods, { from: now, to: null }] };
}

export function recordOnline(session, now) {
  const periods = session.offlinePeriods;
  const last = periods[periods.length - 1];
  if (!last || last.to !== null) return session;
  return { ...session, offlinePeriods: [...periods.slice(0, -1), { ...last, to: now }] };
}

// True when the time range overlaps a time the device was offline (FR-021).
function overlapsOffline(session, from, to) {
  return session.offlinePeriods.some((p) => p.from <= to && (p.to ?? Infinity) >= from);
}

// "connection lost" when a page leave overlaps a time the device was offline (FR-021).
export function technicalEvent(signal, session) {
  if (signal.type !== 'page_leave') return null;
  return overlapsOffline(session, signal.at, signal.until ?? signal.at) ? 'connection lost' : null;
}

export function recordSignal(state, studentId, type, details, now) {
  const session = state.sessions[studentId];
  if (DETECTED.has(type) && (!isRunning(session, now) || openPauseOf(session))) return state;
  return addSignal(state, { studentId, type, at: now, details });
}

export function startLeave(session, now) {
  if (session.leave && session.leave.to === null) return session;
  return { ...session, leave: { from: now, to: null, duringPause: Boolean(openPauseOf(session)) } };
}

export function endLeave(state, studentId, now) {
  const session = state.sessions[studentId];
  const leave = session?.leave;
  if (!leave || leave.to !== null) return state;
  const connectionLoss = overlapsOffline(session, leave.from, now);
  const closed = { ...session, leave: { ...leave, to: now, connectionLoss } };
  if (leave.duringPause || openPauseOf(session) || !isRunning(session, now)) {
    return setSession(state, studentId, closed);
  }
  // A return from a connection loss does not start the 30-second fast-answer window (FR-008).
  const next = setSession(state, studentId, connectionLoss ? closed : { ...closed, lastReturnAt: now });
  return addSignal(next, { studentId, type: 'page_leave', at: leave.from, until: now });
}

export function submitAnswer(state, studentId, questionId, now) {
  const session = state.sessions[studentId];
  if (!isRunning(session, now)) return state;
  const previous = session.answers[questionId] || { value: '', savedAt: null };
  const next = setSession(state, studentId, {
    ...session,
    answers: { ...session.answers, [questionId]: { ...previous, submittedAt: now } },
  });
  const since = session.lastReturnAt === null ? null : now - session.lastReturnAt;
  if (openPauseOf(session) || since === null || since > FAST_ANSWER_MS) return next;
  return addSignal(next, {
    studentId,
    type: 'fast_answer',
    at: now,
    details: { questionId, secondsSinceReturn: Math.round(since / 1000) },
  });
}

export function recordReload(state, studentId, now) {
  const session = state.sessions[studentId];
  if (!isRunning(session, now)) return state;
  const open = session.leave && session.leave.to === null ? session.leave : null;
  const from = open ? open.from : now;
  const connectionLoss = overlapsOffline(session, from, now);
  const closed = { ...session, leave: { from, to: now, duringPause: open ? open.duringPause : false, connectionLoss } };
  if (open?.duringPause || openPauseOf(session)) return setSession(state, studentId, closed);
  const next = setSession(state, studentId, connectionLoss ? closed : { ...closed, lastReturnAt: now });
  return addSignal(next, { studentId, type: 'page_leave', at: from, until: now, details: { cause: 'reload' } });
}
