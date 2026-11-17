import { flagView, keep, dismiss, canRefer, requestExplanation } from '../rules/flags.js';
import { refer } from '../rules/referral.js';
import { pauseLog } from '../rules/timer.js';
import { escapeHtml, formatDateTime, formatDuration } from './format.js';

const ui = { tab: 'flags', flagId: null, recordStudentId: 's1' };

const SIGNAL_LABELS = {
  page_leave: 'Left the exam page',
  fullscreen_exit: 'Exited fullscreen',
  paste: 'Pasted into an answer',
  fast_answer: 'Answered soon after returning',
  same_incorrect_answer: 'Same incorrect answer',
};

function studentName(state, id) {
  return state.students.find((s) => s.id === id)?.name ?? id;
}

function questionText(question, params) {
  if (!params) return question.template;
  return question.template.replace(/\{(\w+)\}/g, (_, key) => params[key]);
}

function renderTabs(el, ctx) {
  el.innerHTML = `
    <div class="actions" style="margin-top:0;margin-bottom:16px">
      <button data-tab="flags" class="${ui.tab === 'flags' ? '' : 'secondary'}">Flags</button>
      <button data-tab="record" class="${ui.tab === 'record' ? '' : 'secondary'}">Exam record</button>
    </div>
    <div data-body></div>`;
  for (const b of el.querySelectorAll('[data-tab]')) {
    b.onclick = () => {
      ui.tab = b.dataset.tab;
      ui.flagId = null;
      renderInstructorView(el, ctx);
    };
  }
  return el.querySelector('[data-body]');
}

function renderRecord(body, ctx) {
  const { state, exam } = ctx;
  const student = state.students.find((s) => s.id === ui.recordStudentId) ?? state.students[0];
  const session = state.sessions[student.id];
  const rows = exam.questions.map((q, i) => {
    let params;
    let answer;
    let submitted = '';
    if (session) {
      params = session.versions[q.id]?.params;
      answer = session.answers[q.id]?.value;
      const at = session.answers[q.id]?.submittedAt;
      submitted = at ? formatDateTime(at) : '';
    } else if (student.prefilledAnswers) {
      params = student.prefilledAnswers[q.id]?.version;
      answer = student.prefilledAnswers[q.id]?.value;
    }
    return `<tr>
      <td>Question ${i + 1}</td>
      <td>${params ? escapeHtml(questionText(q, params)) : '<span class="muted">Not opened</span>'}</td>
      <td>${escapeHtml(answer ?? '')}</td>
      <td>${submitted}</td>
    </tr>`;
  }).join('');
  const signals = state.signals.filter((s) => s.studentId === student.id);

  body.innerHTML = `
    <div class="panel">
      <label>Student
        <select data-record-student>
          ${state.students.map((s) => `<option value="${s.id}" ${s.id === student.id ? 'selected' : ''}>${s.name}</option>`).join('')}
        </select>
      </label>
      <p class="muted">${session
        ? `Started ${session.startedAt ? formatDateTime(session.startedAt) : 'not yet'}${session.endedAt ? `, ended ${formatDateTime(session.endedAt)}` : ''}.`
        : 'Answers from mock data.'}</p>
      <h3>Versions received</h3>
      <table><thead><tr><th></th><th>Version</th><th>Answer</th><th>Submitted</th></tr></thead><tbody>${rows}</tbody></table>
      <h3>Pauses</h3>
      ${session && session.pauses.length ? `<table><thead><tr><th>Reason</th><th>Started</th><th>Length</th></tr></thead><tbody>
        ${pauseLog(session).map((p) => `<tr><td>${escapeHtml(p.reason)}</td><td>${formatDateTime(p.from)}</td>
          <td>${p.lengthMs === null ? 'still open' : formatDuration(p.lengthMs)}</td></tr>`).join('')}
      </tbody></table>` : '<p class="muted">No pauses.</p>'}
      <h3>Signals</h3>
      ${signals.length ? `<table><thead><tr><th>Type</th><th>Time</th><th>Details</th></tr></thead><tbody>
        ${signals.map((s) => `<tr><td>${SIGNAL_LABELS[s.type]}</td><td>${formatDateTime(s.at)}</td>
          <td>${escapeHtml(signalDetails(s))}</td></tr>`).join('')}
      </tbody></table>` : '<p class="muted">No signals recorded.</p>'}
    </div>`;
  body.querySelector('[data-record-student]').onchange = (e) => {
    ui.recordStudentId = e.target.value;
    renderRecord(body, ctx);
  };
}

function signalDetails(signal) {
  const d = signal.details || {};
  const parts = [];
  if (d.cause === 'reload') parts.push('page reload');
  if (signal.until) parts.push(`returned ${formatDateTime(signal.until)}`);
  if (d.questionId) parts.push(`question ${d.questionId.slice(1)}`);
  if (d.secondsSinceReturn !== undefined) parts.push(`${d.secondsSinceReturn} s after returning`);
  if (d.groupId) parts.push(`answer ${d.value}`);
  return parts.join(', ');
}

const STATE_LABELS = {
  new: 'New',
  kept: 'Kept',
  dismissed: 'Dismissed',
  explanation_requested: 'Explanation requested',
  explained: 'Explained',
  referred: 'Referred',
};

function updateFlag(state, flagId, fn) {
  const flag = state.flags.find((f) => f.id === flagId);
  const result = fn(flag);
  if (result && result.ok === false) return result;
  return { ...state, flags: state.flags.map((f) => (f.id === flagId ? result : f)) };
}

function renderFlagList(body, ctx) {
  const { state } = ctx;
  const flags = [...state.flags].sort((a, b) => flagView(b, state).when - flagView(a, state).when);
  body.innerHTML = `
    <div class="panel">
      <h2>Flags</h2>
      ${flags.length ? `<table>
        <thead><tr><th>Student</th><th>What happened</th><th>When</th><th>State</th></tr></thead>
        <tbody>${flags.map((f) => {
          const v = flagView(f, state);
          return `<tr class="clickable" data-flag="${f.id}">
            <td>${studentName(state, f.studentId)}</td>
            <td>${escapeHtml(v.what)}</td>
            <td>${formatDateTime(v.when)}</td>
            <td><span class="flag-state ${f.state === 'dismissed' ? 'dismissed' : ''}">${STATE_LABELS[f.state]}</span></td>
          </tr>`;
        }).join('')}</tbody>
      </table>` : '<p class="muted">No flags yet.</p>'}
    </div>`;
  for (const row of body.querySelectorAll('[data-flag]')) {
    row.onclick = () => {
      ui.flagId = row.dataset.flag;
      renderFlagDetail(body, ctx);
    };
  }
}

function contextList(view) {
  const c = view.context;
  const items = [`Extra time: ${c.extraTimePct ? `${c.extraTimePct}%` : 'none'}`];
  items.push(c.pauses.length
    ? `Pauses: ${c.pauses.map((p) => `${p.reason}, ${p.lengthMs === null ? 'still open' : formatDuration(p.lengthMs)} at ${formatDateTime(p.from)}`).join('; ')}`
    : 'Pauses: none');
  if (c.technicalEvent) items.push(`Technical event: ${c.technicalEvent}`);
  if (c.group) items.push(`Same answer (${c.group.value}) as: ${c.group.otherStudents.join(', ')}`);
  return `<ul>${items.map((i) => `<li>${escapeHtml(i)}</li>`).join('')}</ul>`;
}

function renderFlagDetail(body, ctx) {
  const { state } = ctx;
  const flag = state.flags.find((f) => f.id === ui.flagId);
  if (!flag) {
    ui.flagId = null;
    renderFlagList(body, ctx);
    return;
  }
  const view = flagView(flag, state);
  const t = ctx.now();
  body.innerHTML = `
    <div class="panel">
      <button class="secondary" data-action="back">Back to flags</button>
      <h2>${escapeHtml(view.what)}</h2>
      <p><span class="flag-state ${flag.state === 'dismissed' ? 'dismissed' : ''}">${STATE_LABELS[flag.state]}</span></p>
      <dl>
        <dt>Student</dt><dd>${studentName(state, flag.studentId)}</dd>
        <dt>When</dt><dd>${formatDateTime(view.when)}${view.until ? ` to ${formatDateTime(view.until)}` : ''}</dd>
        <dt>Why</dt><dd>${escapeHtml(view.why)}</dd>
      </dl>
      <h3>Context</h3>
      ${contextList(view)}
      ${flag.explanationRequestedAt ? `
      <h3>Explanation</h3>
      <dl>
        <dt>Requested</dt><dd>${formatDateTime(flag.explanationRequestedAt)}</dd>
        <dt>Deadline</dt><dd>${formatDateTime(flag.deadline)}${t > flag.deadline ? ' (passed)' : ''}</dd>
        <dt>Student's explanation</dt><dd>${flag.explanation ? escapeHtml(flag.explanation.text) : '<span class="muted">None yet</span>'}</dd>
      </dl>` : ''}
      <div class="actions">
        ${flag.state === 'new' ? '<button data-action="keep">Keep</button>' : ''}
        ${flag.state === 'kept' ? '<button data-action="ask">Ask for explanation</button>' : ''}
        ${['new', 'kept', 'explanation_requested', 'explained'].includes(flag.state) ? '<button class="secondary" data-action="dismiss">Dismiss</button>' : ''}
      </div>
      ${flag.state === 'referred' ? '<p>Referred to the integrity office.</p>' : `
      <div data-refer>
        <h3>Refer to the integrity office</h3>
        ${canRefer(flag, t) ? '' : '<p class="muted">Available after the student explains or the deadline passes.</p>'}
        <label>Reason<textarea data-refer-reason ${canRefer(flag, t) ? '' : 'disabled'}></textarea></label>
        <div class="actions">
          <button data-action="refer" ${canRefer(flag, t) ? '' : 'disabled'}>Refer to integrity office</button>
        </div>
      </div>`}
    </div>`;

  body.querySelector('[data-action="back"]').onclick = () => {
    ui.flagId = null;
    renderFlagList(body, ctx);
  };
  const act = (name, fn) => {
    const button = body.querySelector(`[data-action="${name}"]`);
    if (button) button.onclick = () => ctx.update((st) => updateFlag(st, flag.id, fn));
  };
  act('keep', keep);
  act('dismiss', dismiss);
  act('ask', (f) => requestExplanation(f, ctx.now()));
  const referButton = body.querySelector('[data-action="refer"]');
  if (referButton) {
    referButton.onclick = () => {
      const reason = body.querySelector('[data-refer-reason]').value;
      ctx.update((st) => refer(st, flag.id, reason, ctx.now()));
    };
  }
}

export function renderInstructorView(el, ctx) {
  const body = renderTabs(el, ctx);
  if (ui.tab === 'record') renderRecord(body, ctx);
  else if (ui.flagId) renderFlagDetail(body, ctx);
  else renderFlagList(body, ctx);
}
