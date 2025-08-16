from src.models.user import db
from datetime import datetime

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # lipstick, eyeshadow, blush
    brand = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with colors
    colors = db.relationship('ProductColor', backref='product', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Product {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'brand': self.brand,
            'price': self.price,
            'description': self.description,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'colors': [color.to_dict() for color in self.colors]
        }

class ProductColor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    color_name = db.Column(db.String(50), nullable=False)
    color_hex = db.Column(db.String(7), nullable=False)  # #RRGGBB format
    stock_quantity = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<ProductColor {self.color_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'color_name': self.color_name,
            'color_hex': self.color_hex,
            'stock_quantity': self.stock_quantity
        }

