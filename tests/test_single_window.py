import sys
import os
import cv2
import time
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.screen_capture import ScreenCapture
from core.roulette_detector import RouletteDetector

def single_window_test(duration=15):
    """Prueba con UNA sola ventana - VERSIÓN MEJORADA"""
    print("🎯 INICIANDO PRUEBA - UNA SOLA VENTANA MEJORADA")
    print("=" * 50)
    
    try:
        # Inicializar módulos
        capture = ScreenCapture()
        detector = RouletteDetector()
        
        print("✅ Módulos inicializados")
        print(f"🎯 Región configurada: {capture.monitor}")
        
        # Verificar captura inicial
        test_img, success = capture.capture_screen()
        if not success or test_img is None or test_img.max() == 0:
            print("❌ ERROR: La captura inicial está vacía o en negro")
            print("   Ejecuta: python tests/debug_black_screen.py")
            return
        
        print(f"✅ Captura inicial OK: {test_img.shape[1]}x{test_img.shape[0]}")
        
        # Crear UNA sola ventana
        window_name = "Ruleta Predictor - Vista Única"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1000, 700)
        
        start_time = time.time()
        frame_count = 0
        detection_count = 0
        wheel_detections = 0
        ball_detections = 0
        
        print("🎥 Iniciando captura...")
        print("🛑 Presiona 'q' para salir")
        print("⏰ Duración: 15 segundos")
        print("💡 La ventana debería mostrar la ruleta en tiempo real")
        
        last_frame = None
        
        while time.time() - start_time < duration:
            # Capturar pantalla
            img, success = capture.capture_screen()
            
            if success and img is not None and img.max() > 0:
                frame_count += 1
                
                # Procesar detección
                result_img, wheel, ball, detected = detector.test_detection(img)
                
                if detected:
                    detection_count += 1
                    if wheel:
                        wheel_detections += 1
                    if ball:
                        ball_detections += 1
                
                # Calcular métricas
                current_time = time.time() - start_time
                fps = frame_count / current_time if current_time > 0 else 0
                
                # Crear display mejorado
                display_img = result_img.copy()
                
                # Panel de información (fondo semitransparente)
                overlay = display_img.copy()
                cv2.rectangle(overlay, (5, 5), (400, 180), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.7, display_img, 0.3, 0, display_img)
                
                # Información principal
                cv2.putText(display_img, f"FPS: {fps:.1f}", (15, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.putText(display_img, f"Frames: {frame_count}", (15, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Estadísticas de detección
                wheel_rate = (wheel_detections / frame_count * 100) if frame_count > 0 else 0
                ball_rate = (ball_detections / frame_count * 100) if frame_count > 0 else 0
                
                wheel_color = (0, 255, 0) if wheel_detections > 0 else (255, 255, 255)
                ball_color = (255, 0, 0) if ball_detections > 0 else (255, 255, 255)
                
                cv2.putText(display_img, f"Ruedas: {wheel_detections} ({wheel_rate:.1f}%)", (15, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, wheel_color, 2)
                cv2.putText(display_img, f"Bolas: {ball_detections} ({ball_rate:.1f}%)", (15, 115), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, ball_color, 2)
                
                # Tiempo y región
                remaining = duration - (time.time() - start_time)
                cv2.putText(display_img, f"Tiempo: {remaining:.1f}s", (15, 140), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                region_info = f"Region: {capture.monitor['left']},{capture.monitor['top']}"
                cv2.putText(display_img, region_info, (15, 165), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                
                # Estado de detección actual
                status_y = display_img.shape[0] - 20
                current_status = "DETECTANDO..."
                if wheel and ball:
                    current_status = "✅ RULETA Y BOLA DETECTADAS"
                    cv2.putText(display_img, current_status, (15, status_y), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                elif wheel:
                    current_status = "✅ RULETA DETECTADA"
                    cv2.putText(display_img, current_status, (15, status_y), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else:
                    current_status = "🔍 BUSCANDO RULETA..."
                    cv2.putText(display_img, current_status, (15, status_y), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                
                # Mostrar en la ÚNICA ventana
                cv2.imshow(window_name, display_img)
                last_frame = display_img
                
            else:
                # Si la captura falla, mostrar último frame o mensaje de error
                if last_frame is not None:
                    error_overlay = last_frame.copy()
                    cv2.putText(error_overlay, "❌ ERROR DE CAPTURA", (50, 100), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    cv2.imshow(window_name, error_overlay)
                else:
                    # Crear imagen de error inicial
                    error_img = np.zeros((400, 600, 3), dtype=np.uint8)
                    cv2.putText(error_img, "❌ ERROR DE CAPTURA", (50, 150), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    cv2.putText(error_img, "Ejecuta: python tests/debug_black_screen.py", (30, 200), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.imshow(window_name, error_img)
            
            # Control de teclado
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("⏹️ Salida solicitada por usuario")
                break
            elif key == ord(' '):
                print("⏸️ Pausa - Presiona cualquier tecla para continuar...")
                cv2.waitKey(0)
            elif key == ord('r'):
                print("🔄 Reintentando captura...")
                # Forzar nueva captura
                img, success = capture.capture_screen()
        
        # Estadísticas finales
        cv2.destroyAllWindows()
        
        total_time = time.time() - start_time
        detection_rate = (detection_count / frame_count * 100) if frame_count > 0 else 0
        
        print("\n📊 ESTADÍSTICAS FINALES:")
        print(f"   Tiempo total: {total_time:.1f}s")
        print(f"   Frames procesados: {frame_count}")
        print(f"   FPS promedio: {frame_count/total_time:.1f}")
        print(f"   Ruedas detectadas: {wheel_detections}")
        print(f"   Bolas detectadas: {ball_detections}")
        print(f"   Tasa de detección: {detection_rate:.1f}%")
        
        # Análisis de resultados
        if frame_count == 0:
            print("❌ CRÍTICO: No se procesaron frames")
        elif wheel_detections == 0:
            print("⚠️  ADVERTENCIA: No se detectaron ruedas")
            print("   Posibles causas:")
            print("   - Región de captura incorrecta")
            print("   - Parámetros de detección muy estrictos")
            print("   - La ruleta no está en la región capturada")
        elif detection_rate < 10:
            print("⚠️  ADVERTENCIA: Tasa de detección muy baja")
            print("   Ejecuta: python tests/debug_black_screen.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    single_window_test(duration=15)