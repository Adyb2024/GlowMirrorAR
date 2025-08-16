from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.payment import PaymentMethod, PaymentTransaction, ShoppingCart, Promotion, Invoice
from src.models.order import Order, OrderItem
from datetime import datetime, timedelta
import uuid
import hashlib
import hmac

payment_bp = Blueprint('payment', __name__)

class PaymentGateway:
    """فئة محاكاة بوابة الدفع"""
    
    @staticmethod
    def process_stc_pay(amount, phone_number, transaction_id):
        """محاكاة معالجة دفع STC Pay"""
        # في التطبيق الحقيقي، هنا سيتم الاتصال بـ API الخاص بـ STC Pay
        return {
            'success': True,
            'gateway_transaction_id': f"STC_{uuid.uuid4().hex[:12]}",
            'status': 'completed',
            'message': 'Payment processed successfully via STC Pay'
        }
    
    @staticmethod
    def process_apple_pay(amount, payment_token, transaction_id):
        """محاكاة معالجة دفع Apple Pay"""
        return {
            'success': True,
            'gateway_transaction_id': f"APPLE_{uuid.uuid4().hex[:12]}",
            'status': 'completed',
            'message': 'Payment processed successfully via Apple Pay'
        }
    
    @staticmethod
    def process_google_pay(amount, payment_token, transaction_id):
        """محاكاة معالجة دفع Google Pay"""
        return {
            'success': True,
            'gateway_transaction_id': f"GOOGLE_{uuid.uuid4().hex[:12]}",
            'status': 'completed',
            'message': 'Payment processed successfully via Google Pay'
        }
    
    @staticmethod
    def process_credit_card(amount, card_data, transaction_id):
        """محاكاة معالجة دفع البطاقة الائتمانية"""
        return {
            'success': True,
            'gateway_transaction_id': f"CARD_{uuid.uuid4().hex[:12]}",
            'status': 'completed',
            'message': 'Payment processed successfully via Credit Card'
        }
    
    @staticmethod
    def process_mada(amount, card_data, transaction_id):
        """محاكاة معالجة دفع مدى"""
        return {
            'success': True,
            'gateway_transaction_id': f"MADA_{uuid.uuid4().hex[:12]}",
            'status': 'completed',
            'message': 'Payment processed successfully via Mada'
        }

@payment_bp.route('/payment-methods', methods=['GET'])
def get_payment_methods():
    """الحصول على طرق الدفع المتاحة"""
    try:
        methods = PaymentMethod.query.filter_by(is_active=True).all()
        return jsonify({
            'success': True,
            'payment_methods': [method.to_dict() for method in methods]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@payment_bp.route('/checkout', methods=['POST'])
def checkout():
    """بدء عملية الدفع"""
    try:
        data = request.get_json()
        
        required_fields = ['user_id', 'payment_method_id', 'shipping_address']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400
        
        user_id = data['user_id']
        payment_method_id = data['payment_method_id']
        
        # الحصول على السلة
        cart = ShoppingCart.query.filter_by(user_id=user_id).first()
        if not cart or not cart.items:
            return jsonify({
                'success': False,
                'error': 'Cart is empty'
            }), 400
        
        # التحقق من طريقة الدفع
        payment_method = PaymentMethod.query.get(payment_method_id)
        if not payment_method or not payment_method.is_active:
            return jsonify({
                'success': False,
                'error': 'Invalid payment method'
            }), 400
        
        # حساب المبلغ الإجمالي
        subtotal = cart.get_total_amount()
        discount_amount = 0
        
        # تطبيق كود الخصم إذا كان موجوداً
        if 'promotion_code' in data:
            promotion = Promotion.query.filter_by(code=data['promotion_code']).first()
            if promotion:
                is_valid, message = promotion.is_valid()
                if is_valid:
                    discount_amount = promotion.calculate_discount(subtotal)
                    promotion.used_count += 1
                else:
                    return jsonify({
                        'success': False,
                        'error': f'Promotion code error: {message}'
                    }), 400
        
        # حساب الضريبة والشحن
        tax_rate = 0.15  # ضريبة القيمة المضافة 15%
        tax_amount = (subtotal - discount_amount) * tax_rate
        shipping_amount = data.get('shipping_amount', 0)
        
        total_amount = subtotal - discount_amount + tax_amount + shipping_amount
        
        # إنشاء الطلب
        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            shipping_address=data['shipping_address'],
            status='pending'
        )
        db.session.add(order)
        db.session.flush()  # للحصول على order.id
        
        # إضافة عناصر الطلب
        for cart_item in cart.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                color_id=cart_item.color_id,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price
            )
            db.session.add(order_item)
        
        # إنشاء معاملة الدفع
        transaction = PaymentTransaction(
            order_id=order.id,
            payment_method_id=payment_method_id,
            amount=total_amount,
            status='pending'
        )
        db.session.add(transaction)
        
        # إنشاء الفاتورة
        invoice = Invoice(
            order_id=order.id,
            user_id=user_id,
            subtotal=subtotal,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            shipping_amount=shipping_amount,
            total_amount=total_amount,
            status='draft',
            due_date=datetime.utcnow() + timedelta(days=30)
        )
        db.session.add(invoice)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'order_id': order.id,
            'transaction_id': transaction.transaction_id,
            'invoice_id': invoice.id,
            'total_amount': total_amount,
            'currency': 'SAR',
            'payment_method': payment_method.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@payment_bp.route('/process-payment', methods=['POST'])
def process_payment():
    """معالجة الدفع"""
    try:
        data = request.get_json()
        
        if 'transaction_id' not in data:
            return jsonify({
                'success': False,
                'error': 'Transaction ID is required'
            }), 400
        
        # البحث عن المعاملة
        transaction = PaymentTransaction.query.filter_by(
            transaction_id=data['transaction_id']
        ).first()
        
        if not transaction:
            return jsonify({
                'success': False,
                'error': 'Transaction not found'
            }), 404
        
        if transaction.status != 'pending':
            return jsonify({
                'success': False,
                'error': 'Transaction already processed'
            }), 400
        
        # تحديث حالة المعاملة
        transaction.status = 'processing'
        db.session.commit()
        
        # معالجة الدفع حسب طريقة الدفع
        payment_method = transaction.payment_method
        gateway_response = None
        
        try:
            if payment_method.name == 'stc_pay':
                gateway_response = PaymentGateway.process_stc_pay(
                    transaction.amount,
                    data.get('phone_number'),
                    transaction.transaction_id
                )
            elif payment_method.name == 'apple_pay':
                gateway_response = PaymentGateway.process_apple_pay(
                    transaction.amount,
                    data.get('payment_token'),
                    transaction.transaction_id
                )
            elif payment_method.name == 'google_pay':
                gateway_response = PaymentGateway.process_google_pay(
                    transaction.amount,
                    data.get('payment_token'),
                    transaction.transaction_id
                )
            elif payment_method.name == 'credit_card':
                gateway_response = PaymentGateway.process_credit_card(
                    transaction.amount,
                    data.get('card_data'),
                    transaction.transaction_id
                )
            elif payment_method.name == 'mada':
                gateway_response = PaymentGateway.process_mada(
                    transaction.amount,
                    data.get('card_data'),
                    transaction.transaction_id
                )
            else:
                raise Exception(f"Unsupported payment method: {payment_method.name}")
            
            # تحديث المعاملة بناءً على استجابة البوابة
            transaction.gateway_response = gateway_response
            transaction.gateway_transaction_id = gateway_response.get('gateway_transaction_id')
            
            if gateway_response.get('success'):
                transaction.status = 'completed'
                
                # تحديث حالة الطلب
                order = transaction.order
                order.status = 'confirmed'
                order.payment_method = payment_method.name
                
                # تحديث الفاتورة
                invoice = Invoice.query.filter_by(order_id=order.id).first()
                if invoice:
                    invoice.status = 'paid'
                    invoice.paid_date = datetime.utcnow()
                
                # مسح السلة
                cart = ShoppingCart.query.filter_by(user_id=order.user_id).first()
                if cart:
                    for item in cart.items:
                        db.session.delete(item)
                
            else:
                transaction.status = 'failed'
                order = transaction.order
                order.status = 'payment_failed'
            
            db.session.commit()
            
            return jsonify({
                'success': gateway_response.get('success', False),
                'transaction': transaction.to_dict(),
                'message': gateway_response.get('message', 'Payment processing completed')
            }), 200
            
        except Exception as gateway_error:
            # فشل في معالجة الدفع
            transaction.status = 'failed'
            transaction.gateway_response = {'error': str(gateway_error)}
            
            order = transaction.order
            order.status = 'payment_failed'
            
            db.session.commit()
            
            return jsonify({
                'success': False,
                'transaction': transaction.to_dict(),
                'error': f'Payment processing failed: {str(gateway_error)}'
            }), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@payment_bp.route('/transaction/<transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """الحصول على تفاصيل المعاملة"""
    try:
        transaction = PaymentTransaction.query.filter_by(
            transaction_id=transaction_id
        ).first()
        
        if not transaction:
            return jsonify({
                'success': False,
                'error': 'Transaction not found'
            }), 404
        
        return jsonify({
            'success': True,
            'transaction': transaction.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@payment_bp.route('/validate-promotion', methods=['POST'])
def validate_promotion():
    """التحقق من صحة كود الخصم"""
    try:
        data = request.get_json()
        
        if 'code' not in data or 'order_amount' not in data:
            return jsonify({
                'success': False,
                'error': 'Promotion code and order amount are required'
            }), 400
        
        promotion = Promotion.query.filter_by(code=data['code']).first()
        
        if not promotion:
            return jsonify({
                'success': False,
                'error': 'Promotion code not found'
            }), 404
        
        is_valid, message = promotion.is_valid()
        
        if not is_valid:
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        order_amount = data['order_amount']
        discount_amount = promotion.calculate_discount(order_amount)
        
        return jsonify({
            'success': True,
            'promotion': promotion.to_dict(),
            'discount_amount': discount_amount,
            'final_amount': order_amount - discount_amount
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

