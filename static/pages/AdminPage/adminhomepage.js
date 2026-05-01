// adminhomepage.js
// Simple tab toggler for admin moderation panels
document.addEventListener('DOMContentLoaded', function () {
  const tabButtons = document.querySelectorAll('.admin-tab-button');
  const panels = document.querySelectorAll('.admin-tab-panel');

  function activate(targetId, button) {
    panels.forEach(p => p.classList.add('hidden'));
    tabButtons.forEach(b => b.classList.remove('text-blue-700', 'border-blue-700'));
    const panel = document.getElementById(targetId);
    if (panel) panel.classList.remove('hidden');
    if (button) {
      button.classList.add('text-blue-700', 'border-blue-700');
    }
  }

  tabButtons.forEach(btn => {
    btn.addEventListener('click', function () {
      const target = btn.getAttribute('data-tab-target');
      activate(target, btn);
    });
  });
});
