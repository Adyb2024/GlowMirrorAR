from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.product import Product, ProductColor

products_bp = Blueprint('products', __name__)

@products_bp.route('/products', methods=['GET'])
def get_products():
    """Get all products with optional filtering by category"""
    try:
        category = request.args.get('category')
        
        if category:
            products = Product.query.filter_by(category=category).all()
        else:
            products = Product.query.all()
        
        return jsonify({
            'success': True,
            'products': [product.to_dict() for product in products]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID"""
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify({
            'success': True,
            'product': product.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@products_bp.route('/products', methods=['POST'])
def create_product():
    """Create a new product"""
    try:
        data = request.get_json()
        
        product = Product(
            name=data['name'],
            category=data['category'],
            brand=data['brand'],
            price=data['price'],
            description=data.get('description', ''),
            image_url=data.get('image_url', '')
        )
        
        db.session.add(product)
        db.session.commit()
        
        # Add colors if provided
        if 'colors' in data:
            for color_data in data['colors']:
                color = ProductColor(
                    product_id=product.id,
                    color_name=color_data['color_name'],
                    color_hex=color_data['color_hex'],
                    stock_quantity=color_data.get('stock_quantity', 0)
                )
                db.session.add(color)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'product': product.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@products_bp.route('/products/<int:product_id>/colors', methods=['GET'])
def get_product_colors(product_id):
    """Get all colors for a specific product"""
    try:
        product = Product.query.get_or_404(product_id)
        colors = ProductColor.query.filter_by(product_id=product_id).all()
        
        return jsonify({
            'success': True,
            'colors': [color.to_dict() for color in colors]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@products_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all available product categories"""
    try:
        categories = db.session.query(Product.category).distinct().all()
        category_list = [category[0] for category in categories]
        
        return jsonify({
            'success': True,
            'categories': category_list
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

