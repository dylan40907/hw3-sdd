import { canRefer, flagView } from './flags.js';

export const NO_EXPLANATION = 'No explanation was given before the deadline.';

function deepFreeze(value) {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {
    Object.freeze(value);
    for (const key of Object.keys(value)) deepFreeze(value[key]);
  }
  return value;
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

// flag carries the flag view (signals, context) next to the flag fields.
export function buildReferralDocument(flag, reason, now) {
  return deepFreeze(clone({
    id: `ref-${flag.id}`,
    flagId: flag.id,
    studentId: flag.studentId,
    createdAt: now,
    flag: {
      signals: flag.signals.map((i) => ({
        what: i.what, when: i.when, until: i.until ?? null, why: i.why, technicalEvent: i.technicalEvent ?? null,
      })),
      context: flag.context,
    },
    evidence: {
      signals: flag.signals.map((i) => ({
        type: i.signal.type,
        at: i.signal.at,
        until: i.signal.until,
        details: i.signal.details,
        technicalEvent: i.technicalEvent ?? null,
      })),
      groups: flag.context.groups,
    },
    explanation: flag.explanation?.text ?? NO_EXPLANATION,
    reason,
  }));
}

export function refer(state, flagId, reason, now) {
  const flag = state.flags.find((f) => f.id === flagId);
  if (!flag) return { ok: false, error: 'Flag not found.' };
  const trimmed = String(reason ?? '').trim();
  if (!trimmed) return { ok: false, error: 'Write a reason for the referral.' };
  if (!canRefer(flag, now)) {
    return { ok: false, error: 'This flag can be referred only after the student explains or the deadline passes.' };
  }
  const view = flagView(flag, state);
  const doc = buildReferralDocument({ ...flag, ...view }, trimmed, now);
  return {
    ...state,
    flags: state.flags.map((f) => (f.id === flagId ? { ...f, state: 'referred', referralId: doc.id } : f)),
    referrals: [...state.referrals, doc],
  };
}

export function referralsForOffice(state) {
  return state.referrals.map((doc) => deepFreeze(clone(doc)));
}
