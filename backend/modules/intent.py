# ============================================================
#  modules/intent.py — Intent Detection Engine (FINAL VERSION)
# ============================================================

import re
from modules.nlp import get_similarity
from config import CONFIDENCE_THRESHOLD


# ── RULE-BASED PATTERNS (FIXED & CLEAN) ────────────────────

RULE_PATTERNS = [
    # 🔹 Track order
    (r'track',                     'track_order', 1),
    (r'where.*order',              'track_order', 1),
    (r'order.*status',             'track_order', 1),
    (r'order[^\w]*#?(\d+)',        'track_order', 1),

    # 🔹 Return / Refund (FIXED)
    (r'return',                    'return_request', 1),
    (r'refund',                    'return_request', 1),
    (r'exchange',                  'return_request', 1),
    (r'send\s+back',               'return_request', 1),
    (r'give\s+back',               'return_request', 1),
    (r'return.*item',              'return_request', 1),

    # 🔹 Cancel order
    (r'cancel.*order',             'cancel_order', 1),
    (r'order.*cancel',             'cancel_order', 1),

    # 🔹 Compare
    (r'compare',                   'compare_products', 1),

    # 🔹 Recommend
    (r'recommend',                 'recommend', 1),
    (r'suggest',                   'recommend', 1),
    (r'what.*buy',                 'recommend', 1),

    # 🔹 Product search (category)
    (r'shoe|sneaker|footwear|boot|sandal', 'search_products', 2),
    (r'headphone|earphone|earbud|speaker|audio', 'search_products', 2),
    (r'cloth|shirt|jeans|top|tshirt|kurta|dress', 'search_products', 2),

    # 🔹 Price filter
    (r'under ₹?(\d+)',             'search_products', 2),
    (r'below ₹?(\d+)',             'search_products', 2),
    (r'less than ₹?(\d+)',         'search_products', 2),

    # 🔹 Greetings
    (r'hello|hi\b|hey|good morning|good evening', 'greet', 3),

    # 🔹 Exit
    (r'bye|goodbye|thanks|thank you', 'farewell', 3),

    # 🔹 FAQ
    (r'faq|help|support|contact', 'faq', 3),

    # 🔹 Payment
    (r'payment|upi|cod|card', 'payment_info', 3),

    # 🔹 Delivery
    (r'deliver.*time|shipping time|how long.*deliver', 'delivery_info', 3),
]


# ── NLP CORPUS (SMART UNDERSTANDING) ──────────────────────

NLP_CORPUS = {
    'track_order': [
        'track my order', 'where is my order', 'order status',
        'delivery update', 'track shipment'
    ],

    'return_request': [
        'return product', 'want refund', 'send item back',
        'send back my product', 'give back item',
        'return my order', 'exchange product'
    ],

    'cancel_order': [
        'cancel my order', 'stop my order'
    ],

    'search_products': [
        'show me products', 'find items', 'browse catalog',
        'search for goods', 'show shoes', 'best headphones'
    ],

    'compare_products': [
        'compare two products', 'which is better',
        'difference between products'
    ],

    'recommend': [
        'recommend something', 'suggest products',
        'what should I buy'
    ],

    'payment_info': [
        'how to pay', 'payment methods', 'upi cod card'
    ],

    'delivery_info': [
        'delivery time', 'how long shipping',
        'estimated delivery'
    ],

    'faq': [
        'frequently asked questions', 'help center'
    ],

    'greet': [
        'hello', 'hi there', 'good morning'
    ],
}


# ── Flatten corpus ────────────────────────────────────────

_corpus_labels = []
_corpus_phrases = []

for label, phrases in NLP_CORPUS.items():
    for phrase in phrases:
        _corpus_labels.append(label)
        _corpus_phrases.append(phrase)


# ── MAIN FUNCTION ─────────────────────────────────────────

def detect_intent(text: str) -> dict:

    lower = text.lower()

    # 🔹 1. RULE MATCHING
    for pattern, intent_type, priority in sorted(RULE_PATTERNS, key=lambda x: x[2]):
        if re.search(pattern, lower):
            return {
                'type': intent_type,
                'confidence': 0.95,
                'entities': _extract_entities(lower, intent_type),
                'method': 'rule'
            }

    # 🔹 2. NLP FALLBACK
    scores = get_similarity(text, _corpus_phrases)

    if len(scores) > 0:
        best_idx = int(scores.argmax())
        best_score = float(scores[best_idx])

        if best_score >= CONFIDENCE_THRESHOLD:
            intent_type = _corpus_labels[best_idx]

            return {
                'type': intent_type,
                'confidence': round(best_score, 3),
                'entities': _extract_entities(lower, intent_type),
                'method': 'nlp'
            }

    # 🔹 3. FALLBACK
    return {
        'type': 'unknown',
        'confidence': 0.0,
        'entities': {},
        'method': 'fallback'
    }


# ── ENTITY EXTRACTION ─────────────────────────────────────

def _extract_entities(text: str, intent_type: str) -> dict:

    entities = {}

    # 🔹 Order ID
    if intent_type == 'track_order':
        m = re.search(r'#?(\d+)', text)
        if m:
            entities['order_id'] = int(m.group(1))

    # 🔹 Price
    price_match = re.search(
        r'under\s*₹?\s*(\d+)|below\s*₹?\s*(\d+)|less.*?(\d+)', text
    )

    if price_match:
        val = next(g for g in price_match.groups() if g)
        entities['max_price'] = int(val)

    # 🔹 Category
    cat_map = {
        'shoes': ['shoe', 'sneaker', 'footwear', 'boot', 'sandal'],
        'headphones': ['headphone', 'earphone', 'earbud', 'speaker', 'audio'],
        'clothing': ['shirt', 'jeans', 'top', 'tshirt', 'cloth', 'kurta', 'dress'],
    }

    for cat, keywords in cat_map.items():
        if any(kw in text for kw in keywords):
            entities['category'] = cat
            break

    return entities