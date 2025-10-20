import cv2
import numpy as np
import os
import json
import time

class RouletteDetector:
    def __init__(self, config_file=None):
        if config_file is None:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_file = os.path.join(project_root, 'config', 'settings.json')
        self.config = self.load_config(config_file)
        
        # ✅ PARÁMETROS OPTIMIZADOS PARA DETECCIÓN REAL
        self.wheel_params = {
            'min_radius': 80,        # Reducido para ruletas más pequeñas
            'max_radius': 250,       # Reducido para evitar falsos positivos
            'dp': 1.2,              # Aumentado para mayor precisión
            'min_dist': 200,         # Aumentado para evitar duplicados
            'param1': 50,           # Reducido para bordes menos definidos
            'param2': 30,           # Reducido para círculos menos perfectos
        }

        self.ball_params = {
            'min_ball_size': 5,
            'max_ball_size': 30,
            'brightness_threshold': 160
        }
        
        self.detection_history = []
        self.verbose = True  # ✅ ACTIVADO para debugging
        
    def load_config(self, config_file):
        """Cargar configuración"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                print(f"✅ Configuración cargada desde: {config_file}")
                return config
        except Exception as e:
            print(f"❌ Error cargando configuración: {e}")
            return {}
    
    def set_verbose(self, verbose):
        """Activar/desactivar mensajes verbose"""
        self.verbose = verbose

    def detect_roulette(self, image):
        """✅ MÉTODO SIMPLIFICADO - Solo detecta ruleta y devuelve coordenadas"""
        try:
            # Convertir a escala de grises
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Aplicar desenfoque para reducir ruido
            blurred = cv2.medianBlur(gray, 5)
            
            # ✅ PARÁMETROS OPTIMIZADOS para detección real
            circles = cv2.HoughCircles(
                blurred,
                cv2.HOUGH_GRADIENT,
                dp=self.wheel_params['dp'],
                minDist=self.wheel_params['min_dist'],
                param1=self.wheel_params['param1'],
                param2=self.wheel_params['param2'],
                minRadius=self.wheel_params['min_radius'],
                maxRadius=self.wheel_params['max_radius']
            )
            
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                
                if self.verbose:
                    print(f"🎯 Círculos detectados inicialmente: {len(circles)}")
                
                # ✅ FILTRADO MEJORADO
                height, width = image.shape[:2]
                valid_circles = []
                
                for (x, y, r) in circles:
                    # Verificar posición central y tamaño razonable
                    is_centered = (abs(x - width/2) < width * 0.4 and 
                                  abs(y - height/2) < height * 0.4)
                    is_good_size = (r >= self.wheel_params['min_radius'] and 
                                   r <= self.wheel_params['max_radius'])
                    
                    if is_centered and is_good_size:
                        valid_circles.append((x, y, r))
                
                if valid_circles:
                    # ✅ SELECCIONAR EL MEJOR CÍRCULO
                    # Priorizar tamaño y centralidad
                    best_circle = max(valid_circles, key=lambda c: (c[2], -abs(c[0] - width/2)))
                    x, y, r = best_circle
                    
                    if self.verbose:
                        print(f"✅ Ruleta detectada - Centro: ({x}, {y}), Radio: {r}")
                    
                    return (x, y, r)
                else:
                    if self.verbose:
                        print("❌ Círculos detectados pero ninguno pasó el filtro")
            else:
                if self.verbose:
                    print("❌ No se detectaron círculos")
                    
            return None
            
        except Exception as e:
            print(f"❌ Error en detect_roulette: {e}")
            return None

    def detect_roulette_wheel(self, image):
        """Método original mejorado"""
        wheel = self.detect_roulette(image)
        
        if wheel is not None:
            x, y, r = wheel
            # Dibujar en la imagen
            output = image.copy()
            cv2.circle(output, (x, y), r, (0, 255, 0), 4)
            cv2.circle(output, (x, y), 5, (0, 0, 255), -1)
            cv2.putText(output, f"Ruleta R:{r}", (x-50, y-r-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            return output, wheel, True
        else:
            return image, None, False

    def detect_ball(self, image, wheel_region):
        """Detectar la bola"""
        try:
            if wheel_region is None:
                return image, None, False
            
            x, y, radius = wheel_region
            
            # Recortar región de la ruleta
            margin = 20
            y_start = max(0, y-radius-margin)
            y_end = min(image.shape[0], y+radius+margin)
            x_start = max(0, x-radius-margin)
            x_end = min(image.shape[1], x+radius+margin)
            
            wheel_img = image[y_start:y_end, x_start:x_end]
            
            if wheel_img.size == 0:
                return image, None, False
            
            # Buscar objetos brillantes
            hsv = cv2.cvtColor(wheel_img, cv2.COLOR_BGR2HSV)
            lower_white = np.array([0, 0, self.ball_params['brightness_threshold']])
            upper_white = np.array([180, 255, 255])
            mask = cv2.inRange(hsv, lower_white, upper_white)
            
            # Limpiar máscara
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # Encontrar contornos
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            ball_position = None
            output = image.copy()
            
            if contours:
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if (area >= self.ball_params['min_ball_size'] and 
                        area <= self.ball_params['max_ball_size']):
                        
                        M = cv2.moments(contour)
                        if M["m00"] != 0:
                            cx = int(M["m10"] / M["m00"])
                            cy = int(M["m01"] / M["m00"])
                            
                            global_x = x_start + cx
                            global_y = y_start + cy
                            
                            # Verificar que esté dentro de la ruleta
                            distance = np.sqrt((global_x - x)**2 + (global_y - y)**2)
                            if distance <= radius:
                                ball_position = (global_x, global_y)
                                cv2.circle(output, (global_x, global_y), 8, (255, 0, 0), -1)
                                cv2.putText(output, "BOLA", (global_x-20, global_y-15),
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
                                return output, ball_position, True
            
            return output, None, False
            
        except Exception as e:
            print(f"❌ Error detectando bola: {e}")
            return image, None, False

    # Mantener el resto de métodos igual...
    def test_detection(self, image):
        """Probar detección completa"""
        wheel = self.detect_roulette(image)
        result_img = image.copy()
        
        if wheel is not None:
            x, y, r = wheel
            cv2.circle(result_img, (x, y), r, (0, 255, 0), 3)
            cv2.circle(result_img, (x, y), 5, (0, 0, 255), -1)
            
            # Detectar bola
            result_img, ball, ball_found = self.detect_ball(result_img, wheel)
            
            status = f"Rueda: SI | Bola: {'SI' if ball_found else 'NO'}"
            cv2.putText(result_img, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            return result_img, wheel, ball, True
        else:
            cv2.putText(result_img, "Rueda: NO | Bola: NO", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            return image, None, None, False

    def live_detection_test(self, capture, duration=10):
        """Prueba en tiempo real"""
        print("🎥 Iniciando prueba de detección...")
        start_time = time.time()
        frame_count = 0
        detection_count = 0
        
        cv2.namedWindow("Ruleta Detector", cv2.WINDOW_NORMAL)
        
        try:
            while time.time() - start_time < duration:
                frame = capture.capture_screen()
                if frame is not None:
                    frame_count += 1
                    
                    result_img, wheel, ball, detected = self.test_detection(frame)
                    
                    if detected:
                        detection_count += 1
                    
                    # Mostrar FPS
                    fps = frame_count / (time.time() - start_time)
                    cv2.putText(result_img, f"FPS: {fps:.1f}", (10, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    cv2.imshow("Ruleta Detector", result_img)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        finally:
            cv2.destroyAllWindows()
        
        print(f"✅ Frames: {frame_count}, Detecciones: {detection_count}")

    def get_detection_stats(self):
        """Estadísticas de detección"""
        if not self.detection_history:
            return {}
        
        total = len(self.detection_history)
        wheels = sum(1 for r in self.detection_history if r['wheel_detected'])
        balls = sum(1 for r in self.detection_history if r['ball_detected'])
        
        return {
            'total_detections': total,
            'wheel_detections': wheels,
            'ball_detections': balls,
            'wheel_rate': (wheels / total * 100) if total > 0 else 0,
            'ball_rate': (balls / total * 100) if total > 0 else 0
        }