import { newSession, startPageSummary, confirm, startExam } from '../rules/start-page.js';
import {
  remainingMs, endTime, finishExam, openPause, closePause, openPauseOf,
} from '../rules/timer.js';
import { studentFlags, flagView, submitExplanation } from '../rules/flags.js';
import { saveAnswer, openQuestion } from '../rules/versions.js';
import {
  recordSignal, startLeave, endLeave, submitAnswer, isRunning, recordOffline, recordOnline,
} from '../rules/signals.js';
import { requestFullscreen, attachExamEvents } from './exam-events.js';
import { escapeHtml, formatClock, formatDateTime, formatRemaining } from './format.js';

let detachEvents = null;
let attachedFor = null;

export function stopExamEvents() {
  if (detachEvents) detachEvents();
  detachEvents = null;
  attachedFor = null;
}

function startExamEvents(ctx) {
  const studentId = ctx.state.currentStudentId;
  if (attachedFor === studentId) return;
  stopExamEvents();
  attachedFor = studentId;
  detachEvents = attachExamEvents({
    doc: document,
    win: window,
    onEvent: (event) => {
      const t = ctx.now();
      ctx.update((state) => {
        if (state.currentStudentId !== studentId) return state;
        switch (event.type) {
          case 'leave': return withSession(state, (s) => startLeave(s, t));
          case 'return': return endLeave(state, studentId, t);
          case 'fullscreen_exit': return recordSignal(state, studentId, 'fullscreen_exit', {}, t);
          case 'paste': return recordSignal(state, studentId, 'paste', { questionId: event.questionId }, t);
          case 'offline': return withSession(state, (s) => recordOffline(s, t));
          case 'online': return withSession(state, (s) => recordOnline(s, t));
          default: return state;
        }
      }, { render: false });
    },
  });
}

function currentStudent(state) {
  return state.students.find((s) => s.id === state.currentStudentId);
}

function sessionOf(state) {
  return state.sessions[state.currentStudentId] || null;
}

// Applies fn to the current student's session. Passes through { ok: false } results.
function withSession(state, fn) {
  const id = state.currentStudentId;
  const result = fn(state.sessions[id]);
  if (result && result.ok === false) return result;
  return { ...state, sessions: { ...state.sessions, [id]: result } };
}

function questionText(question, params) {
  if (!params) return question.template;
  return question.template.replace(/\{(\w+)\}/g, (_, key) => params[key]);
}

function renderStartPage(el, ctx) {
  const { state, exam } = ctx;
  const student = currentStudent(state);
  const summary = startPageSummary(exam, student, ctx.now());
  el.innerHTML = `
    <div class="panel">
      <h2>${escapeHtml(exam.title)}</h2>
      <p>${student.name}, read this page before you start.</p>
      <h3>Rules</h3>
      <ul>${summary.rules.map((r) => `<li>${escapeHtml(r)}</li>`).join('')}</ul>
      <h3>Time</h3>
      <p>Exam length: ${summary.lengthMinutes} minutes. If you start now, your exam ends at
        <strong data-start-end>${formatClock(summary.endTime)}</strong>.</p>
      <h3>Your accommodations</h3>
      <ul>${summary.accommodations.map((a) => `<li>${escapeHtml(a)}</li>`).join('')}</ul>
      <h3>What is detected</h3>
      <p>No camera or microphone is used. The exam records:</p>
      <ul>${summary.detected.map((d) => `<li>${escapeHtml(d)}</li>`).join('')}</ul>
      <div class="actions"><button data-action="confirm">I have read this page. Start the exam</button></div>
    </div>`;
  el.querySelector('[data-action="confirm"]').onclick = () => onConfirm(ctx);
}

function onConfirm(ctx) {
  const t = ctx.now();
  ctx.update((state) => {
    const student = currentStudent(state);
    const withNew = state.sessions[student.id]
      ? state
      : { ...state, sessions: { ...state.sessions, [student.id]: newSession(ctx.exam, student) } };
    return withSession(withNew, (s) => {
      const started = startExam(confirm(s, t), t);
      if (started.ok === false) return started;
      return ctx.exam.questions.reduce((acc, q) => openQuestion(acc, q, t), started);
    });
  });
  requestFullscreen(document.documentElement);
}

function renderEnded(el, ctx) {
  const session = sessionOf(ctx.state);
  el.innerHTML = `
    <div class="panel">
      <h2>Exam ended</h2>
      <p>Your exam ended at ${formatClock(session.endedAt)}. Your answers are saved.</p>
    </div>`;
}

function renderExam(el, ctx) {
  const { state, exam } = ctx;
  const session = sessionOf(state);
  const t = ctx.now();
  const open = openPauseOf(session);
  el.innerHTML = `
    <div class="panel">
      <h2>${escapeHtml(exam.title)}</h2>
      <p>Time left: <span class="timer" data-timer>${formatRemaining(remainingMs(session, t))}</span>
        <span class="muted">(ends at <span data-end>${formatClock(endTime(session, t))}</span>)</span></p>
      ${open ? `
      <div class="panel" data-help-panel>
        <h3>Help request open, timer paused</h3>
        <p>Nothing is detected while the help request is open. Close it to go back to the questions.</p>
        <button data-action="close-help">Close help request</button>
      </div>` : `
      <div class="actions"><button class="secondary" data-action="open-help">Request help</button></div>
      <div data-questions>
        ${exam.questions.map((q, i) => {
          const answer = session.answers[q.id];
          return `
          <div class="question">
            <p><strong>Question ${i + 1}.</strong> ${escapeHtml(questionText(q, session.versions[q.id]?.params))}</p>
            <input type="text" inputmode="decimal" data-question-id="${q.id}" value="${escapeHtml(answer?.value ?? '')}" aria-label="Answer to question ${i + 1}">
            <button class="secondary" data-submit="${q.id}">Submit</button>
            <span class="status" data-status="${q.id}">${answer?.submittedAt ? 'Submitted' : answer?.savedAt ? 'Saved' : ''}</span>
          </div>`;
        }).join('')}
      </div>
      <div class="actions"><button data-action="finish">Finish exam</button></div>`}
    </div>`;

  const helpButton = el.querySelector('[data-action="open-help"]') || el.querySelector('[data-action="close-help"]');
  helpButton.onclick = () => {
    const toggle = open ? closePause : openPause;
    ctx.update((st) => withSession(st, (s) => toggle(s, ctx.now())));
  };
  if (open) return;

  for (const button of el.querySelectorAll('[data-submit]')) {
    button.onclick = () => {
      const qid = button.dataset.submit;
      ctx.update((st) => submitAnswer(st, st.currentStudentId, qid, ctx.now()));
    };
  }
  el.querySelector('[data-action="finish"]').onclick = () => {
    if (!window.confirm('Finish the exam now? You cannot change your answers afterwards.')) return;
    ctx.update((st) => withSession(st, (s) => finishExam(s, ctx.now())));
  };

  for (const input of el.querySelectorAll('input[data-question-id]')) {
    input.addEventListener('input', () => {
      const qid = input.dataset.questionId;
      const value = input.value;
      ctx.update((st) => withSession(st, (s) => saveAnswer(s, qid, value, ctx.now())), { render: false });
      el.querySelector(`[data-status="${qid}"]`).textContent = 'Saved';
    });
  }
}

function renderMyFlags(el, ctx) {
  const { state } = ctx;
  const flags = studentFlags(state.flags, state.currentStudentId);
  const t = ctx.now();
  el.innerHTML = `
    <div class="panel">
      <h2>My flags</h2>
      ${flags.length ? flags.map((f) => {
        const v = flagView(f, state);
        const canExplain = f.state === 'explanation_requested' && t <= f.deadline;
        return `
        <div class="question ${f.dismissed ? 'dismissed-flag' : ''}">
          <p><strong class="${f.dismissed ? 'dismissed' : ''}">${escapeHtml(v.what)}</strong>
            <span class="flag-state ${f.dismissed ? 'dismissed' : ''}">${f.dismissed ? 'Dismissed' : f.state === 'explained' ? 'Explanation sent' : f.state === 'referred' ? 'Referred' : 'Explanation requested'}</span></p>
          <dl>
            <dt>When</dt><dd>${formatDateTime(v.when)}</dd>
            <dt>Why</dt><dd>${escapeHtml(v.why)}</dd>
            <dt>Deadline</dt><dd>${formatDateTime(f.deadline)}</dd>
            ${f.explanation ? `<dt>Your explanation</dt><dd>${escapeHtml(f.explanation.text)}</dd>` : ''}
          </dl>
          ${canExplain ? `
          <label>Your explanation<textarea data-explain-text="${f.id}"></textarea></label>
          <div class="actions"><button data-explain="${f.id}">Submit explanation</button></div>` : ''}
        </div>`;
      }).join('') : '<p class="muted">No flags need your explanation.</p>'}
    </div>`;
  for (const button of el.querySelectorAll('[data-explain]')) {
    button.onclick = () => {
      const id = button.dataset.explain;
      const text = el.querySelector(`[data-explain-text="${id}"]`).value;
      ctx.update((st) => {
        const flag = st.flags.find((f) => f.id === id);
        const result = submitExplanation(flag, text, ctx.now());
        if (result.ok === false) return result;
        return { ...st, flags: st.flags.map((f) => (f.id === id ? result : f)) };
      });
    };
  }
}

export function renderStudentView(el, ctx) {
  el.innerHTML = '<div data-main></div><div data-my-flags></div>';
  const main = el.querySelector('[data-main]');
  const session = sessionOf(ctx.state);
  if (!session || session.startedAt === null) {
    stopExamEvents();
    renderStartPage(main, ctx);
  } else if (session.endedAt !== null || !isRunning(session, ctx.now())) {
    stopExamEvents();
    renderEnded(main, ctx);
  } else {
    startExamEvents(ctx);
    renderExam(main, ctx);
  }
  renderMyFlags(el.querySelector('[data-my-flags]'), ctx);
}

export function tickStudentView(el, ctx) {
  const session = sessionOf(ctx.state);
  const t = ctx.now();
  const timerEl = el.querySelector('[data-timer]');
  if (session && session.startedAt !== null && timerEl) {
    timerEl.textContent = formatRemaining(remainingMs(session, t));
    const endEl = el.querySelector('[data-end]');
    if (endEl) endEl.textContent = formatClock(endTime(session, t));
  }
  const startEndEl = el.querySelector('[data-start-end]');
  if (startEndEl) {
    const student = currentStudent(ctx.state);
    startEndEl.textContent = formatClock(startPageSummary(ctx.exam, student, t).endTime);
  }
}
