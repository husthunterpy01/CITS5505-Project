document.addEventListener('DOMContentLoaded', function () {
  const chatboxToggle = document.getElementById('chatbox-toggle');
  const chatboxPopup = document.getElementById('chatbox-popup');
  const chatboxClose = document.getElementById('chatbox-close');
  const tabButtons = document.querySelectorAll('.chatbox-tab-btn');
  const tabPanels = document.querySelectorAll('.chatbox-tab-panel');
  const searchInput = document.getElementById('chatbox-search');

  // Toggle popup visibility
  if (chatboxToggle) {
    chatboxToggle.addEventListener('click', function () {
      chatboxPopup.classList.toggle('hidden');
    });
  }

  // Close popup
  if (chatboxClose) {
    chatboxClose.addEventListener('click', function () {
      chatboxPopup.classList.add('hidden');
    });
  }

  // Tab switching
  tabButtons.forEach(btn => {
    btn.addEventListener('click', function () {
      const targetTab = btn.getAttribute('data-tab');

      // Hide all panels
      tabPanels.forEach(panel => {
        panel.classList.add('hidden');
        panel.classList.remove('active');
      });

      // Remove active state from all buttons
      tabButtons.forEach(b => {
        b.classList.remove('active');
        b.classList.remove('text-blue-700', 'border-blue-700');
        b.classList.add('text-slate-500');
      });

      // Show selected panel
      const targetPanel = document.getElementById(targetTab + '-panel');
      if (targetPanel) {
        targetPanel.classList.remove('hidden');
        targetPanel.classList.add('active');
      }

      // Mark button as active
      btn.classList.add('active', 'text-blue-700', 'border-blue-700');
      btn.classList.remove('text-slate-500');
    });
  });

  // Search functionality
  if (searchInput) {
    searchInput.addEventListener('input', function (e) {
      const query = e.target.value.toLowerCase();
      const adminsList = document.getElementById('admins-list');
      const usersList = document.getElementById('users-list');

      // Filter admin conversations
      if (adminsList) {
        const admins = adminsList.querySelectorAll('[data-name]');
        admins.forEach(admin => {
          const name = admin.getAttribute('data-name').toLowerCase();
          admin.style.display = name.includes(query) ? 'block' : 'none';
        });
      }

      // Filter user conversations
      if (usersList) {
        const users = usersList.querySelectorAll('[data-name]');
        users.forEach(user => {
          const name = user.getAttribute('data-name').toLowerCase();
          user.style.display = name.includes(query) ? 'block' : 'none';
        });
      }
    });
  }

  // Close popup when clicking outside
  document.addEventListener('click', function (e) {
    if (
      !chatboxToggle.contains(e.target) &&
      !chatboxPopup.contains(e.target)
    ) {
      chatboxPopup.classList.add('hidden');
    }
  });

  // Send message functionality (placeholder)
  const messageInput = document.getElementById('chatbox-message-input');
  const sendBtn = document.querySelector('.chatbox-popup button:last-of-type');
  if (sendBtn) {
    sendBtn.addEventListener('click', function () {
      const message = messageInput.value.trim();
      if (message) {
        console.log('Message sent:', message);
        messageInput.value = '';
        // Here you can add code to send the message via AJAX
      }
    });
  }

  // Allow sending message with Enter key
  if (messageInput) {
    messageInput.addEventListener('keypress', function (e) {
      if (e.key === 'Enter') {
        sendBtn.click();
      }
    });
  }
});
