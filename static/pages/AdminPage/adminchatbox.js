function initAdminChatbox() {
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
  let allContacts = [];
  let pendingConversationStart = null;

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

  function getActiveTabName() {
    const activeBtn = document.querySelector('.chatbox-tab-btn.active');
    if (activeBtn) {
      return activeBtn.getAttribute('data-tab') === 'admins' ? 'admins' : 'users';
    }
    const usersPanel = document.getElementById('users-panel');
    if (usersPanel && usersPanel.classList.contains('active')) return 'users';
    return 'admins';
  }

  function getCurrentUserRole() {
    const root = document.getElementById('admin-chatbox');
    const role = root && root.dataset ? root.dataset.currentUserRole : '';
    return (role || '').toLowerCase();
  }

  function isRestrictedUser() {
    return getCurrentUserRole() === 'user';
  }

  function setActiveTab(targetTab, tabButtons, tabPanels) {
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

    const targetBtn = Array.from(tabButtons).find((btn) => btn.getAttribute('data-tab') === targetTab);
    if (targetBtn) {
      targetBtn.classList.add('active', 'text-blue-700', 'border-blue-700');
      targetBtn.classList.remove('text-slate-500');
    }
  }

  function getPanelPrefixFromRole(role) {
    return role === 'admin' ? 'admins' : 'users';
  }

  function escapeHtml(text) {
    return String(text || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function getHighlightedName(fullName, query) {
    const rawName = String(fullName || '');
    const lowerName = rawName.toLowerCase();
    const lowerQuery = String(query || '').toLowerCase();
    const start = lowerName.indexOf(lowerQuery);
    if (start < 0 || !lowerQuery) {
      return escapeHtml(rawName);
    }
    const end = start + lowerQuery.length;
    return `${escapeHtml(rawName.slice(0, start))}<mark class="chatbox-search-mark">${escapeHtml(rawName.slice(start, end))}</mark>${escapeHtml(rawName.slice(end))}`;
  }

  function showThreadPanel(panelPrefix, statusText) {
    const targetTab = panelPrefix === 'admins' ? 'admins' : 'users';
    const tabButtons = document.querySelectorAll('.chatbox-tab-btn');
    const tabPanels = document.querySelectorAll('.chatbox-tab-panel');
    if (tabButtons.length && tabPanels.length) {
      setActiveTab(targetTab, tabButtons, tabPanels);
    }

    const chatboxPopup = document.getElementById('chatbox-popup');
    const chatboxBack = document.getElementById('chatbox-back');
    if (chatboxPopup) chatboxPopup.classList.add('chat-in-thread');
    if (chatboxBack) chatboxBack.classList.remove('hidden');

    messagesList = document.getElementById(`${panelPrefix}-messages-list`);
    const targetContainer = document.getElementById(`${panelPrefix}-messages-container`);
    const otherPrefix = panelPrefix === 'admins' ? 'users' : 'admins';
    const otherContainer = document.getElementById(`${otherPrefix}-messages-container`);
    if (targetContainer) targetContainer.classList.remove('hidden');
    if (otherContainer) otherContainer.classList.add('hidden');

    if (messagesList && statusText) {
      messagesList.innerHTML = `<div class="text-xs text-slate-400 p-2">${statusText}</div>`;
    }
  }

  function createContactCard(conv, roleLabel) {
    const other = conv.other_participant;
    const card = document.createElement('div');
    card.className = 'chat-contact-card p-3 rounded-lg bg-slate-50 hover:bg-slate-100 cursor-pointer transition border border-slate-200';
    card.setAttribute('data-contact-id', other.user_id);
    card.setAttribute('data-name', `${other.first_name} ${other.last_name}`);
    if (conv.conversation_id) {
      card.setAttribute('data-conversation-id', conv.conversation_id);
    }
    if (conv.product_id) card.setAttribute('data-product-id', conv.product_id);
    card.setAttribute('data-has-history', conv.has_history ? 'true' : 'false');
    const messagePreview = `Last message: ${conv.last_message_preview || '-'}`;
    card.innerHTML = `<p class="font-medium text-sm text-slate-900">${other.first_name} ${other.last_name}</p>
                      <p class="text-xs text-slate-500">${messagePreview}</p>`;
    return card;
  }

  function renderConversationLists(conversations) {
    const adminsList = document.getElementById('admins-list');
    const usersList = document.getElementById('users-list');
    if (!adminsList || !usersList) return;

    adminsList.innerHTML = '';
    usersList.innerHTML = '';

    allContacts = conversations.filter((c) => c && c.other_participant);
    const historyContacts = allContacts.filter((c) => c.has_history && c.conversation_id);
    const adminContacts = historyContacts.filter((c) => c.other_participant.role === 'admin');
    const userContacts = historyContacts.filter((c) => c.other_participant.role === 'user');

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

    const searchInput = document.getElementById('chatbox-search');
    if (searchInput && searchInput.value) {
      updateSearchSuggestions(searchInput.value);
    }
  }

  function updateSearchSuggestions(rawQuery) {
    const suggestions = document.getElementById('chatbox-search-suggestions');
    const searchWrap = document.getElementById('chatbox-search-wrap');
    if (!suggestions) return;

    const query = (rawQuery || '').trim().toLowerCase();
    if (!query) {
      suggestions.classList.add('hidden');
      suggestions.innerHTML = '';
      if (searchWrap) searchWrap.classList.remove('is-searching');
      return;
    }
    if (searchWrap) searchWrap.classList.add('is-searching');
    const restrictedUser = isRestrictedUser();
    const activeTab = getActiveTabName();

    const matched = allContacts
      .filter((c) => {
        const other = c.other_participant || {};
        if (activeTab === 'admins' && other.role !== 'admin') return false;
        if (activeTab === 'users' && other.role !== 'user') return false;
        if (restrictedUser && activeTab === 'users' && !(c.has_history && c.conversation_id)) return false;
        const fullName = `${other.first_name || ''} ${other.last_name || ''}`.trim().toLowerCase();
        return fullName.includes(query);
      })
      .sort((a, b) => {
        const nameA = `${a.other_participant.first_name || ''} ${a.other_participant.last_name || ''}`.trim().toLowerCase();
        const nameB = `${b.other_participant.first_name || ''} ${b.other_participant.last_name || ''}`.trim().toLowerCase();
        const idxA = nameA.indexOf(query);
        const idxB = nameB.indexOf(query);
        if (idxA !== idxB) return idxA - idxB;
        return nameA.localeCompare(nameB);
      })
      .slice(0, 8);

    if (!matched.length) {
      suggestions.classList.remove('hidden');
      suggestions.innerHTML = activeTab === 'users' && restrictedUser
        ? '<div class="chatbox-search-empty">No matching past conversations. New user chats must start from a product page.</div>'
        : '<div class="chatbox-search-empty">No matching users/admins</div>';
      return;
    }

    const rows = matched.map((conv) => {
      const other = conv.other_participant;
      const role = other.role || 'user';
      const actionText = conv.conversation_id ? 'Open chat' : 'Start new chat';
      const name = `${other.first_name} ${other.last_name}`.trim();
      const initials = name
        .split(' ')
        .filter(Boolean)
        .slice(0, 2)
        .map((part) => part[0].toUpperCase())
        .join('') || 'U';
      const highlightedName = getHighlightedName(name, query);
      const roleLabel = role === 'admin' ? 'Admin' : 'User';
      return `<button type="button"
                      class="chatbox-search-item"
                      data-search-contact-id="${other.user_id}">
                <span class="chatbox-search-avatar">${initials}</span>
                <span class="chatbox-search-content">
                  <span class="chatbox-search-name">${highlightedName}</span>
                  <span class="chatbox-search-meta">${roleLabel}</span>
                </span>
                <span class="chatbox-search-action">${actionText}</span>
              </button>`;
    }).join('');

    suggestions.innerHTML = `<div class="chatbox-search-header">${matched.length} suggestion${matched.length > 1 ? 's' : ''}</div>${rows}`;
    suggestions.classList.remove('hidden');
  }

  function openConversation(conversationId, productId, panelPrefix) {
    currentConversationId = conversationId;
    currentProductId = productId || null;
    showThreadPanel(panelPrefix, 'Loading messages...');

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

    const root = document.getElementById('admin-chatbox');
    const currentUserId = Number(root && root.dataset ? root.dataset.currentUserId : 0);
    const senderId = Number(message.sender_id || 0);
    const senderName = (message.sender_username || String(message.sender_id || 'User')).trim();
    const initials = senderName.split(' ').filter(Boolean).slice(0, 2).map((part) => part[0].toUpperCase()).join('') || 'U';
    const isOwn = currentUserId > 0 && senderId === currentUserId;
    const sideClass = isOwn ? 'right-msg' : 'left-msg';
    const time = message.sent_at ? new Date(message.sent_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';
    const safeText = String(message.content || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    const el = document.createElement('div');
    el.className = `msg ${sideClass}`;
    el.innerHTML = `<div class="msg-img">${initials}</div>
                    <div class="msg-bubble">
                      <div class="msg-info">
                        <div class="msg-info-name">${senderName}</div>
                        <div class="msg-info-time">${time}</div>
                      </div>
                      <div class="msg-text">${safeText}</div>
                    </div>`;
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
    pendingConversationStart = null;
    updateSearchSuggestions('');
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
    const searchWrap = document.getElementById('chatbox-search-wrap');
    if (searchWrap && !document.getElementById('chatbox-search-suggestions')) {
      const suggestions = document.createElement('div');
      suggestions.id = 'chatbox-search-suggestions';
      suggestions.className = 'hidden mt-2 max-h-44 overflow-y-auto rounded-lg border border-slate-200 bg-white shadow-sm';
      searchWrap.appendChild(suggestions);
    }

    if (chatboxToggle) {
      chatboxToggle.addEventListener('click', function (e) {
        e.stopPropagation();
        const isHidden = chatboxPopup.classList.toggle('hidden');
        if (!isHidden) {
          resetToMenuMode();
          setActiveTab('admins', tabButtons, tabPanels);
          if (searchInput) searchInput.value = '';
          updateSearchSuggestions('');
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
        setActiveTab(targetTab, tabButtons, tabPanels);
        const searchValue = searchInput ? searchInput.value : '';
        updateSearchSuggestions(searchValue || '');
      });
    });

    // Ensure initial state is truly on Admins tab.
    setActiveTab('admins', tabButtons, tabPanels);
    if (searchInput) {
      searchInput.addEventListener('input', function (e) {
        updateSearchSuggestions(e.target.value || '');
      });
      searchInput.addEventListener('focus', function (e) {
        updateSearchSuggestions(e.target.value || '');
      });
      searchInput.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
          updateSearchSuggestions('');
          e.target.blur();
        }
      });
    }

    document.addEventListener('click', function (e) {
      const searchWrapEl = document.getElementById('chatbox-search-wrap');
      const suggestions = document.getElementById('chatbox-search-suggestions');
      if (suggestions && searchWrapEl && !searchWrapEl.contains(e.target)) {
        suggestions.classList.add('hidden');
        searchWrapEl.classList.remove('is-searching');
      }
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
    const chatboxTitle = document.getElementById('chatbox-title');
    const displayName = card.getAttribute('data-name');
    if (chatboxTitle && displayName) {
      chatboxTitle.textContent = displayName;
    }
    if (conversationId) {
      openConversation(Number(conversationId), productId ? Number(productId) : null, panelPrefix);
      return;
    }
  });

  document.addEventListener('click', function (e) {
    const suggestion = e.target.closest('[data-search-contact-id]');
    if (!suggestion) return;
    e.stopImmediatePropagation();

    const targetUserId = Number(suggestion.getAttribute('data-search-contact-id'));
    const conv = allContacts.find((item) => Number(item.other_participant.user_id) === targetUserId);
    if (!conv) return;
    if (isRestrictedUser() && conv.other_participant.role === 'user' && !conv.conversation_id) return;

    const displayName = `${conv.other_participant.first_name} ${conv.other_participant.last_name}`;
    const panelPrefix = getPanelPrefixFromRole(conv.other_participant.role);
    const chatboxTitle = document.getElementById('chatbox-title');
    if (chatboxTitle) chatboxTitle.textContent = displayName;

    const searchInput = document.getElementById('chatbox-search');
    const suggestions = document.getElementById('chatbox-search-suggestions');
    if (searchInput) searchInput.value = displayName;
    if (suggestions) updateSearchSuggestions('');

    if (conv.conversation_id) {
      openConversation(Number(conv.conversation_id), conv.product_id ? Number(conv.product_id) : null, panelPrefix);
      return;
    }

    if (!socket) return;
    pendingConversationStart = {
      targetUserId,
      panelPrefix,
      displayName,
    };
    showThreadPanel(panelPrefix, 'Creating conversation...');
    socket.emit('start_conversation', { target_user_id: targetUserId });
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

    socket.on('conversation_started', (data) => {
      const targetUserId = Number(data.target_user_id);
      const matched = allContacts.find((c) => Number(c.other_participant.user_id) === targetUserId);
      const panelPrefix = pendingConversationStart && pendingConversationStart.targetUserId === targetUserId
        ? pendingConversationStart.panelPrefix
        : getPanelPrefixFromRole(matched && matched.other_participant ? matched.other_participant.role : 'user');

      if (matched) {
        matched.conversation_id = data.conversation_id;
        matched.product_id = data.product_id || matched.product_id || null;
        matched.has_history = true;
      }

      openConversation(Number(data.conversation_id), data.product_id ? Number(data.product_id) : null, panelPrefix);
      pendingConversationStart = null;
      requestConversations();
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
}

initAdminChatbox();
