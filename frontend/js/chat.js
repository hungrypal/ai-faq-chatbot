// ============================================================
//  js/chat.js — Chat UI Logic
//  Handles: rendering messages, product cards, order cards,
//           typing animation, suggestions, screen transitions
// ============================================================

// ── Constants ─────────────────────────────────────────────
const DEFAULT_SUGGESTIONS = [
  '📦 Track order #101',
  '👟 Shoes under ₹2000',
  '🔄 Return an item',
  '⚡ Compare products',
  '🎧 Best headphones',
  '💳 Refund status',
];

const PRODUCT_EMOJIS = {
  shoes:      ['👟','👠','🥿','👞'],
  headphones: ['🎧','🎵','🔊','🎤'],
  clothing:   ['👕','👖','👗','🧥'],
  default:    ['🛍️','📦','⭐','🏷️'],
};

// ── DOM References ────────────────────────────────────────
const welcomeScreen = document.getElementById('welcomeScreen');
const chatScreen    = document.getElementById('chatScreen');
const messagesEl    = document.getElementById('messages');
const chatInput     = document.getElementById('chatInput');
const suggestBar    = document.getElementById('suggestBar');
const startBtn      = document.getElementById('startBtn');
const sendBtn       = document.getElementById('sendBtn');
const resetBtn      = document.getElementById('resetBtn');

// ── Init ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  renderSuggestions(DEFAULT_SUGGESTIONS);

  startBtn.addEventListener('click', startChat);
  resetBtn.addEventListener('click', resetChat);
  sendBtn.addEventListener('click',  sendMessage);

  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
  chatInput.addEventListener('input', autoResize);
});

// ── Screen Transitions ────────────────────────────────────
function startChat() {
  welcomeScreen.classList.add('hidden');
  chatScreen.classList.add('active');
  addSectionLabel('Today');
  addBotWelcome();
}

function resetChat() {
  chatScreen.classList.remove('active');
  welcomeScreen.classList.remove('hidden');
  messagesEl.innerHTML = '';
  chatInput.value = '';
  chatInput.style.height = '';
  renderSuggestions(DEFAULT_SUGGESTIONS);
}

// ── Suggestion Chips ──────────────────────────────────────
function renderSuggestions(suggestions) {
  suggestBar.innerHTML = '';
  suggestions.forEach(text => {
    const chip = document.createElement('span');
    chip.className = 'suggest-chip';
    chip.textContent = text;
    chip.addEventListener('click', () => {
      const clean = text.replace(/^[\p{Emoji}\s]+/u, '').trim();
      addUserMessage(clean);
      handleSend(clean);
    });
    suggestBar.appendChild(chip);
  });
}

// ── Send Flow ─────────────────────────────────────────────
function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;
  chatInput.value = '';
  chatInput.style.height = '';
  addUserMessage(text);
  handleSend(text);
}

async function handleSend(text) {
  showTyping();

  try {
    // Try Flask backend first; fall back to demo if unavailable
    let response;
    try {
      response = await sendQueryToBackend(text);
    } catch (_) {
      // Backend not running — use demo mode
      await sleep(700 + Math.random() * 500);
      response = demoResponse(text);
    }

    removeTyping();
    renderBotResponse(response);

    // Update suggestion chips with contextual options
    if (response.suggestions && response.suggestions.length) {
      renderSuggestions(response.suggestions);
    }

  } catch (err) {
    removeTyping();
    addBotText("Oops! Something went wrong. Please try again. 🙏", 0);
    console.error('Chat error:', err);
  }
}

// ── Response Renderer ─────────────────────────────────────
function renderBotResponse(res) {
  switch (res.type) {
    case 'order':    renderOrderCard(res);    break;
    case 'products': renderProductCards(res); break;
    case 'steps':    renderStepsCard(res);    break;
    default:         renderTextMessage(res);  break;
  }
}

// ── Text Message ──────────────────────────────────────────
function renderTextMessage(res) {
  const row = createBotRow();
  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.innerHTML = res.text || '';
  row.group.appendChild(bubble);
  appendConfidence(row.group, res.confidence);
  finishBotRow(row);
}

// Alias used by welcome message
function addBotText(html, confidence = 97) {
  renderBotResponse({ type: 'text', text: html, confidence });
}

// ── Order Card ────────────────────────────────────────────
function renderOrderCard(res) {
  const row = createBotRow();

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.innerHTML = res.text || '';
  row.group.appendChild(bubble);

  if (res.data) {
    const d = res.data;
    const statusBadgeClass =
      d.status === 'delivered' ? 'badge-delivered' :
      d.status === 'placed'    ? 'badge-placed'    : 'badge-transit';
    const statusLabel =
      d.status === 'delivered' ? '✅ Delivered' :
      d.status === 'placed'    ? '📋 Placed'    : '🚚 In Transit';

    const card = document.createElement('div');
    card.className = 'order-card';
    card.innerHTML = `
      <div class="order-header">
        <div>
          <div style="font-size:13px;font-weight:600">${d.product_name}</div>
          <div class="order-id">Order #${d.order_id} · Est. ${formatDate(d.delivery_date)}</div>
        </div>
        <span class="order-badge ${statusBadgeClass}">${statusLabel}</span>
      </div>
      <div class="order-steps">
        ${(d.steps || []).map(s => `
          <div class="step ${s.state}">
            <div class="step-icon">${s.label.split(' ')[0]}</div>
            <div class="step-label">${s.label.replace(/^\S+\s/,'')}</div>
          </div>`).join('')}
      </div>`;
    row.group.appendChild(card);
  }

  appendConfidence(row.group, res.confidence);
  finishBotRow(row);
}

// ── Product Cards ─────────────────────────────────────────
function renderProductCards(res) {
  const row = createBotRow();

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.innerHTML = res.text || '';
  row.group.appendChild(bubble);

  if (res.data && res.data.length) {
    const cards = document.createElement('div');
    cards.className = 'product-cards';

    res.data.forEach((p, i) => {

      // 🧠 Smart emoji based on name/category
      let category = 'default';
      if (p.name.toLowerCase().includes('shoe')) category = 'shoes';
      if (p.name.toLowerCase().includes('headphone')) category = 'headphones';
      if (p.name.toLowerCase().includes('jeans') || p.name.toLowerCase().includes('shirt')) category = 'clothing';

      const emojis = PRODUCT_EMOJIS[category] || PRODUCT_EMOJIS.default;
      const emoji  = emojis[i % emojis.length];

      const card = document.createElement('div');
      card.className = 'product-card';

      card.innerHTML = `
        <div class="product-img">${emoji}</div>

        <div class="product-info">
          <div class="product-name">${p.name}</div>
          <div class="product-meta">
            <span class="product-price">${p.price}</span>
            <span class="product-rating">${p.rating}</span>
          </div>
        </div>

        <button class="add-btn" onclick="addToCart('${p.name}')">
          Add 🛒
        </button>
      `;

      cards.appendChild(card);
    });

    row.group.appendChild(cards);
  }

  appendConfidence(row.group, res.confidence);
  finishBotRow(row);
}

// ── Steps Card (return/refund workflow) ───────────────────
function renderStepsCard(res) {
  const row = createBotRow();

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.innerHTML = res.text || '';
  row.group.appendChild(bubble);

  if (res.data && res.data.length) {
    const card = document.createElement('div');
    card.className = 'order-card';
    card.innerHTML = `
      <div class="order-steps">
        ${res.data.map(s => `
          <div class="step ${s.state}">
            <div class="step-icon">${s.icon}</div>
            <div class="step-label">${s.label}</div>
          </div>`).join('')}
      </div>`;
    row.group.appendChild(card);
  }

  appendConfidence(row.group, res.confidence);
  finishBotRow(row);
}

// ── Typing Indicator ──────────────────────────────────────
function showTyping() {
  const row = document.createElement('div');
  row.className = 'msg bot';
  row.id = 'typingRow';
  row.innerHTML = `
    <div class="msg-avatar">🤖</div>
    <div class="typing-indicator">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>`;
  messagesEl.appendChild(row);
  scrollBottom();
}

function removeTyping() {
  const t = document.getElementById('typingRow');
  if (t) t.remove();
}

// ── User Message ──────────────────────────────────────────
function addUserMessage(text) {
  const row = document.createElement('div');
  row.className = 'msg user';
  row.innerHTML = `
    <div class="msg-avatar">👤</div>
    <div class="bubble">${escapeHtml(text)}</div>
    <div class="msg-time">${getTime()}</div>`;
  messagesEl.appendChild(row);
  scrollBottom();
}

// ── Bot Row Helpers ───────────────────────────────────────
function createBotRow() {
  const row   = document.createElement('div');
  row.className = 'msg bot';
  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.textContent = '🤖';
  const group = document.createElement('div');
  group.className = 'msg-group';
  row.appendChild(avatar);
  row.appendChild(group);
  return { row, group };
}

function finishBotRow({ row, group }) {
  const time = document.createElement('div');
  time.className = 'msg-time';
  time.textContent = getTime();
  row.appendChild(time);
  messagesEl.appendChild(row);
  scrollBottom();
}

function appendConfidence(group, confidence) {
  if (confidence == null) return;
  const conf = document.createElement('div');
  conf.className = 'confidence';
  conf.innerHTML = `
    <span>Confidence</span>
    <div class="conf-bar"><div class="conf-fill" style="width:${confidence}%"></div></div>
    <span>${confidence}%</span>`;
  group.appendChild(conf);
}

// ── Welcome Message ───────────────────────────────────────
function addBotWelcome() {
  addBotText(
    "Hey there! 👋 I'm <strong>ShopMind AI</strong> — your personal shopping assistant.<br/><br/>" +
    "I can <strong>track orders</strong>, <strong>find products</strong>, handle <strong>returns & refunds</strong>, " +
    "and answer any shopping questions. What can I do for you today?",
    97
  );
}

// ── Section Label ─────────────────────────────────────────
function addSectionLabel(text) {
  const el = document.createElement('div');
  el.className = 'section-label';
  el.textContent = text;
  messagesEl.appendChild(el);
}

// ── Cart Action ───────────────────────────────────────────
function addToCart(productName) {
  addUserMessage(`Add ${productName} to cart`);
  handleSend(`Add ${productName} to cart`);
}

// ── Utils ─────────────────────────────────────────────────
function scrollBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function getTime() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function formatDate(dateStr) {
  if (!dateStr) return 'TBD';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

function escapeHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function autoResize(e) {
  e.target.style.height = 'auto';
  e.target.style.height = Math.min(e.target.scrollHeight, 100) + 'px';
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
