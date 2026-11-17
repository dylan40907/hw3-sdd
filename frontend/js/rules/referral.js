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

// flag carries the flag view (what, when, until, why, context) next to the flag fields.
export function buildReferralDocument(flag, signal, reason, now) {
  return deepFreeze(clone({
    id: `ref-${flag.id}`,
    flagId: flag.id,
    studentId: flag.studentId,
    createdAt: now,
    flag: { what: flag.what, when: flag.when, until: flag.until ?? null, why: flag.why, context: flag.context },
    evidence: {
      signal: { type: signal.type, at: signal.at, until: signal.until, details: signal.details },
      technicalEvent: flag.context.technicalEvent ?? null,
      group: flag.context.group ?? null,
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
  const doc = buildReferralDocument({ ...flag, ...view }, view.signal, trimmed, now);
  return {
    ...state,
    flags: state.flags.map((f) => (f.id === flagId ? { ...f, state: 'referred', referralId: doc.id } : f)),
    referrals: [...state.referrals, doc],
  };
}

export function referralsForOffice(state) {
  return state.referrals.map((doc) => deepFreeze(clone(doc)));
}
