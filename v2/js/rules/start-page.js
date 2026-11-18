import { baseDurationMs } from './timer.js';

export function newSession(exam, student) {
  return {
    studentId: student.id,
    confirmedAt: null,
    startedAt: null,
    baseDurationMs: baseDurationMs(exam.lengthMinutes, student.extraTimePct),
    versions: {},
    answers: {},
    pauses: [],
    offlinePeriods: [],
    leave: null,
    lastReturnAt: null,
    endedAt: null,
  };
}

export function startPageSummary(exam, student, now) {
  return {
    rules: exam.rules,
    lengthMinutes: exam.lengthMinutes,
    endTime: now + baseDurationMs(exam.lengthMinutes, student.extraTimePct),
    accommodations: student.extraTimePct > 0 ? [`${student.extraTimePct}% extra time`] : ['None'],
    detected: exam.detected,
  };
}

export function confirm(session, now) {
  return { ...session, confirmedAt: now };
}

export function startExam(session, now) {
  if (session.confirmedAt === null) {
    return { ok: false, error: 'Confirm the start page before the exam can start.' };
  }
  if (session.startedAt !== null) return session;
  return { ...session, startedAt: now };
}
