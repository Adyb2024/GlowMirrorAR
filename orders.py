from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.order import Order, OrderItem
from src.models.product import Product, ProductColor

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/orders', methods=['POST'])
def create_order():
    """Create a new order"""
    try:
        data = request.get_json()
        
        # Create the order
        order = Order(
            user_id=data['user_id'],
            total_amount=data['total_amount'],
            payment_method=data.get('payment_method'),
            shipping_address=data.get('shipping_address')
        )
        
        db.session.add(order)
        db.session.flush()  # Get the order ID
        
        # Add order items
        for item_data in data['items']:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data['product_id'],
                color_id=item_data['color_id'],
                quantity=item_data.get('quantity', 1),
                unit_price=item_data['unit_price']
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'order': order.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get a specific order by ID"""
    try:
        order = Order.query.get_or_404(order_id)
        return jsonify({
            'success': True,
            'order': order.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@orders_bp.route('/users/<int:user_id>/orders', methods=['GET'])
def get_user_orders(user_id):
    """Get all orders for a specific user"""
    try:
        orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
        return jsonify({
            'success': True,
            'orders': [order.to_dict() for order in orders]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@orders_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Update order status"""
    try:
        data = request.get_json()
        order = Order.query.get_or_404(order_id)
        
        order.status = data['status']
        db.session.commit()
        
        return jsonify({
            'success': True,
            'order': order.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@orders_bp.route('/orders/<int:order_id>', methods=['DELETE'])
def cancel_order(order_id):
    """Cancel an order (set status to cancelled)"""
    try:
        order = Order.query.get_or_404(order_id)
        
        if order.status in ['pending', 'confirmed']:
            order.status = 'cancelled'
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Order cancelled successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Order cannot be cancelled in current status'
            }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

