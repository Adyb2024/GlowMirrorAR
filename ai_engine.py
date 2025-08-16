import cv2
import numpy as np
import mediapipe as mp
from PIL import Image, ImageDraw, ImageFilter
import colorsys
import math

class GlowMirrorAI:
    """
    محرك الذكاء الاصطناعي الرئيسي لتطبيق GlowMirror AR
    يتضمن جميع وظائف كشف الوجه وتطبيق المكياج والتوصيات الذكية
    """
    
    def __init__(self):
        # تهيئة MediaPipe للوجه
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # تهيئة كاشف الوجه
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # نقاط الوجه المهمة
        self.LIPS_LANDMARKS = [
            61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318,
            78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308
        ]
        
        self.LEFT_EYE_LANDMARKS = [
            33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158,
            159, 160, 161, 246
        ]
        
        self.RIGHT_EYE_LANDMARKS = [
            362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388,
            387, 386, 385, 384, 398
        ]
        
        self.LEFT_EYEBROW_LANDMARKS = [
            46, 53, 52, 51, 48, 115, 131, 134, 102, 49, 220, 305
        ]
        
        self.RIGHT_EYEBROW_LANDMARKS = [
            276, 283, 282, 281, 278, 344, 360, 363, 331, 279, 440, 75
        ]
        
        self.CHEEK_LANDMARKS = [
            116, 117, 118, 119, 120, 121, 126, 142, 36, 205, 206, 207,
            213, 192, 147, 187, 207, 213, 192, 147, 187, 207, 213, 192
        ]

    def detect_face_landmarks(self, image):
        """
        كشف الوجه وتحديد النقاط المرجعية
        """
        try:
            # تحويل الصورة إلى RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # معالجة الصورة
            results = self.face_mesh.process(rgb_image)
            
            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                
                # استخراج النقاط
                landmarks = []
                h, w, _ = image.shape
                
                for landmark in face_landmarks.landmark:
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    landmarks.append((x, y))
                
                return {
                    'success': True,
                    'landmarks': landmarks,
                    'lips': [landmarks[i] for i in self.LIPS_LANDMARKS],
                    'left_eye': [landmarks[i] for i in self.LEFT_EYE_LANDMARKS],
                    'right_eye': [landmarks[i] for i in self.RIGHT_EYE_LANDMARKS],
                    'left_eyebrow': [landmarks[i] for i in self.LEFT_EYEBROW_LANDMARKS],
                    'right_eyebrow': [landmarks[i] for i in self.RIGHT_EYEBROW_LANDMARKS],
                    'cheeks': [landmarks[i] for i in self.CHEEK_LANDMARKS]
                }
            else:
                return {'success': False, 'error': 'No face detected'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def apply_lipstick(self, image, landmarks, color_hex, intensity=0.7):
        """
        تطبيق أحمر الشفاه
        """
        try:
            # تحويل اللون من hex إلى RGB
            color_rgb = tuple(int(color_hex[i:i+2], 16) for i in (1, 3, 5))
            
            # إنشاء قناع للشفاه
            mask = np.zeros(image.shape[:2], dtype=np.uint8)
            lips_points = np.array(landmarks['lips'], dtype=np.int32)
            cv2.fillPoly(mask, [lips_points], 255)
            
            # تطبيق اللون
            colored_lips = image.copy()
            colored_lips[mask > 0] = [
                int(colored_lips[mask > 0, 0] * (1 - intensity) + color_rgb[2] * intensity),
                int(colored_lips[mask > 0, 1] * (1 - intensity) + color_rgb[1] * intensity),
                int(colored_lips[mask > 0, 2] * (1 - intensity) + color_rgb[0] * intensity)
            ]
            
            return {'success': True, 'image': colored_lips}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def apply_eyeshadow(self, image, landmarks, color_hex, intensity=0.5):
        """
        تطبيق ظل العيون
        """
        try:
            color_rgb = tuple(int(color_hex[i:i+2], 16) for i in (1, 3, 5))
            
            result_image = image.copy()
            
            # تطبيق على العين اليسرى
            left_eye_mask = np.zeros(image.shape[:2], dtype=np.uint8)
            left_eye_points = np.array(landmarks['left_eye'], dtype=np.int32)
            cv2.fillPoly(left_eye_mask, [left_eye_points], 255)
            
            # تطبيق على العين اليمنى
            right_eye_mask = np.zeros(image.shape[:2], dtype=np.uint8)
            right_eye_points = np.array(landmarks['right_eye'], dtype=np.int32)
            cv2.fillPoly(right_eye_mask, [right_eye_points], 255)
            
            # دمج الأقنعة
            eye_mask = cv2.bitwise_or(left_eye_mask, right_eye_mask)
            
            # تطبيق اللون
            result_image[eye_mask > 0] = [
                int(result_image[eye_mask > 0, 0] * (1 - intensity) + color_rgb[2] * intensity),
                int(result_image[eye_mask > 0, 1] * (1 - intensity) + color_rgb[1] * intensity),
                int(result_image[eye_mask > 0, 2] * (1 - intensity) + color_rgb[0] * intensity)
            ]
            
            return {'success': True, 'image': result_image}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def apply_blush(self, image, landmarks, color_hex, intensity=0.4):
        """
        تطبيق البلاشر
        """
        try:
            color_rgb = tuple(int(color_hex[i:i+2], 16) for i in (1, 3, 5))
            
            result_image = image.copy()
            
            # إنشاء قناع للخدود
            cheek_mask = np.zeros(image.shape[:2], dtype=np.uint8)
            cheek_points = np.array(landmarks['cheeks'], dtype=np.int32)
            
            # تطبيق تأثير دائري للبلاشر
            for point in cheek_points:
                cv2.circle(cheek_mask, tuple(point), 30, 255, -1)
            
            # تطبيق تأثير ضبابي للحصول على مظهر طبيعي
            cheek_mask = cv2.GaussianBlur(cheek_mask, (51, 51), 0)
            
            # تطبيق اللون
            for i in range(3):
                result_image[:, :, i] = np.where(
                    cheek_mask > 0,
                    result_image[:, :, i] * (1 - intensity * cheek_mask / 255) + 
                    color_rgb[2-i] * intensity * cheek_mask / 255,
                    result_image[:, :, i]
                )
            
            return {'success': True, 'image': result_image}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def analyze_skin_tone(self, image, landmarks):
        """
        تحليل لون البشرة
        """
        try:
            # استخراج منطقة الوجه
            face_points = landmarks['cheeks'] + landmarks['lips']
            
            # حساب متوسط اللون في منطقة الوجه
            mask = np.zeros(image.shape[:2], dtype=np.uint8)
            face_polygon = np.array(face_points, dtype=np.int32)
            cv2.fillPoly(mask, [face_polygon], 255)
            
            # حساب متوسط RGB
            mean_color = cv2.mean(image, mask)[:3]
            
            # تحويل إلى HSV لتحليل أفضل
            hsv_color = colorsys.rgb_to_hsv(
                mean_color[2]/255, mean_color[1]/255, mean_color[0]/255
            )
            
            # تصنيف لون البشرة
            brightness = hsv_color[2]
            if brightness < 0.3:
                skin_tone = 'dark'
            elif brightness < 0.6:
                skin_tone = 'medium'
            else:
                skin_tone = 'light'
            
            return {
                'success': True,
                'skin_tone': skin_tone,
                'rgb': mean_color,
                'hsv': hsv_color
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_color_recommendations(self, skin_tone):
        """
        الحصول على توصيات الألوان بناءً على لون البشرة
        """
        recommendations = {
            'light': {
                'lipstick': ['#ff6b9d', '#ff7675', '#fd79a8', '#e84393'],
                'eyeshadow': ['#a55eea', '#3742fa', '#ff6348', '#f8b500'],
                'blush': ['#ff9ff3', '#ff6b9d', '#fd79a8', '#ff7675']
            },
            'medium': {
                'lipstick': ['#ff4757', '#c44569', '#f8b500', '#e84393'],
                'eyeshadow': ['#2f3542', '#ff6348', '#ff9ff3', '#a55eea'],
                'blush': ['#ff7675', '#fd79a8', '#e84393', '#c44569']
            },
            'dark': {
                'lipstick': ['#c44569', '#8b0000', '#ff4757', '#e84393'],
                'eyeshadow': ['#2f3542', '#8b4513', '#ff6348', '#a55eea'],
                'blush': ['#e84393', '#ff7675', '#c44569', '#ff4757']
            }
        }
        
        return recommendations.get(skin_tone, recommendations['medium'])

    def enhance_image_quality(self, image):
        """
        تحسين جودة الصورة
        """
        try:
            # تحسين الإضاءة
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # تطبيق CLAHE على قناة الإضاءة
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            l = clahe.apply(l)
            
            # دمج القنوات
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
            
            # تحسين الحدة
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(enhanced, -1, kernel)
            
            # دمج الصورة الأصلية مع المحسنة
            result = cv2.addWeighted(enhanced, 0.7, sharpened, 0.3, 0)
            
            return {'success': True, 'image': result}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def process_makeup_application(self, image_path, makeup_config):
        """
        تطبيق المكياج الكامل على الصورة
        """
        try:
            # قراءة الصورة
            image = cv2.imread(image_path)
            if image is None:
                return {'success': False, 'error': 'Could not load image'}
            
            # كشف الوجه
            face_result = self.detect_face_landmarks(image)
            if not face_result['success']:
                return face_result
            
            landmarks = face_result
            result_image = image.copy()
            
            # تطبيق المكياج حسب التكوين
            if 'lipstick' in makeup_config:
                lipstick_result = self.apply_lipstick(
                    result_image, 
                    landmarks, 
                    makeup_config['lipstick']['color'],
                    makeup_config['lipstick'].get('intensity', 0.7)
                )
                if lipstick_result['success']:
                    result_image = lipstick_result['image']
            
            if 'eyeshadow' in makeup_config:
                eyeshadow_result = self.apply_eyeshadow(
                    result_image,
                    landmarks,
                    makeup_config['eyeshadow']['color'],
                    makeup_config['eyeshadow'].get('intensity', 0.5)
                )
                if eyeshadow_result['success']:
                    result_image = eyeshadow_result['image']
            
            if 'blush' in makeup_config:
                blush_result = self.apply_blush(
                    result_image,
                    landmarks,
                    makeup_config['blush']['color'],
                    makeup_config['blush'].get('intensity', 0.4)
                )
                if blush_result['success']:
                    result_image = blush_result['image']
            
            # تحسين جودة الصورة النهائية
            enhancement_result = self.enhance_image_quality(result_image)
            if enhancement_result['success']:
                result_image = enhancement_result['image']
            
            # تحليل لون البشرة للتوصيات
            skin_analysis = self.analyze_skin_tone(image, landmarks)
            
            return {
                'success': True,
                'image': result_image,
                'skin_analysis': skin_analysis,
                'landmarks': landmarks
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

