(function () {
  if (window.__adminChatboxInitialized) return;
  window.__adminChatboxInitialized = true;

  const backendOrigin = `${window.location.protocol}//${window.location.hostname}:5000`;
  const socket = window.io
    ? io(backendOrigin, {
        path: '/socket.io',
        transports: ['polling'],
      })
    : null;
  let currentConversationId = null;
  let currentProductId = null;
  let messagesList = null;
  let messageLoadTimeout = null;

  function setListStatus(message) {
    const adminList = document.getElementById('admins-list');
    const userList = document.getElementById('users-list');
    const html = `<div class="p-3 text-xs text-slate-400">${message}</div>`;
    if (adminList) adminList.innerHTML = html;
    if (userList) userList.innerHTML = html;
  }

  function requestConversations() {
    if (!socket) {
      setListStatus('Socket unavailable');
      return;
    }
    if (socket.connected) {
      socket.emit('list_conversations');
    } else {
      socket.connect();
    }
  }

  function getPanelPrefix(panelElement) {
    return panelElement && panelElement.id && panelElement.id.startsWith('admins') ? 'admins' : 'users';
  }

  function createContactCard(conv, roleLabel) {
    const other = conv.other_participant;
    const card = document.createElement('div');
    card.className = 'chat-contact-card p-3 rounded-lg bg-slate-50 hover:bg-slate-100 cursor-pointer transition border border-slate-200';
    card.setAttribute('data-contact-id', other.user_id);
    card.setAttribute('data-name', `${other.first_name} ${other.last_name}`);
    card.setAttribute('data-conversation-id', conv.conversation_id);
    if (conv.product_id) card.setAttribute('data-product-id', conv.product_id);
    card.innerHTML = `<p class="font-medium text-sm text-slate-900">${other.first_name} ${other.last_name}</p>
                      <p class="text-xs text-slate-500">${roleLabel} - Last message: ${conv.last_message_preview || '-'}</p>`;
    return card;
  }

  function renderConversationLists(conversations) {
    const adminsList = document.getElementById('admins-list');
    const usersList = document.getElementById('users-list');
    if (!adminsList || !usersList) return;

    adminsList.innerHTML = '';
    usersList.innerHTML = '';

    const withHistory = conversations.filter((c) => c && c.has_history && c.conversation_id && c.other_participant);
    const adminContacts = withHistory.filter((c) => c.other_participant.role === 'admin');
    const userContacts = withHistory.filter((c) => c.other_participant.role === 'user');

    if (adminContacts.length === 0) {
      adminsList.innerHTML = '<div class="p-3 text-xs text-slate-400">No admin conversation history</div>';
    } else {
      adminContacts.forEach((conv) => adminsList.appendChild(createContactCard(conv, 'admin')));
    }

    if (userContacts.length === 0) {
      usersList.innerHTML = '<div class="p-3 text-xs text-slate-400">No user conversation history</div>';
    } else {
      userContacts.forEach((conv) => usersList.appendChild(createContactCard(conv, 'user')));
    }
  }

  function openConversation(conversationId, productId, panelPrefix) {
    currentConversationId = conversationId;
    currentProductId = productId || null;
    messagesList = document.getElementById(`${panelPrefix}-messages-list`);

    const chatboxPopup = document.getElementById('chatbox-popup');
    const chatboxBack = document.getElementById('chatbox-back');
    if (chatboxPopup) chatboxPopup.classList.add('chat-in-thread');
    if (chatboxBack) chatboxBack.classList.remove('hidden');

    const targetContainer = document.getElementById(`${panelPrefix}-messages-container`);
    const otherPrefix = panelPrefix === 'admins' ? 'users' : 'admins';
    const otherContainer = document.getElementById(`${otherPrefix}-messages-container`);
    if (targetContainer) targetContainer.classList.remove('hidden');
    if (otherContainer) otherContainer.classList.add('hidden');

    if (messagesList) {
      messagesList.innerHTML = '<div class="text-xs text-slate-400 p-2">Loading messages...</div>';
    }

    if (socket) {
      if (socket.connected) {
        socket.emit('join_conversation', { conversation_id: conversationId });
        socket.emit('load_message', { conversation_id: conversationId });
      } else {
        socket.connect();
      }
      if (messageLoadTimeout) clearTimeout(messageLoadTimeout);
      messageLoadTimeout = setTimeout(() => {
        if (!messagesList) return;
        messagesList.innerHTML = '<div class="text-xs text-red-500 p-2">Socket not connected or no response yet.</div>';
      }, 7000);
    } else if (messagesList) {
      messagesList.innerHTML = '<div class="text-xs text-red-500 p-2">Socket library missing. Check base template socket.io script.</div>';
    }
  }

  function appendMessageToList(message) {
    if (!messagesList) return;
    const el = document.createElement('div');
    el.className = 'p-2 mb-2 rounded bg-slate-50';
    el.innerHTML = `<p class="text-xs text-slate-600">${message.sender_username || message.sender_id}</p>
                    <p class="text-sm text-slate-900">${message.content}</p>
                    <p class="text-xs text-slate-400 mt-1">${message.sent_at ? new Date(message.sent_at).toLocaleTimeString() : ''}</p>`;
    messagesList.appendChild(el);
    messagesList.scrollTop = messagesList.scrollHeight;
  }

  function resetToMenuMode() {
    const chatboxPopup = document.getElementById('chatbox-popup');
    const chatboxBack = document.getElementById('chatbox-back');
    const title = document.getElementById('chatbox-title');
    const adminsContainer = document.getElementById('admins-messages-container');
    const usersContainer = document.getElementById('users-messages-container');

    if (chatboxPopup) chatboxPopup.classList.remove('chat-in-thread');
    if (chatboxBack) chatboxBack.classList.add('hidden');
    if (title) title.textContent = 'Chat';
    if (adminsContainer) adminsContainer.classList.add('hidden');
    if (usersContainer) usersContainer.classList.add('hidden');
    if (messageLoadTimeout) {
      clearTimeout(messageLoadTimeout);
      messageLoadTimeout = null;
    }
    currentConversationId = null;
    currentProductId = null;
    messagesList = null;
  }

  document.addEventListener('DOMContentLoaded', function () {
    const chatboxToggle = document.getElementById('chatbox-toggle');
    const chatboxPopup = document.getElementById('chatbox-popup');
    const chatboxClose = document.getElementById('chatbox-close');
    const chatboxBack = document.getElementById('chatbox-back');
    const chatboxTitle = document.getElementById('chatbox-title');
    const tabButtons = document.querySelectorAll('.chatbox-tab-btn');
    const tabPanels = document.querySelectorAll('.chatbox-tab-panel');
    const searchInput = document.getElementById('chatbox-search');

    if (chatboxToggle) {
      chatboxToggle.addEventListener('click', function (e) {
        e.stopPropagation();
        const isHidden = chatboxPopup.classList.toggle('hidden');
        if (!isHidden) {
          resetToMenuMode();
          setListStatus('Loading...');
          requestConversations();
        }
      });
    }

    if (chatboxClose) {
      chatboxClose.addEventListener('click', function () {
        chatboxPopup.classList.add('hidden');
        resetToMenuMode();
      });
    }

    if (chatboxBack) {
      chatboxBack.addEventListener('click', function () {
        resetToMenuMode();
      });
    }

    tabButtons.forEach((btn) => {
      btn.addEventListener('click', function () {
        const targetTab = btn.getAttribute('data-tab');
        tabPanels.forEach((panel) => {
          panel.classList.add('hidden');
          panel.classList.remove('active');
        });
        tabButtons.forEach((otherBtn) => {
          otherBtn.classList.remove('active', 'text-blue-700', 'border-blue-700');
          otherBtn.classList.add('text-slate-500');
        });
        const targetPanel = document.getElementById(`${targetTab}-panel`);
        if (targetPanel) {
          targetPanel.classList.remove('hidden');
          targetPanel.classList.add('active');
        }
        btn.classList.add('active', 'text-blue-700', 'border-blue-700');
        btn.classList.remove('text-slate-500');
      });
    });

    if (searchInput) {
      searchInput.addEventListener('input', function (e) {
        const query = (e.target.value || '').toLowerCase();
        ['admins-list', 'users-list'].forEach((listId) => {
          const container = document.getElementById(listId);
          if (!container) return;
          container.querySelectorAll('[data-name]').forEach((item) => {
            const name = (item.getAttribute('data-name') || '').toLowerCase();
            item.style.display = name.includes(query) ? 'block' : 'none';
          });
        });
      });
    }

    document.addEventListener('click', function (e) {
      if (chatboxToggle && chatboxPopup && !chatboxToggle.contains(e.target) && !chatboxPopup.contains(e.target)) {
        chatboxPopup.classList.add('hidden');
        resetToMenuMode();
      }
    });
  });

  document.addEventListener('click', function (e) {
    const card = e.target.closest('[data-contact-id]');
    if (!card) return;
    const panelPrefix = getPanelPrefix(card.closest('.chatbox-tab-panel'));
    const conversationId = card.getAttribute('data-conversation-id');
    const productId = card.getAttribute('data-product-id');
    if (!conversationId) return;
    const chatboxTitle = document.getElementById('chatbox-title');
    const displayName = card.getAttribute('data-name');
    if (chatboxTitle && displayName) {
      chatboxTitle.textContent = displayName;
    }
    openConversation(Number(conversationId), productId ? Number(productId) : null, panelPrefix);
  });

  document.addEventListener('click', function (e) {
    if (!e.target.matches('.admins-send-btn') && !e.target.matches('.users-send-btn')) return;
    const input = e.target.matches('.admins-send-btn') ? document.getElementById('admins-message-input') : document.getElementById('users-message-input');
    if (!input || !socket) return;
    const content = input.value.trim();
    if (!content || !currentConversationId) return;

    socket.emit('send_message', {
      conversation_id: currentConversationId,
      product_id: currentProductId,
      content,
    });
    input.value = '';
  });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Enter') return;
    const target = e.target;
    if (!target || target.tagName !== 'INPUT' || !target.id || !target.id.endsWith('-message-input')) return;
    e.preventDefault();
    const panelPrefix = target.id.startsWith('admins') ? 'admins' : 'users';
    const sendBtn = document.querySelector(`.${panelPrefix}-send-btn`);
    if (sendBtn) sendBtn.click();
  });

  if (socket) {
    socket.on('connect', () => {
      console.log('Chat socket connected:', socket.id);
      if (currentConversationId) {
        socket.emit('join_conversation', { conversation_id: currentConversationId });
        socket.emit('load_message', { conversation_id: currentConversationId });
      } else {
        socket.emit('list_conversations');
      }
    });

    socket.on('disconnect', () => {
      console.warn('Chat socket disconnected');
    });

    socket.on('message_history', (data) => {
      if (!messagesList) return;
      if (messageLoadTimeout) {
        clearTimeout(messageLoadTimeout);
        messageLoadTimeout = null;
      }
      const messages = data.messages || [];
      messagesList.innerHTML = '';
      if (!messages.length) {
        messagesList.innerHTML = '<div class="text-xs text-slate-400 p-2">No messages yet</div>';
        return;
      }
      messages.forEach((m) => appendMessageToList(m));
    });

    socket.on('message_received', (data) => {
      if (!messagesList || String(data.conversation_id) !== String(currentConversationId)) return;
      appendMessageToList(data);
      requestConversations();
    });

    socket.on('conversations_list', (data) => {
      renderConversationLists(data.conversations || []);
    });

    socket.on('error', (err) => {
      console.error('Chat socket error:', err);
      if (messagesList) {
        messagesList.innerHTML += '<div class="text-xs text-red-500 p-2">Realtime error</div>';
      }
    });

    socket.on('connect_error', (err) => {
      console.error('Socket connect_error:', err);
      if (messagesList) {
        const detail = err && err.message ? err.message : 'Connection failed';
        messagesList.innerHTML = `<div class="text-xs text-red-500 p-2">Socket connect error: ${detail}</div>`;
      }
    });
  }
})();
