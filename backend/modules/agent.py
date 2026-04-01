# ============================================================
#  modules/agent.py — Decision Engine (Core AI Agent)
#  Maps intent → action → response
# ============================================================
from modules.nlp import get_similarity
from modules.db import (
    get_order, get_products_by_category,
    get_all_faqs, log_chat, query
)
FAQ_CONFIDENCE_THRESHOLD = 0.51
# ── Order Status Display Map ──────────────────────────────
STATUS_STEPS = ['placed', 'confirmed', 'shipped', 'delivered']
STATUS_LABEL = {
    'placed':    '📋 Order Placed',
    'confirmed': '✅ Confirmed',
    'shipped':   '🚚 Out for Delivery',
    'delivered': '🏠 Delivered',
    'cancelled': '❌ Cancelled',
    'returned':  '🔄 Return Processed',
}


# ── Main Agent Function ───────────────────────────────────

def process(intent: dict, raw_text: str) -> dict:
    """
    Receives an intent dict, executes the right action,
    and returns a structured response dict for the frontend.

    Response schema:
    {
        'text':       str,          # Main message to show user
        'type':       str,          # 'text' | 'order' | 'products' | 'faq' | 'steps'
        'data':       dict | list,  # Extra data (order, products, etc.)
        'confidence': float,        # Passed through from intent
        'suggestions': list[str]    # Follow-up suggestions
    }
    """
    itype      = intent['type']
    entities   = intent.get('entities', {})
    confidence = intent.get('confidence', 0.0)
    if confidence < 0.5:
        response = _fallback()
    else:
        response = _route(itype, entities, raw_text)
    
    # Only override if not already set
    if 'confidence' not in response:
        response['confidence'] = round(confidence * 100)

    # Log to DB
    log_chat(raw_text, itype, confidence, response.get('text', ''))

    return response


# ── Intent Router ─────────────────────────────────────────

def _route(itype, entities, raw_text):

    if itype == 'greet':
        return _greet()

    if itype == 'track_order':
        return _track_order(entities)

    if itype == 'return_request':
        return _return_info()

    if itype == 'cancel_order':
        return _cancel_info()

    if itype == 'search_products':
        return _search_products(entities)

    if itype == 'compare_products':
        return _compare_guide()

    if itype == 'recommend':
        return _recommend()

    if itype == 'payment_info':
        return _payment_info()

    if itype == 'delivery_info':
        return _delivery_info()

    if itype == 'faq':
        return _faq(raw_text)

    if itype == 'farewell':
        return _farewell()

    return _fallback()


# ── Action Handlers ───────────────────────────────────────

def _greet():
    return {
        'type': 'text',
        'text': "Hey there! 👋 I'm ShopMind AI. I can help you track orders, find products, handle returns, and answer any shopping questions. What do you need today?",
        'suggestions': ['Track my order', 'Show products', 'Return an item', 'FAQs']
    }


def _track_order(entities):
    order_id = entities.get('order_id')

    if not order_id:
        return {
            'type': 'text',
            'text': "Please tell me your order number! For example: <strong>Track order #101</strong>",
            'suggestions': ['Track order #101', 'Track order #102', 'Track order #103']
        }

    order = get_order(order_id)

    if not order:
        return {
            'type': 'text',
            'text': f"I couldn't find an order with ID <strong>#{order_id}</strong>. Please check the order number and try again.",
            'suggestions': ['Track order #101', 'Contact support']
        }

    status  = order['status']
    steps   = STATUS_STEPS if status not in ('cancelled', 'returned') else [status]
    cur_idx = STATUS_STEPS.index(status) if status in STATUS_STEPS else -1

    step_data = []
    for i, s in enumerate(STATUS_STEPS):
        if i < cur_idx:       state = 'done'
        elif i == cur_idx:    state = 'active'
        else:                 state = 'pending'
        step_data.append({'label': STATUS_LABEL[s], 'state': state})

    return {
        'type':    'order',
        'text':    f"Here's the live status of your order <strong>#{order_id}</strong>:",
        'data': {
            'order_id':     order_id,
            'product_name': order['product_name'],
            'status':       status,
            'delivery_date':str(order['delivery_date']),
            'steps':        step_data
        },
        'suggestions': ['Track another order', 'Return this item', 'FAQs']
    }


def _search_products(entities):
    category  = entities.get('category', 'shoes')
    max_price = entities.get('max_price')

    products = get_products_by_category(category, max_price)

    if not products:
        return {
            'type': 'text',
            'text': f"No products found in <strong>{category}</strong>" +
                    (f" under ₹{max_price}" if max_price else "") + ". Try a different search!",
            'suggestions': ['Show all shoes', 'Show headphones', 'Show clothing']
        }

    label = category.title()
    price_note = f" under ₹{max_price}" if max_price else ""

    return {
        'type': 'products',
        'text': f"Here are the best <strong>{label}</strong>{price_note} for you:",
        'data': [
            {
                'id':     p['id'],
                'name':   p['name'],
                'price':  f"₹{int(p['price']):,}",
                'rating': f"⭐ {p['rating']}",
                'stock':  p['stock'],
            }
            for p in products[:4]
        ],
        'suggestions': ['Show more products', 'Compare products', 'Add to cart']
    }


def _return_info():
    return {
        'type': 'steps',
        'text': "No worries! Here's how to return an item 🔄",
        'data': [
            {'icon': '📦', 'label': 'Request return within 7 days of delivery', 'state': 'done'},
            {'icon': '🏷️', 'label': 'Print return label from your orders page', 'state': 'done'},
            {'icon': '🚚', 'label': 'Drop off at nearest courier partner', 'state': 'active'},
            {'icon': '💰', 'label': 'Refund in 3–5 business days', 'state': 'pending'},
        ],
        'suggestions': ['Track my refund', 'Contact support', 'FAQs']
    }


def _cancel_info():
    return {
        'type': 'text',
        'text': "You can cancel your order <strong>within 24 hours</strong> of placing it. After that, the order enters processing and cannot be cancelled — but you can return it after delivery. To cancel, go to <strong>My Orders → Select Order → Cancel</strong>.",
        'suggestions': ['Return instead', 'Track my order', 'Refund policy']
    }


def _compare_guide():
    return {
        'type': 'text',
        'text': "I can compare any two products for you! 🔍 Just tell me which ones, like: <em>'Compare Nike Air Max and Puma Softride'</em> or <em>'Compare Boat Rockerz and JBL Tune'</em>",
        'suggestions': ['Compare Nike and Puma', 'Compare Boat and JBL', 'Show all products']
    }


def _recommend():
    top = query("SELECT * FROM products ORDER BY rating DESC LIMIT 4")
    return {
        'type': 'products',
        'text': "Here are our <strong>top-rated products</strong> right now 🌟",
        'data': [
            {'id': p['id'], 'name': p['name'], 'price': f"₹{int(p['price']):,}", 'rating': f"⭐ {p['rating']}"}
            for p in top
        ],
        'suggestions': ['Filter by category', 'Filter by price', 'Show all products']
    }


def _payment_info():
    return {
        'type': 'text',
        'text': "We accept all major payment methods 💳:<br/><br/>"
                "• <strong>UPI</strong> — GPay, PhonePe, Paytm<br/>"
                "• <strong>Cards</strong> — Visa, Mastercard, Amex<br/>"
                "• <strong>Net Banking</strong> — All major banks<br/>"
                "• <strong>Cash on Delivery</strong> — Orders under ₹5,000<br/>"
                "• <strong>EMI</strong> — 3/6/12 months on orders above ₹2,000",
        'suggestions': ['Is COD available?', 'EMI options', 'Return policy']
    }


def _delivery_info():
    return {
        'type': 'text',
        'text': "Delivery timelines 🚚:<br/><br/>"
                "• <strong>Standard Delivery</strong> — 3–5 business days (Free above ₹499)<br/>"
                "• <strong>Express Delivery</strong> — 1–2 business days (₹99 flat)<br/>"
                "• <strong>Same Day</strong> — Available in select cities (₹199)<br/><br/>"
                "You'll receive tracking updates via SMS and email.",
        'suggestions': ['Track my order', 'COD available?', 'Return policy']
    }


def _faq(raw_text=None):
    faqs = get_all_faqs()

    if not faqs:
        return {
            'type': 'text',
            'text': "No FAQs available right now.",
            'suggestions': ['Track my order', 'Show products']
        }

    # 🧠 NLP MATCHING
    if raw_text:
        questions = [f['question'] for f in faqs]
        scores = get_similarity(raw_text, questions)

        if len(scores) > 0:
            best_index = scores.argmax()
            best_score = float(scores[best_index])

            if best_score > FAQ_CONFIDENCE_THRESHOLD:
                best_faq = faqs[best_index]

                return {
                    'type': 'faq',
                    'text': f"💡 <strong>{best_faq['question']}</strong><br/>{best_faq['answer']}",
                    'confidence': round(best_score * 100, 2),
                    'suggestions': ['Ask another question', 'Track my order']
                }

    # 🔹 fallback: show top FAQs
    faq_html = '<br/><br/>'.join(
        f"<strong>Q: {f['question']}</strong><br/>A: {f['answer']}"
        for f in faqs[:5]
    )

    return {
        'type': 'text',
        'text': f"<strong>Frequently Asked Questions 📋</strong><br/><br/>{faq_html}",
        'suggestions': ['Track my order', 'Return an item']
    }


def _farewell():
    return {
        'type': 'text',
        'text': "Thanks for shopping with us! 🛍️ Have a great day! Feel free to come back anytime you need help.",
        'suggestions': ['Start over', 'Browse products']
    }


def _fallback():
    return {
        'type': 'text',
        'text': "Hmm, I didn't quite get that. 🤔 Could you try rephrasing?",
        'confidence': 40,   # 🔥 force low confidence
        'suggestions': ['Track my order', 'Show products', 'Return item']
    }
