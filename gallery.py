from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.gallery import SavedLook, UserPreference

gallery_bp = Blueprint('gallery', __name__)

@gallery_bp.route('/users/<int:user_id>/looks', methods=['GET'])
def get_user_looks(user_id):
    """Get all saved looks for a user"""
    try:
        looks = SavedLook.query.filter_by(user_id=user_id).order_by(SavedLook.created_at.desc()).all()
        return jsonify({
            'success': True,
            'looks': [look.to_dict() for look in looks]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@gallery_bp.route('/users/<int:user_id>/looks', methods=['POST'])
def save_look(user_id):
    """Save a new look for a user"""
    try:
        data = request.get_json()
        
        look = SavedLook(
            user_id=user_id,
            image_url=data['image_url'],
            look_name=data.get('look_name', ''),
            products_used=data.get('products_used', [])
        )
        
        db.session.add(look)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'look': look.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@gallery_bp.route('/looks/<int:look_id>', methods=['DELETE'])
def delete_look(look_id):
    """Delete a saved look"""
    try:
        look = SavedLook.query.get_or_404(look_id)
        db.session.delete(look)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Look deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@gallery_bp.route('/looks/<int:look_id>/favorite', methods=['PUT'])
def toggle_favorite(look_id):
    """Toggle favorite status of a look"""
    try:
        look = SavedLook.query.get_or_404(look_id)
        look.is_favorite = not look.is_favorite
        db.session.commit()
        
        return jsonify({
            'success': True,
            'look': look.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@gallery_bp.route('/users/<int:user_id>/preferences', methods=['GET'])
def get_user_preferences(user_id):
    """Get user preferences"""
    try:
        preferences = UserPreference.query.filter_by(user_id=user_id).first()
        if preferences:
            return jsonify({
                'success': True,
                'preferences': preferences.to_dict()
            }), 200
        else:
            return jsonify({
                'success': True,
                'preferences': None
            }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@gallery_bp.route('/users/<int:user_id>/preferences', methods=['POST'])
def save_user_preferences(user_id):
    """Save or update user preferences"""
    try:
        data = request.get_json()
        
        preferences = UserPreference.query.filter_by(user_id=user_id).first()
        if preferences:
            # Update existing preferences
            preferences.skin_tone = data.get('skin_tone', preferences.skin_tone)
            preferences.preferred_categories = data.get('preferred_categories', preferences.preferred_categories)
            preferences.favorite_colors = data.get('favorite_colors', preferences.favorite_colors)
            preferences.budget_range = data.get('budget_range', preferences.budget_range)
        else:
            # Create new preferences
            preferences = UserPreference(
                user_id=user_id,
                skin_tone=data.get('skin_tone'),
                preferred_categories=data.get('preferred_categories', []),
                favorite_colors=data.get('favorite_colors', []),
                budget_range=data.get('budget_range')
            )
            db.session.add(preferences)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'preferences': preferences.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

