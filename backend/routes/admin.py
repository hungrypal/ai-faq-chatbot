# ============================================================
#  routes/admin.py — /api/admin endpoints
# ============================================================

from flask import Blueprint, request, jsonify
from modules.db import query, execute

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/faqs', methods=['GET'])
def list_faqs():
    """GET /api/admin/faqs"""
    faqs = query("SELECT * FROM faqs ORDER BY category")
    return jsonify(faqs), 200


@admin_bp.route('/faq', methods=['POST'])
def add_faq():
    """POST /api/admin/faq — add a new FAQ"""
    data = request.get_json()
    if not data or 'question' not in data or 'answer' not in data:
        return jsonify({'error': 'question and answer are required'}), 400
    new_id = execute(
        "INSERT INTO faqs (question, answer, category) VALUES (%s, %s, %s)",
        (data['question'], data['answer'], data.get('category', 'general'))
    )
    return jsonify({'id': new_id, 'message': 'FAQ added'}), 201


@admin_bp.route('/faq/<int:faq_id>', methods=['DELETE'])
def delete_faq(faq_id):
    """DELETE /api/admin/faq/<id>"""
    execute("DELETE FROM faqs WHERE id = %s", (faq_id,))
    return jsonify({'message': 'FAQ deleted'}), 200


@admin_bp.route('/products', methods=['POST'])
def add_product():
    """POST /api/admin/products — add a product"""
    d = request.get_json()
    new_id = execute(
        "INSERT INTO products (name, category, price, rating, stock) VALUES (%s,%s,%s,%s,%s)",
        (d['name'], d['category'], d['price'], d.get('rating', 0), d.get('stock', 0))
    )
    return jsonify({'id': new_id, 'message': 'Product added'}), 201


@admin_bp.route('/logs', methods=['GET'])
def chat_logs():
    """GET /api/admin/logs — view recent chat logs"""
    logs = query("SELECT * FROM chat_logs ORDER BY created_at DESC LIMIT 100")
    return jsonify(logs), 200
