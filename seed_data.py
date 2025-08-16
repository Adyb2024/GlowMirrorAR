import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db, User
from src.models.product import Product, ProductColor
from src.models.gallery import UserPreference
from src.main import app

def seed_database():
    """Add sample data to the database"""
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create sample users
        user1 = User(username='sara_beauty', email='sara@example.com')
        user2 = User(username='noor_makeup', email='noor@example.com')
        
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        
        # Create sample products
        products_data = [
            {
                'name': 'أحمر شفاه مات',
                'category': 'lipstick',
                'brand': 'GlowBeauty',
                'price': 89.0,
                'description': 'أحمر شفاه مات طويل الثبات',
                'colors': [
                    {'color_name': 'وردي كلاسيكي', 'color_hex': '#ff6b9d', 'stock_quantity': 50},
                    {'color_name': 'أحمر جريء', 'color_hex': '#ff4757', 'stock_quantity': 30},
                    {'color_name': 'بنفسجي عميق', 'color_hex': '#c44569', 'stock_quantity': 25}
                ]
            },
            {
                'name': 'ظل عيون لامع',
                'category': 'eyeshadow',
                'brand': 'GlowBeauty',
                'price': 129.0,
                'description': 'ظل عيون لامع بألوان متنوعة',
                'colors': [
                    {'color_name': 'ذهبي', 'color_hex': '#f8b500', 'stock_quantity': 40},
                    {'color_name': 'بنفسجي', 'color_hex': '#a55eea', 'stock_quantity': 35},
                    {'color_name': 'أزرق', 'color_hex': '#3742fa', 'stock_quantity': 20}
                ]
            },
            {
                'name': 'بلاشر طبيعي',
                'category': 'blush',
                'brand': 'GlowBeauty',
                'price': 79.0,
                'description': 'بلاشر بلمسة طبيعية',
                'colors': [
                    {'color_name': 'خوخي', 'color_hex': '#ff7675', 'stock_quantity': 60},
                    {'color_name': 'وردي فاتح', 'color_hex': '#ff9ff3', 'stock_quantity': 45},
                    {'color_name': 'كورالي', 'color_hex': '#fd79a8', 'stock_quantity': 30}
                ]
            }
        ]
        
        for product_data in products_data:
            product = Product(
                name=product_data['name'],
                category=product_data['category'],
                brand=product_data['brand'],
                price=product_data['price'],
                description=product_data['description']
            )
            db.session.add(product)
            db.session.flush()  # Get the product ID
            
            # Add colors
            for color_data in product_data['colors']:
                color = ProductColor(
                    product_id=product.id,
                    color_name=color_data['color_name'],
                    color_hex=color_data['color_hex'],
                    stock_quantity=color_data['stock_quantity']
                )
                db.session.add(color)
        
        # Create sample user preferences
        pref1 = UserPreference(
            user_id=1,
            skin_tone='medium',
            preferred_categories=['lipstick', 'blush'],
            favorite_colors=['#ff6b9d', '#ff7675'],
            budget_range='medium'
        )
        
        pref2 = UserPreference(
            user_id=2,
            skin_tone='light',
            preferred_categories=['eyeshadow', 'lipstick'],
            favorite_colors=['#a55eea', '#f8b500'],
            budget_range='high'
        )
        
        db.session.add(pref1)
        db.session.add(pref2)
        
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()

