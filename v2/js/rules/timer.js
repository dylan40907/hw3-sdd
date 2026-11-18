export function baseDurationMs(lengthMinutes, extraTimePct) {
  return lengthMinutes * 60000 * (1 + extraTimePct / 100);
}

export function openPauseOf(session) {
  return session.pauses.find((p) => p.to === null) || null;
}

function closedPauseMs(session) {
  return session.pauses
    .filter((p) => p.to !== null)
    .reduce((sum, p) => sum + (p.to - p.from), 0);
}

export function endTime(session, now) {
  const open = openPauseOf(session);
  return session.startedAt + session.baseDurationMs + closedPauseMs(session) + (open ? now - open.from : 0);
}

export function remainingMs(session, now) {
  return Math.max(0, endTime(session, now) - now);
}

export function isEnded(session, now) {
  if (session.endedAt !== null) return true;
  return session.startedAt !== null && now >= endTime(session, now);
}

export function finishExam(session, now) {
  if (session.endedAt !== null) return session;
  return { ...session, endedAt: now };
}

// The student must pick or type a reason; it is stored on the pause (FR-010, FR-011).
export function openPause(session, now, reason) {
  if (openPauseOf(session)) return { ok: false, error: 'A help request is already open.' };
  const trimmed = String(reason ?? '').trim();
  if (!trimmed) return { ok: false, error: 'Pick or type a reason for the help request.' };
  const pause = { id: `p${session.pauses.length + 1}`, reason: trimmed, from: now, to: null };
  return { ...session, pauses: [...session.pauses, pause] };
}

// The questions are hidden while a help request is open (FR-010).
export function questionsHidden(session) {
  return Boolean(openPauseOf(session));
}

export function closePause(session, now) {
  const open = openPauseOf(session);
  if (!open) return { ok: false, error: 'No help request is open.' };
  // Returning from help does not start the 30-second fast-answer window (FR-008).
  return { ...session, lastReturnAt: null, pauses: session.pauses.map((p) => (p === open ? { ...p, to: now } : p)) };
}

export function pauseLog(session) {
  return session.pauses.map((p) => ({
    reason: p.reason,
    from: p.from,
    to: p.to,
    lengthMs: p.to === null ? null : p.to - p.from,
  }));
}
