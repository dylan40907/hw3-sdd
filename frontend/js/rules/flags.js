import { technicalEvent } from './signals.js';
import { pauseLog } from './timer.js';

export const FLAG_STATES = ['new', 'kept', 'dismissed', 'explanation_requested', 'explained', 'referred'];

function reject(error) {
  return { ok: false, error };
}

function questionNumber(questionId) {
  return questionId ? questionId.replace(/^q/, '') : '?';
}

function seconds(ms) {
  return Math.round(ms / 1000);
}

export function createFlag(signal, state) {
  return {
    id: `flag-${state.flags.length + 1}`,
    signalId: signal.id,
    studentId: signal.studentId,
    state: 'new',
    createdAt: signal.at,
    explanationRequestedAt: null,
    deadline: null,
    explanation: null,
    referralId: null,
  };
}

function describe(signal, group) {
  const d = signal.details || {};
  switch (signal.type) {
    case 'page_leave':
      if (d.cause === 'reload') {
        return {
          what: 'Reloaded the exam page',
          why: 'The exam page was reloaded while the exam was running. Leaving the exam page is a detected behavior.',
        };
      }
      return {
        what: 'Left the exam page',
        why: `Away from the exam page for ${seconds((signal.until ?? signal.at) - signal.at)} s. Leaving the exam page is a detected behavior.`,
      };
    case 'fullscreen_exit':
      return { what: 'Exited fullscreen', why: 'Fullscreen was exited while the exam was running. Exiting fullscreen is a detected behavior.' };
    case 'paste':
      return {
        what: `Pasted into the answer for question ${questionNumber(d.questionId)}`,
        why: 'Text was pasted into an answer field. Pasting into an answer field is a detected behavior.',
      };
    case 'fast_answer':
      return {
        what: `Submitted question ${questionNumber(d.questionId)} soon after returning`,
        why: `Submitted ${d.secondsSinceReturn} s after returning to the exam page (limit 30 s).`,
      };
    case 'same_incorrect_answer': {
      const others = group ? group.studentIds.length - 1 : 0;
      return {
        what: `Same incorrect answer on question ${questionNumber(d.questionId)}`,
        why: `Answered ${d.value}, which is incorrect for this student's version, as did ${others} other students.`,
      };
    }
    default:
      return { what: signal.type, why: '' };
  }
}

export function flagView(flag, state) {
  const signal = state.signals.find((s) => s.id === flag.signalId);
  const student = state.students.find((s) => s.id === flag.studentId);
  const session = state.sessions[flag.studentId];
  const group = signal.details?.groupId ? state.groups.find((g) => g.id === signal.details.groupId) : null;
  const { what, why } = describe(signal, group);
  return {
    what,
    when: signal.at,
    until: signal.until,
    why,
    signal,
    context: {
      extraTimePct: student?.extraTimePct ?? 0,
      pauses: session ? pauseLog(session) : [],
      technicalEvent: session ? technicalEvent(signal, session) : null,
      group: group
        ? {
          questionId: group.questionId,
          value: group.value,
          otherStudents: group.studentIds
            .filter((id) => id !== flag.studentId)
            .map((id) => state.students.find((s) => s.id === id)?.name ?? id),
        }
        : null,
    },
  };
}

export function keep(flag) {
  if (flag.state !== 'new') return reject('Only a new flag can be kept.');
  return { ...flag, state: 'kept' };
}

export function dismiss(flag) {
  if (!['new', 'kept', 'explanation_requested', 'explained'].includes(flag.state)) {
    return reject(`A ${flag.state.replace('_', ' ')} flag cannot be dismissed.`);
  }
  return { ...flag, state: 'dismissed' };
}

export function canRefer(flag, now) {
  if (flag.state === 'explained') return true;
  return flag.state === 'explanation_requested' && flag.deadline !== null && now > flag.deadline;
}

// Flags the student may see: only after the instructor asked for an explanation.
export function studentFlags(flags, studentId) {
  return flags
    .filter((f) => f.studentId === studentId && f.explanationRequestedAt !== null)
    .map((f) => ({ ...f, dismissed: f.state === 'dismissed' }));
}

export const EXPLANATION_DAYS = 3;
const DAY_MS = 86400000;

export function requestExplanation(flag, now) {
  if (flag.state !== 'kept') return reject('Keep the flag before asking for an explanation.');
  return {
    ...flag,
    state: 'explanation_requested',
    explanationRequestedAt: now,
    deadline: now + EXPLANATION_DAYS * DAY_MS,
  };
}

export function submitExplanation(flag, text, now) {
  if (flag.state !== 'explanation_requested') return reject('No explanation was requested for this flag.');
  if (now > flag.deadline) return reject('The deadline for this explanation has passed.');
  const trimmed = String(text ?? '').trim();
  if (!trimmed) return reject('Write an explanation before submitting.');
  return { ...flag, state: 'explained', explanation: { text: trimmed, submittedAt: now } };
}
