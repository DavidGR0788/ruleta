import sys
import os
import cv2

# Agregar la carpeta raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.screen_capture import ScreenCapture
from core.roulette_detector import RouletteDetector

def debug_detection():
    print("🔍 Modo debug - Detección paso a paso...")
    
    try:
        # Inicializar capturador y detector
        capture = ScreenCapture()
        detector = RouletteDetector()
        
        print("✅ Módulos inicializados")
        print("📸 Capturando pantalla...")
        
        # Capturar una sola imagen para debug
        img, success = capture.capture_screen()
        
        if success:
            print(f"✅ Imagen capturada: {img.shape[1]}x{img.shape[0]}")
            
            # Probar solo detección de rueda
            print("🎯 Probando detección de rueda...")
            result_img, wheel, wheel_found = detector.detect_roulette_wheel(img)
            
            if wheel_found:
                x, y, radius = wheel
                print(f"✅ Rueda encontrada en ({x}, {y}) con radio {radius}")
                
                # Probar detección de bola
                print("🎱 Probando detección de bola...")
                result_img, ball, ball_found = detector.detect_ball(result_img, wheel)
                
                if ball_found:
                    print(f"✅ Bola encontrada en {ball}")
                else:
                    print("❌ Bola no encontrada - mostrando análisis...")
                    
                    # Mostrar análisis de color en la región de la ruleta
                    debug_ball_detection(img, wheel)
            
            # Mostrar resultado
            cv2.imshow("Debug - Deteccion", result_img)
            print("🖼️ Imagen mostrada - Presiona cualquier tecla para continuar...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
        else:
            print("❌ Error capturando pantalla")
            
    except Exception as e:
        print(f"❌ Error en debug: {e}")
        import traceback
        traceback.print_exc()

def debug_ball_detection(image, wheel_region):
    """Análisis detallado de la detección de bola"""
    x, y, radius = wheel_region
    
    # Recortar región de la ruleta
    margin = 30
    y_start = max(0, y-radius-margin)
    y_end = min(image.shape[0], y+radius+margin)
    x_start = max(0, x-radius-margin)
    x_end = min(image.shape[1], x+radius+margin)
    
    wheel_img = image[y_start:y_end, x_start:x_end]
    
    if wheel_img.size == 0:
        print("❌ Región de ruleta vacía")
        return
    
    # Análisis de color
    hsv = cv2.cvtColor(wheel_img, cv2.COLOR_BGR2HSV)
    
    print("🎨 Análisis de colores en la región de la ruleta:")
    print(f"   - Brillo promedio: {np.mean(hsv[:,:,2]):.1f}")
    print(f"   - Saturación promedio: {np.mean(hsv[:,:,1]):.1f}")
    
    # Probar diferentes umbrales de brillo
    for threshold in [150, 180, 200, 220]:
        lower_white = np.array([0, 0, threshold])
        upper_white = np.array([180, 255, 255])
        mask = cv2.inRange(hsv, lower_white, upper_white)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        small_contours = [c for c in contours if 10 < cv2.contourArea(c) < 100]
        print(f"   - Umbral {threshold}: {len(small_contours)} objetos pequeños encontrados")

if __name__ == "__main__":
    debug_detection()