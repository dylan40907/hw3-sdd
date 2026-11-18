export function renderRoleSelector(ctx) {
  const { state } = ctx;
  const roleSelect = document.getElementById('role');
  const studentSelect = document.getElementById('student');
  const picker = document.getElementById('student-picker');

  roleSelect.value = state.role;

  const playable = state.students.filter((s) => s.playable);
  studentSelect.innerHTML = playable
    .map((s) => `<option value="${s.id}">${s.name}${s.extraTimePct ? ` (${s.extraTimePct}% extra time)` : ''}</option>`)
    .join('');
  studentSelect.value = state.currentStudentId;
  picker.hidden = state.role !== 'student';

  roleSelect.onchange = () => ctx.update((st) => ({ ...st, role: roleSelect.value }));
  studentSelect.onchange = () => ctx.update((st) => ({ ...st, currentStudentId: studentSelect.value }));
}
