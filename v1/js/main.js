import { createStore } from './rules/store.js';
import { now } from './rules/clock.js';
import { isRunning, recordReload } from './rules/signals.js';
import { processExamEnd } from './rules/grouping.js';
import { exam, seed, students } from './data/mock-data.js';
import { renderRoleSelector } from './ui/role-selector.js';
import { renderStudentView, tickStudentView, stopExamEvents } from './ui/student-view.js';
import { renderInstructorView } from './ui/instructor-view.js';
import { renderOfficeView } from './ui/office-view.js';

const store = createStore(localStorage, seed);
let state = store.load();

const views = {
  student: document.getElementById('student-view'),
  instructor: document.getElementById('instructor-view'),
  office: document.getElementById('office-view'),
};

const errorEl = document.getElementById('error');

function showError(message) {
  errorEl.textContent = message;
  errorEl.hidden = !message;
}

const ctx = {
  get state() { return state; },
  exam,
  now,
  showError,
  // Applies a change. A rules function that rejects the action returns { ok: false, error }.
  update(fn, { render: shouldRender = true } = {}) {
    const next = fn(state);
    if (next && next.ok === false) {
      showError(next.error);
      return false;
    }
    showError('');
    if (next === state) return true;
    state = next;
    store.save(state);
    if (shouldRender) render();
    return true;
  },
};

const renderers = {
  student: renderStudentView,
  instructor: renderInstructorView,
  office: renderOfficeView,
};

const tickers = {
  student: tickStudentView,
};

function render() {
  renderRoleSelector(ctx);
  for (const [role, el] of Object.entries(views)) el.hidden = role !== state.role;
  if (state.role !== 'student') stopExamEvents();
  renderers[state.role]?.(views[state.role], ctx);
}

// Ends exams whose time is up and forms answer groups, in every role.
function runExamEnd() {
  const next = processExamEnd(state, exam, students, now());
  if (next !== state) ctx.update(() => next);
}

function tick() {
  runExamEnd();
  tickers[state.role]?.(views[state.role], ctx);
}

// A reload of a running exam (FR-022).
if (state.role === 'student' && isRunning(state.sessions[state.currentStudentId], now())) {
  state = recordReload(state, state.currentStudentId, now());
  store.save(state);
}

render();
runExamEnd();
setInterval(tick, 1000);
