# ============================================================
#  routes/chat.py — /api/chat endpoint
# ============================================================

from flask import Blueprint, request, jsonify
from modules.intent import detect_intent
from modules.agent  import process

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    POST /api/chat
    Body: { "query": "Track my order 101" }
    Returns: { "text": "...", "type": "order", "data": {...}, "confidence": 99 }
    """
    data = request.get_json()

    if not data or 'query' not in data:
        return jsonify({'error': 'Missing query field'}), 400

    user_query = data['query'].strip()
    if not user_query:
        return jsonify({'error': 'Empty query'}), 400

    # Step 1: Detect intent
    intent = detect_intent(user_query)

    # Step 2: Agent processes intent → response
    response = process(intent, user_query)

    return jsonify(response), 200


@chat_bp.route('/products', methods=['GET'])
def get_products():
    """GET /api/products — list all products"""
    from modules.db import query
    products = query("SELECT * FROM products ORDER BY rating DESC")
    return jsonify(products), 200


@chat_bp.route('/order/<int:order_id>', methods=['GET'])
def get_order_route(order_id):
    """GET /api/order/<id> — get single order"""
    from modules.db import get_order
    order = get_order(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    return jsonify(order), 200
