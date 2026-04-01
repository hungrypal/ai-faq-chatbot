// ============================================================
//  js/api.js — Flask API Communication Layer
//  All fetch() calls to the backend live here.
// ============================================================

const API_BASE = 'http://localhost:5000/api';

/**
 * Send a user query to the Flask backend.
 * Returns the parsed JSON response from the agent.
 */
async function sendQueryToBackend(query) {
  const response = await fetch(`${API_BASE}/chat`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ query }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}

/**
 * Fetch all products (optional — for product browsing page).
 */
async function fetchProducts() {
  const res = await fetch(`${API_BASE}/products`);
  return res.json();
}

/**
 * Fetch a single order by ID.
 */
async function fetchOrder(orderId) {
  const res = await fetch(`${API_BASE}/order/${orderId}`);
  if (!res.ok) return null;
  return res.json();
}

// ── DEMO MODE ─────────────────────────────────────────────
// When Flask is not running, this function provides offline responses.
// Remove this and use sendQueryToBackend() once your backend is running.

function demoResponse(text) {
  const t = text.toLowerCase();

  if (/track|order.*\d+|#\d+/.test(t)) {
    const id = (t.match(/\d+/) || ['101'])[0];
    return {
      type: 'order', confidence: 99,
      text: `Here's your order <strong>#${id}</strong>:`,
      data: {
        order_id: id, product_name: 'Nike Air Max 270',
        status: 'shipped', delivery_date: '2026-03-27',
        steps: [
          { label: '📋 Order Placed',     state: 'done'    },
          { label: '✅ Confirmed',         state: 'done'    },
          { label: '🚚 Out for Delivery',  state: 'active'  },
          { label: '🏠 Delivered',         state: 'pending' },
        ]
      },
      suggestions: ['Track another order', 'Return this item']
    };
  }
  if (/shoe|sneaker/.test(t)) {
    return {
      type: 'products', confidence: 94,
      text: 'Here are top <strong>Shoes</strong> for you:',
      data: [
        { id:1, name:'Nike Air Max 270',  price:'₹1,899', rating:'⭐ 4.7' },
        { id:2, name:'Puma Softride Enzo',price:'₹1,499', rating:'⭐ 4.5' },
        { id:3, name:'Skechers Go Walk 6',price:'₹1,750', rating:'⭐ 4.4' },
      ],
      suggestions: ['Filter by price', 'Show headphones']
    };
  }
  if (/headphone|earphone/.test(t)) {
    return {
      type: 'products', confidence: 94,
      text: 'Here are top <strong>Headphones</strong>:',
      data: [
        { id:4, name:'Boat Rockerz 550', price:'₹1,299', rating:'⭐ 4.6' },
        { id:5, name:'Sony WH-CH720N',   price:'₹7,990', rating:'⭐ 4.8' },
        { id:6, name:'JBL Tune 510BT',   price:'₹1,899', rating:'⭐ 4.5' },
      ],
      suggestions: ['Compare Boat and JBL', 'Show shoes']
    };
  }
  if (/return|refund/.test(t)) {
    return {
      type: 'steps', confidence: 96,
      text: "Here's the return process 🔄",
      data: [
        { icon:'📦', label:'Request return within 7 days',  state:'done'    },
        { icon:'🏷️', label:'Print return label',            state:'done'    },
        { icon:'🚚', label:'Drop at courier partner',       state:'active'  },
        { icon:'💰', label:'Refund in 3–5 business days',   state:'pending' },
      ],
      suggestions: ['Track refund', 'Contact support']
    };
  }
  if (/hello|hi|hey/.test(t)) {
    return {
      type: 'text', confidence: 95,
      text: "Hello! 👋 I'm <strong>ShopMind AI</strong>. How can I help you today?",
      suggestions: ['Track my order', 'Show products', 'Return item', 'FAQs']
    };
  }
  return {
    type: 'text', confidence: 60,
    text: "I didn't quite get that. Try: <em>Track order #101</em>, <em>Show shoes</em>, or <em>Return item</em> 🛍️",
    suggestions: ['Track order #101', 'Show products', 'FAQs']
  };
}
