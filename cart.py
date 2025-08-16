from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.payment import ShoppingCart, CartItem
from src.models.product import Product, ProductColor

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    """الحصول على سلة التسوق للمستخدم"""
    try:
        cart = ShoppingCart.query.filter_by(user_id=user_id).first()
        
        if not cart:
            # إنشاء سلة جديدة إذا لم تكن موجودة
            cart = ShoppingCart(user_id=user_id)
            db.session.add(cart)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'cart': cart.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cart_bp.route('/cart/<int:user_id>/add', methods=['POST'])
def add_to_cart(user_id):
    """إضافة منتج إلى السلة"""
    try:
        data = request.get_json()
        
        if 'product_id' not in data or 'color_id' not in data:
            return jsonify({
                'success': False,
                'error': 'Product ID and Color ID are required'
            }), 400
        
        # التحقق من وجود المنتج واللون
        product = Product.query.get(data['product_id'])
        if not product:
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
        
        color = ProductColor.query.get(data['color_id'])
        if not color or color.product_id != product.id:
            return jsonify({
                'success': False,
                'error': 'Color not found or does not belong to this product'
            }), 404
        
        # الحصول على السلة أو إنشاؤها
        cart = ShoppingCart.query.filter_by(user_id=user_id).first()
        if not cart:
            cart = ShoppingCart(user_id=user_id)
            db.session.add(cart)
            db.session.flush()
        
        # التحقق من وجود العنصر في السلة
        existing_item = CartItem.query.filter_by(
            cart_id=cart.id,
            product_id=data['product_id'],
            color_id=data['color_id']
        ).first()
        
        quantity = data.get('quantity', 1)
        
        if existing_item:
            # تحديث الكمية
            existing_item.quantity += quantity
        else:
            # إضافة عنصر جديد
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=data['product_id'],
                color_id=data['color_id'],
                quantity=quantity
            )
            db.session.add(cart_item)
        
        db.session.commit()
        
        # إعادة تحميل السلة مع العناصر المحدثة
        cart = ShoppingCart.query.get(cart.id)
        
        return jsonify({
            'success': True,
            'message': 'Product added to cart successfully',
            'cart': cart.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cart_bp.route('/cart/<int:user_id>/update/<int:item_id>', methods=['PUT'])
def update_cart_item(user_id, item_id):
    """تحديث كمية عنصر في السلة"""
    try:
        data = request.get_json()
        
        if 'quantity' not in data:
            return jsonify({
                'success': False,
                'error': 'Quantity is required'
            }), 400
        
        quantity = data['quantity']
        if quantity < 0:
            return jsonify({
                'success': False,
                'error': 'Quantity cannot be negative'
            }), 400
        
        # البحث عن العنصر
        cart_item = CartItem.query.join(ShoppingCart).filter(
            CartItem.id == item_id,
            ShoppingCart.user_id == user_id
        ).first()
        
        if not cart_item:
            return jsonify({
                'success': False,
                'error': 'Cart item not found'
            }), 404
        
        if quantity == 0:
            # حذف العنصر إذا كانت الكمية صفر
            db.session.delete(cart_item)
        else:
            # تحديث الكمية
            cart_item.quantity = quantity
        
        db.session.commit()
        
        # إعادة تحميل السلة
        cart = ShoppingCart.query.filter_by(user_id=user_id).first()
        
        return jsonify({
            'success': True,
            'message': 'Cart item updated successfully',
            'cart': cart.to_dict() if cart else None
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cart_bp.route('/cart/<int:user_id>/remove/<int:item_id>', methods=['DELETE'])
def remove_from_cart(user_id, item_id):
    """حذف عنصر من السلة"""
    try:
        # البحث عن العنصر
        cart_item = CartItem.query.join(ShoppingCart).filter(
            CartItem.id == item_id,
            ShoppingCart.user_id == user_id
        ).first()
        
        if not cart_item:
            return jsonify({
                'success': False,
                'error': 'Cart item not found'
            }), 404
        
        db.session.delete(cart_item)
        db.session.commit()
        
        # إعادة تحميل السلة
        cart = ShoppingCart.query.filter_by(user_id=user_id).first()
        
        return jsonify({
            'success': True,
            'message': 'Item removed from cart successfully',
            'cart': cart.to_dict() if cart else None
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cart_bp.route('/cart/<int:user_id>/clear', methods=['DELETE'])
def clear_cart(user_id):
    """مسح جميع عناصر السلة"""
    try:
        cart = ShoppingCart.query.filter_by(user_id=user_id).first()
        
        if cart:
            # حذف جميع العناصر
            CartItem.query.filter_by(cart_id=cart.id).delete()
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cart cleared successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cart_bp.route('/cart/<int:user_id>/summary', methods=['GET'])
def get_cart_summary(user_id):
    """الحصول على ملخص السلة"""
    try:
        cart = ShoppingCart.query.filter_by(user_id=user_id).first()
        
        if not cart:
            return jsonify({
                'success': True,
                'summary': {
                    'total_items': 0,
                    'total_amount': 0,
                    'currency': 'SAR'
                }
            }), 200
        
        summary = {
            'total_items': cart.get_total_items(),
            'total_amount': cart.get_total_amount(),
            'currency': 'SAR',
            'items_count': len(cart.items)
        }
        
        return jsonify({
            'success': True,
            'summary': summary
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

