(function(){
  // messaging page JS (pure JS, no Django template tags). Relies on window.currentUser and window.chatUser to be set by the template.
  if (typeof window === 'undefined') return;
  const chatBox = document.getElementById('chat-box');
  const sendBtn = document.getElementById('send-btn');
  const messageInput = document.getElementById('message-input');
  const scrollBtn = document.getElementById('scroll-to-bottom');
  const scrollUnread = document.getElementById('scroll-unread');

  function smoothScrollToBottom(){ if (!chatBox) return; chatBox.lastElementChild?.scrollIntoView({ behavior: 'smooth', block: 'end' }); }
  function instantScrollToBottom(){ if (!chatBox) return; chatBox.scrollTop = chatBox.scrollHeight; }

  let unreadCount = 0;
  function setUnread(n){ unreadCount = n; if (!scrollUnread) return; if (n > 0) { scrollUnread.style.display = 'inline-block'; scrollUnread.textContent = n; } else { scrollUnread.style.display = 'none'; } }

  if (chatBox && scrollBtn) {
    chatBox.addEventListener('scroll', () => {
      const atBottom = chatBox.scrollHeight - chatBox.scrollTop - chatBox.clientHeight <= 20;
      scrollBtn.style.display = atBottom ? 'none' : 'flex';
      if (atBottom) setUnread(0);
    });
    scrollBtn.addEventListener('click', () => { smoothScrollToBottom(); setUnread(0); scrollBtn.style.display = 'none'; });
  }

  function escapeHtml(text){ if (!text) return ''; return String(text).replace(/[&<>"']/g, (c)=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"})[c]); }

  function renderMessage({ message, sender, sender_image_url, date }, opts = {}){
    if (!chatBox) return;
    const me = sender === window.currentUser;
    const wrapper = document.createElement('div');
    wrapper.className = 'd-flex mb-3 ' + (me ? 'justify-content-end' : 'justify-content-start');
    const avatarImg = sender_image_url ? `<img src="${sender_image_url}" class="avatar ${me ? 'ms-2' : 'me-2'}" alt="${sender}">` : '';
    const time = date ? new Date(date).toLocaleString() : '';
    const bubble = `<div><div class="chat-bubble ${me ? 'me' : ''}">${escapeHtml(message)}</div><div class="msg-meta">${time}</div></div>`;
    if (me) wrapper.innerHTML = bubble + avatarImg; else wrapper.innerHTML = avatarImg + bubble;
    chatBox.appendChild(wrapper);
    if (opts.scroll !== false) { const atBottom = chatBox.scrollHeight - chatBox.scrollTop - chatBox.clientHeight <= 20; if (atBottom) instantScrollToBottom(); else { setUnread(unreadCount + 1); if (scrollBtn) scrollBtn.style.display = 'flex'; } }
  }

  let socket = null; let reconnectAttempts = 0; const maxBackoff = 30000;
  function backoff(attempt){ return Math.min(1000 * Math.pow(2, attempt), maxBackoff) * (0.5 + Math.random() * 0.5); }

  function createSocket(){ if (!window.chatUser) { console.warn('No chatUser, skipping socket creation'); return null; }
    const wsScheme = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const socketUrl = wsScheme + window.location.host + '/ws/direct/' + encodeURIComponent(window.chatUser) + '/';
    console.log('Opening', socketUrl);
    const ws = new WebSocket(socketUrl);
    ws.onopen = () => { console.log('WebSocket open'); reconnectAttempts = 0; instantScrollToBottom(); };
    ws.onmessage = (e) => { try { const data = JSON.parse(e.data); renderMessage(data); } catch(err) { console.error('invalid msg', err); } };
    ws.onerror = (e) => { console.error('WebSocket error', e); };
    ws.onclose = (e) => {
      console.warn('WebSocket closed', e.code, e.reason, 'wasClean', e.wasClean);
      if (e.code && e.code !== 1000) console.warn('WSDISCONNECT', e.code, e.reason);
      reconnectAttempts += 1; const delay = backoff(reconnectAttempts); console.log('Reconnect in', Math.round(delay), 'ms');
      setTimeout(() => { socket = createSocket(); }, delay);
    };
    return ws;
  }

  socket = createSocket();

  function sendMessage(){ const text = (messageInput.value || '').trim(); if (!text) return; const payload = { message: text };
    renderMessage({ message: text, sender: window.currentUser, sender_image_url: '', date: new Date().toISOString() }, { scroll: true });
    if (socket && socket.readyState === WebSocket.OPEN) socket.send(JSON.stringify(payload)); else console.warn('Socket not open, message queued (not implemented)');
    messageInput.value = '';
  }

  if (sendBtn) sendBtn.addEventListener('click', sendMessage);
  if (messageInput) messageInput.addEventListener('keyup', (e) => { if (e.key === 'Enter') sendMessage(); });

  setTimeout(() => { instantScrollToBottom(); }, 120);
})();
