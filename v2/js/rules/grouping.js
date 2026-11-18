import { correctAnswer } from './versions.js';
import { isEnded, endTime } from './timer.js';
import { addSignal } from './signals.js';

export const MIN_GROUP_SIZE = 2;

// answersByStudent: { studentId: { questionId: { params, value } } }
export function findGroups(exam, answersByStudent) {
  const groups = [];
  for (const question of exam.questions) {
    const byValue = new Map();
    for (const [studentId, answers] of Object.entries(answersByStudent)) {
      const answer = answers[question.id];
      if (!answer || !answer.params) continue;
      const text = String(answer.value ?? '').trim();
      if (text === '') continue;
      const value = Number(text);
      if (!Number.isFinite(value) || value === correctAnswer(question, answer.params)) continue;
      if (!byValue.has(value)) byValue.set(value, []);
      byValue.get(value).push(studentId);
    }
    for (const [value, studentIds] of byValue) {
      if (studentIds.length >= MIN_GROUP_SIZE) {
        groups.push({ id: `${question.id}:${value}`, questionId: question.id, value, studentIds: [...studentIds].sort() });
      }
    }
  }
  return groups;
}

export function applyGroups(state, groups, now) {
  let next = state;
  for (const group of groups) {
    const existing = next.groups.find((g) => g.id === group.id);
    if (!existing || JSON.stringify(existing) !== JSON.stringify(group)) {
      next = { ...next, groups: [...next.groups.filter((g) => g.id !== group.id), group] };
    }
    for (const studentId of group.studentIds) {
      const has = next.signals.some(
        (s) => s.studentId === studentId && s.type === 'same_incorrect_answer' && s.details.groupId === group.id,
      );
      if (!has) {
        next = addSignal(next, {
          studentId,
          type: 'same_incorrect_answer',
          at: now,
          details: { questionId: group.questionId, groupId: group.id, value: group.value },
        });
      }
    }
  }
  return next;
}

export function processExamEnd(state, exam, students, now) {
  let sessions = state.sessions;
  for (const [id, session] of Object.entries(state.sessions)) {
    if (session.startedAt !== null && session.endedAt === null && isEnded(session, now)) {
      sessions = { ...sessions, [id]: { ...session, endedAt: endTime(session, now) } };
    }
  }
  const next = sessions === state.sessions ? state : { ...state, sessions };

  const answersByStudent = {};
  for (const [id, session] of Object.entries(next.sessions)) {
    if (session.endedAt === null) continue;
    answersByStudent[id] = {};
    for (const question of exam.questions) {
      answersByStudent[id][question.id] = {
        params: session.versions[question.id]?.params,
        value: session.answers[question.id]?.value,
      };
    }
  }
  if (Object.keys(answersByStudent).length === 0) return next;
  for (const student of students) {
    if (!student.prefilledAnswers) continue;
    answersByStudent[student.id] = {};
    for (const [questionId, answer] of Object.entries(student.prefilledAnswers)) {
      answersByStudent[student.id][questionId] = { params: answer.version, value: answer.value };
    }
  }
  return applyGroups(next, findGroups(exam, answersByStudent), now);
}
