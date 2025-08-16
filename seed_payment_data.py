import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db
from src.models.payment import PaymentMethod, Promotion
from src.main import app
from datetime import datetime, timedelta

def seed_payment_data():
    """إضافة بيانات تجريبية لأنظمة الدفع"""
    
    with app.app_context():
        print("🔄 إضافة بيانات أنظمة الدفع...")
        
        # طرق الدفع
        payment_methods = [
            {
                'name': 'stc_pay',
                'display_name': 'STC Pay',
                'is_active': True,
                'fees_percentage': 2.5,
                'gateway_config': {
                    'api_url': 'https://api.stcpay.com.sa',
                    'merchant_id': 'GLOWMIRROR_MERCHANT',
                    'supported_currencies': ['SAR']
                }
            },
            {
                'name': 'apple_pay',
                'display_name': 'Apple Pay',
                'is_active': True,
                'fees_percentage': 2.9,
                'gateway_config': {
                    'merchant_id': 'merchant.com.glowmirror.ar',
                    'supported_currencies': ['SAR', 'USD']
                }
            },
            {
                'name': 'google_pay',
                'display_name': 'Google Pay',
                'is_active': True,
                'fees_percentage': 2.9,
                'gateway_config': {
                    'merchant_id': 'GLOWMIRROR_GOOGLE_PAY',
                    'supported_currencies': ['SAR', 'USD']
                }
            },
            {
                'name': 'credit_card',
                'display_name': 'بطاقة ائتمانية (Visa/Mastercard)',
                'is_active': True,
                'fees_percentage': 3.5,
                'gateway_config': {
                    'supported_cards': ['visa', 'mastercard'],
                    'supported_currencies': ['SAR', 'USD', 'EUR']
                }
            },
            {
                'name': 'mada',
                'display_name': 'مدى',
                'is_active': True,
                'fees_percentage': 1.5,
                'gateway_config': {
                    'network': 'mada',
                    'supported_currencies': ['SAR']
                }
            }
        ]
        
        for method_data in payment_methods:
            existing_method = PaymentMethod.query.filter_by(name=method_data['name']).first()
            if not existing_method:
                method = PaymentMethod(**method_data)
                db.session.add(method)
                print(f"✅ تم إضافة طريقة دفع: {method_data['display_name']}")
        
        # العروض والخصومات
        promotions = [
            {
                'code': 'WELCOME10',
                'name': 'خصم الترحيب',
                'description': 'خصم 10% للمستخدمين الجدد',
                'discount_type': 'percentage',
                'discount_value': 10.0,
                'min_order_amount': 100.0,
                'max_discount_amount': 50.0,
                'usage_limit': 1000,
                'used_count': 0,
                'is_active': True,
                'start_date': datetime.utcnow(),
                'end_date': datetime.utcnow() + timedelta(days=90)
            },
            {
                'code': 'SUMMER25',
                'name': 'عرض الصيف',
                'description': 'خصم 25% على جميع المنتجات',
                'discount_type': 'percentage',
                'discount_value': 25.0,
                'min_order_amount': 200.0,
                'max_discount_amount': 100.0,
                'usage_limit': 500,
                'used_count': 0,
                'is_active': True,
                'start_date': datetime.utcnow(),
                'end_date': datetime.utcnow() + timedelta(days=60)
            },
            {
                'code': 'FREESHIP',
                'name': 'شحن مجاني',
                'description': 'شحن مجاني للطلبات فوق 150 ريال',
                'discount_type': 'fixed_amount',
                'discount_value': 25.0,  # قيمة الشحن
                'min_order_amount': 150.0,
                'max_discount_amount': 25.0,
                'usage_limit': None,  # بلا حدود
                'used_count': 0,
                'is_active': True,
                'start_date': datetime.utcnow(),
                'end_date': datetime.utcnow() + timedelta(days=365)
            },
            {
                'code': 'GLOWMIRROR50',
                'name': 'خصم خاص',
                'description': 'خصم 50 ريال على الطلبات فوق 300 ريال',
                'discount_type': 'fixed_amount',
                'discount_value': 50.0,
                'min_order_amount': 300.0,
                'max_discount_amount': 50.0,
                'usage_limit': 200,
                'used_count': 0,
                'is_active': True,
                'start_date': datetime.utcnow(),
                'end_date': datetime.utcnow() + timedelta(days=30)
            },
            {
                'code': 'EXPIRED',
                'name': 'عرض منتهي الصلاحية',
                'description': 'عرض تجريبي منتهي الصلاحية',
                'discount_type': 'percentage',
                'discount_value': 20.0,
                'min_order_amount': 100.0,
                'max_discount_amount': 40.0,
                'usage_limit': 100,
                'used_count': 0,
                'is_active': True,
                'start_date': datetime.utcnow() - timedelta(days=60),
                'end_date': datetime.utcnow() - timedelta(days=30)
            }
        ]
        
        for promo_data in promotions:
            existing_promo = Promotion.query.filter_by(code=promo_data['code']).first()
            if not existing_promo:
                promotion = Promotion(**promo_data)
                db.session.add(promotion)
                print(f"✅ تم إضافة عرض: {promo_data['name']} ({promo_data['code']})")
        
        db.session.commit()
        print("🎉 تم إضافة جميع بيانات أنظمة الدفع بنجاح!")

if __name__ == '__main__':
    seed_payment_data()

