from flask import Blueprint, request, jsonify, send_file
import os
import cv2
import numpy as np
from werkzeug.utils import secure_filename
import base64
from io import BytesIO
from PIL import Image
from src.ai_engine import GlowMirrorAI

ai_bp = Blueprint('ai', __name__)

# تهيئة محرك الذكاء الاصطناعي
ai_engine = GlowMirrorAI()

# مجلد حفظ الصور
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
PROCESSED_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'processed')

# إنشاء المجلدات إذا لم تكن موجودة
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    """التحقق من امتداد الملف المسموح"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def base64_to_image(base64_string):
    """تحويل base64 إلى صورة"""
    try:
        # إزالة البادئة إذا كانت موجودة
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # فك التشفير
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))
        
        # تحويل إلى RGB إذا كانت RGBA
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        
        # تحويل إلى numpy array
        image_array = np.array(image)
        
        # تحويل من RGB إلى BGR لـ OpenCV
        image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        return image_bgr
    except Exception as e:
        return None

def image_to_base64(image):
    """تحويل الصورة إلى base64"""
    try:
        # تحويل من BGR إلى RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # تحويل إلى PIL Image
        pil_image = Image.fromarray(image_rgb)
        
        # حفظ في buffer
        buffer = BytesIO()
        pil_image.save(buffer, format='PNG')
        
        # تحويل إلى base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return f"data:image/png;base64,{image_base64}"
    except Exception as e:
        return None

@ai_bp.route('/detect-face', methods=['POST'])
def detect_face():
    """كشف الوجه وتحديد النقاط المرجعية"""
    try:
        data = request.get_json()
        
        if 'image' not in data:
            return jsonify({
                'success': False,
                'error': 'No image provided'
            }), 400
        
        # تحويل base64 إلى صورة
        image = base64_to_image(data['image'])
        if image is None:
            return jsonify({
                'success': False,
                'error': 'Invalid image format'
            }), 400
        
        # كشف الوجه
        result = ai_engine.detect_face_landmarks(image)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_bp.route('/apply-makeup', methods=['POST'])
def apply_makeup():
    """تطبيق المكياج على الصورة"""
    try:
        data = request.get_json()
        
        if 'image' not in data or 'makeup_config' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing image or makeup configuration'
            }), 400
        
        # تحويل base64 إلى صورة
        image = base64_to_image(data['image'])
        if image is None:
            return jsonify({
                'success': False,
                'error': 'Invalid image format'
            }), 400
        
        # حفظ الصورة مؤقتاً
        temp_filename = 'temp_image.jpg'
        temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)
        cv2.imwrite(temp_path, image)
        
        # تطبيق المكياج
        result = ai_engine.process_makeup_application(temp_path, data['makeup_config'])
        
        if result['success']:
            # تحويل الصورة المعالجة إلى base64
            processed_image_base64 = image_to_base64(result['image'])
            
            if processed_image_base64:
                result['processed_image'] = processed_image_base64
                # إزالة الصورة من النتيجة لتوفير الذاكرة
                del result['image']
            else:
                result['success'] = False
                result['error'] = 'Failed to encode processed image'
        
        # حذف الملف المؤقت
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_bp.route('/analyze-skin-tone', methods=['POST'])
def analyze_skin_tone():
    """تحليل لون البشرة"""
    try:
        data = request.get_json()
        
        if 'image' not in data:
            return jsonify({
                'success': False,
                'error': 'No image provided'
            }), 400
        
        # تحويل base64 إلى صورة
        image = base64_to_image(data['image'])
        if image is None:
            return jsonify({
                'success': False,
                'error': 'Invalid image format'
            }), 400
        
        # كشف الوجه أولاً
        face_result = ai_engine.detect_face_landmarks(image)
        if not face_result['success']:
            return jsonify(face_result), 400
        
        # تحليل لون البشرة
        skin_result = ai_engine.analyze_skin_tone(image, face_result)
        
        if skin_result['success']:
            # الحصول على توصيات الألوان
            recommendations = ai_engine.get_color_recommendations(skin_result['skin_tone'])
            skin_result['color_recommendations'] = recommendations
        
        return jsonify(skin_result), 200 if skin_result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_bp.route('/enhance-image', methods=['POST'])
def enhance_image():
    """تحسين جودة الصورة"""
    try:
        data = request.get_json()
        
        if 'image' not in data:
            return jsonify({
                'success': False,
                'error': 'No image provided'
            }), 400
        
        # تحويل base64 إلى صورة
        image = base64_to_image(data['image'])
        if image is None:
            return jsonify({
                'success': False,
                'error': 'Invalid image format'
            }), 400
        
        # تحسين الصورة
        result = ai_engine.enhance_image_quality(image)
        
        if result['success']:
            # تحويل الصورة المحسنة إلى base64
            enhanced_image_base64 = image_to_base64(result['image'])
            
            if enhanced_image_base64:
                result['enhanced_image'] = enhanced_image_base64
                # إزالة الصورة من النتيجة لتوفير الذاكرة
                del result['image']
            else:
                result['success'] = False
                result['error'] = 'Failed to encode enhanced image'
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_bp.route('/color-recommendations/<skin_tone>', methods=['GET'])
def get_color_recommendations(skin_tone):
    """الحصول على توصيات الألوان بناءً على لون البشرة"""
    try:
        if skin_tone not in ['light', 'medium', 'dark']:
            return jsonify({
                'success': False,
                'error': 'Invalid skin tone. Must be light, medium, or dark'
            }), 400
        
        recommendations = ai_engine.get_color_recommendations(skin_tone)
        
        return jsonify({
            'success': True,
            'skin_tone': skin_tone,
            'recommendations': recommendations
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_bp.route('/upload-image', methods=['POST'])
def upload_image():
    """رفع صورة للمعالجة"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'filepath': filepath
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid file type'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

