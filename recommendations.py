from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.product import Product, ProductColor
from src.models.gallery import UserPreference, SavedLook
from src.models.order import Order, OrderItem
import random

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/users/<int:user_id>/recommendations', methods=['GET'])
def get_recommendations(user_id):
    """Get personalized product recommendations for a user"""
    try:
        # Get user preferences
        preferences = UserPreference.query.filter_by(user_id=user_id).first()
        
        # Get user's order history
        orders = Order.query.filter_by(user_id=user_id).all()
        purchased_products = []
        for order in orders:
            for item in order.items:
                purchased_products.append(item.product_id)
        
        # Get user's saved looks
        saved_looks = SavedLook.query.filter_by(user_id=user_id).all()
        
        # Base query for products
        query = Product.query
        
        # Filter by preferred categories if available
        if preferences and preferences.preferred_categories:
            query = query.filter(Product.category.in_(preferences.preferred_categories))
        
        # Filter by budget range if available
        if preferences and preferences.budget_range:
            if preferences.budget_range == 'low':
                query = query.filter(Product.price <= 100)
            elif preferences.budget_range == 'medium':
                query = query.filter(Product.price.between(100, 300))
            elif preferences.budget_range == 'high':
                query = query.filter(Product.price >= 300)
        
        # Exclude already purchased products
        if purchased_products:
            query = query.filter(~Product.id.in_(purchased_products))
        
        # Get products
        products = query.limit(20).all()
        
        # If we have user's favorite colors, prioritize products with similar colors
        if preferences and preferences.favorite_colors:
            products_with_colors = []
            for product in products:
                for color in product.colors:
                    if color.color_hex in preferences.favorite_colors:
                        products_with_colors.append(product)
                        break
            
            # Mix prioritized products with others
            other_products = [p for p in products if p not in products_with_colors]
            products = products_with_colors + other_products[:10]
        
        # Shuffle for variety
        random.shuffle(products)
        
        return jsonify({
            'success': True,
            'recommendations': [product.to_dict() for product in products[:10]]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@recommendations_bp.route('/users/<int:user_id>/trending', methods=['GET'])
def get_trending_products(user_id):
    """Get trending products based on overall popularity"""
    try:
        # Get most ordered products
        popular_products = db.session.query(
            Product,
            db.func.count(OrderItem.product_id).label('order_count')
        ).join(
            OrderItem, Product.id == OrderItem.product_id
        ).group_by(
            Product.id
        ).order_by(
            db.func.count(OrderItem.product_id).desc()
        ).limit(10).all()
        
        trending_list = []
        for product, count in popular_products:
            product_dict = product.to_dict()
            product_dict['order_count'] = count
            trending_list.append(product_dict)
        
        return jsonify({
            'success': True,
            'trending': trending_list
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@recommendations_bp.route('/users/<int:user_id>/similar-looks', methods=['GET'])
def get_similar_looks(user_id):
    """Get looks similar to user's saved looks"""
    try:
        # Get user's saved looks
        user_looks = SavedLook.query.filter_by(user_id=user_id).all()
        
        if not user_looks:
            return jsonify({
                'success': True,
                'similar_looks': []
            }), 200
        
        # Extract products used in user's looks
        user_products = set()
        for look in user_looks:
            if look.products_used:
                for product in look.products_used:
                    if 'product_id' in product:
                        user_products.add(product['product_id'])
        
        # Find other users' looks that use similar products
        similar_looks = []
        if user_products:
            all_looks = SavedLook.query.filter(SavedLook.user_id != user_id).all()
            
            for look in all_looks:
                if look.products_used:
                    look_products = set()
                    for product in look.products_used:
                        if 'product_id' in product:
                            look_products.add(product['product_id'])
                    
                    # Check for overlap
                    overlap = user_products.intersection(look_products)
                    if len(overlap) > 0:
                        look_dict = look.to_dict()
                        look_dict['similarity_score'] = len(overlap) / len(user_products.union(look_products))
                        similar_looks.append(look_dict)
        
        # Sort by similarity score
        similar_looks.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return jsonify({
            'success': True,
            'similar_looks': similar_looks[:10]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@recommendations_bp.route('/colors/recommendations', methods=['POST'])
def get_color_recommendations():
    """Get color recommendations based on skin tone"""
    try:
        data = request.get_json()
        skin_tone = data.get('skin_tone', 'medium')
        
        # Color recommendations based on skin tone
        color_recommendations = {
            'light': {
                'lipstick': ['#ff6b9d', '#ff7675', '#fd79a8'],
                'eyeshadow': ['#a55eea', '#3742fa', '#ff6348'],
                'blush': ['#ff9ff3', '#ff6b9d', '#fd79a8']
            },
            'medium': {
                'lipstick': ['#ff4757', '#c44569', '#f8b500'],
                'eyeshadow': ['#2f3542', '#ff6348', '#ff9ff3'],
                'blush': ['#ff7675', '#fd79a8', '#e84393']
            },
            'dark': {
                'lipstick': ['#c44569', '#8b0000', '#ff4757'],
                'eyeshadow': ['#2f3542', '#8b4513', '#ff6348'],
                'blush': ['#e84393', '#ff7675', '#c44569']
            }
        }
        
        recommendations = color_recommendations.get(skin_tone, color_recommendations['medium'])
        
        return jsonify({
            'success': True,
            'color_recommendations': recommendations
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

