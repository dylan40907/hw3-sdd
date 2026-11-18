import { referralsForOffice } from '../rules/referral.js';
import { escapeHtml, formatDateTime, formatDuration } from './format.js';

const ui = { docId: null };

function studentName(state, id) {
  return state.students.find((s) => s.id === id)?.name ?? id;
}

function renderList(el, ctx, docs) {
  el.innerHTML = `
    <div class="panel">
      <h2>Referrals</h2>
      ${docs.length ? `<table>
        <thead><tr><th>Student</th><th>What happened</th><th>Referred</th></tr></thead>
        <tbody>${docs.map((d) => `<tr class="clickable" data-doc="${d.id}">
          <td>${studentName(ctx.state, d.studentId)}</td>
          <td>${escapeHtml(d.flag.signals.map((i) => i.what).join('; '))}</td>
          <td>${formatDateTime(d.createdAt)}</td>
        </tr>`).join('')}</tbody>
      </table>` : '<p class="muted">No referrals yet.</p>'}
    </div>`;
  for (const row of el.querySelectorAll('[data-doc]')) {
    row.onclick = () => {
      ui.docId = row.dataset.doc;
      renderOfficeView(el, ctx);
    };
  }
}

function renderDocument(el, ctx, doc) {
  const c = doc.flag.context;
  el.innerHTML = `
    <div class="panel">
      <button class="secondary" data-action="back">Back to referrals</button>
      <h2>Referral for ${studentName(ctx.state, doc.studentId)}</h2>
      <dl>
        <dt>Student</dt><dd>${studentName(ctx.state, doc.studentId)}</dd>
        <dt>Referred</dt><dd>${formatDateTime(doc.createdAt)}</dd>
      </dl>
      <h3>Flag</h3>
      ${doc.flag.signals.map((i) => `
      <dl>
        <dt>What</dt><dd>${escapeHtml(i.what)}${i.technicalEvent ? ` (${escapeHtml(i.technicalEvent)})` : ''}</dd>
        <dt>When</dt><dd>${formatDateTime(i.when)}${i.until ? ` to ${formatDateTime(i.until)}` : ''}</dd>
        <dt>Why</dt><dd>${escapeHtml(i.why)}</dd>
      </dl>`).join('')}
      <dl>
        <dt>Extra time</dt><dd>${c.extraTimePct ? `${c.extraTimePct}%` : 'none'}</dd>
        <dt>Pauses</dt><dd>${c.pauses.length
          ? c.pauses.map((p) => `${escapeHtml(p.reason)}, ${p.lengthMs === null ? 'still open' : formatDuration(p.lengthMs)}`).join('; ')
          : 'none'}</dd>
      </dl>
      <h3>Evidence</h3>
      ${doc.evidence.signals.map((sig) => `
      <dl>
        <dt>Signal</dt><dd>${escapeHtml(sig.type.replace(/_/g, ' '))} at ${formatDateTime(sig.at)}</dd>
        ${sig.details.questionId ? `<dt>Question</dt><dd>${escapeHtml(sig.details.questionId.slice(1))}</dd>` : ''}
        ${sig.technicalEvent ? `<dt>Technical event</dt><dd>${escapeHtml(sig.technicalEvent)}</dd>` : ''}
      </dl>`).join('')}
      ${doc.evidence.groups.map((g) => `<dl><dt>Same answer as</dt><dd>${escapeHtml(g.otherStudents.join(', '))} (answer ${g.value})</dd></dl>`).join('')}
      <h3>Student's explanation</h3>
      <p>${escapeHtml(doc.explanation)}</p>
      <h3>Instructor's reason</h3>
      <p>${escapeHtml(doc.reason)}</p>
    </div>`;
  el.querySelector('[data-action="back"]').onclick = () => {
    ui.docId = null;
    renderOfficeView(el, ctx);
  };
}

export function renderOfficeView(el, ctx) {
  const docs = referralsForOffice(ctx.state);
  const doc = docs.find((d) => d.id === ui.docId);
  if (doc) renderDocument(el, ctx, doc);
  else renderList(el, ctx, docs);
}
