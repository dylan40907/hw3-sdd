// FNV-1a 32-bit hash, so versions are repeatable for the same student and question.
function hash(text) {
  let h = 0x811c9dc5;
  for (let i = 0; i < text.length; i += 1) {
    h ^= text.charCodeAt(i);
    h = Math.imul(h, 0x01000193) >>> 0;
  }
  return h;
}

export function versionFor(studentId, question) {
  const params = {};
  for (const key of Object.keys(question.params).sort()) {
    const values = question.params[key];
    params[key] = values[hash(`${studentId}|${question.id}|${key}`) % values.length];
  }
  return params;
}

export function openQuestion(session, question, now) {
  if (session.versions[question.id]) return session;
  return {
    ...session,
    versions: { ...session.versions, [question.id]: { params: versionFor(session.studentId, question), assignedAt: now } },
  };
}

export function correctAnswer(question, params) {
  return question.answer(params);
}

export function saveAnswer(session, questionId, value, now) {
  const previous = session.answers[questionId] || {};
  return {
    ...session,
    answers: {
      ...session.answers,
      [questionId]: { value, savedAt: now, submittedAt: previous.submittedAt ?? null },
    },
  };
}
