import sys
import os
import cv2
import time
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.screen_capture import ScreenCapture
from core.roulette_detector import RouletteDetector

def validation_test():
    """Prueba de validación completa con la ruleta real"""
    print("🎯 PRUEBA DE VALIDACIÓN - RULETA REAL")
    print("=" * 50)
    
    try:
        # Inicializar módulos
        capture = ScreenCapture()
        detector = RouletteDetector()
        
        print("✅ Módulos inicializados")
        print(f"🎯 Configuración: {capture.monitor}")
        
        # Verificar captura inicial
        test_img, success = capture.capture_screen()
        if not success or test_img is None or test_img.max() == 0:
            print("❌ ERROR: No se puede capturar la pantalla")
            return False
        
        print(f"✅ Captura inicial OK: {test_img.shape[1]}x{test_img.shape[0]}")
        
        # Crear ventana de validación
        window_name = "Validación - Ruleta Real"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1000, 700)
        
        print("\n📋 INSTRUCCIONES DE VALIDACIÓN:")
        print("1. Asegúrate de que la ruleta esté VISIBLE en la pantalla")
        print("2. Observa si se detecta el círculo verde (ruleta)")
        print("3. Observa si se detecta el punto azul (bola)")
        print("4. Presiona 's' si funciona, 'r' para reintentar, 'q' para salir")
        print("5. La prueba durará 10 segundos automáticamente")
        
        start_time = time.time()
        validation_time = 10  # 10 segundos de prueba
        frames_processed = 0
        wheels_detected = 0
        balls_detected = 0
        
        last_valid_frame = None
        
        while time.time() - start_time < validation_time:
            # Capturar pantalla
            img, success = capture.capture_screen()
            
            if success and img is not None and img.max() > 0:
                frames_processed += 1
                
                # Procesar detección
                result_img, wheel, ball, detected = detector.test_detection(img)
                
                if wheel:
                    wheels_detected += 1
                if ball:
                    balls_detected += 1
                
                # Calcular métricas
                current_time = time.time() - start_time
                fps = frames_processed / current_time if current_time > 0 else 0
                
                # Crear display de validación
                display_img = result_img.copy()
                
                # Panel de validación
                overlay = display_img.copy()
                cv2.rectangle(overlay, (5, 5), (500, 200), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.7, display_img, 0.3, 0, display_img)
                
                # Título
                cv2.putText(display_img, "VALIDACION RULETA REAL", (15, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                
                # Estado de detección
                if wheel and ball:
                    status_text = "✅ RULETA Y BOLA DETECTADAS"
                    status_color = (0, 255, 0)
                elif wheel:
                    status_text = "✅ RULETA DETECTADA"
                    status_color = (0, 255, 255)
                else:
                    status_text = "🔍 BUSCANDO RULETA..."
                    status_color = (255, 255, 0)
                
                cv2.putText(display_img, status_text, (15, 65), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
                
                # Métricas
                cv2.putText(display_img, f"FPS: {fps:.1f}", (15, 95), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(display_img, f"Ruedas: {wheels_detected}/{frames_processed}", (15, 120), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(display_img, f"Bolas: {balls_detected}/{frames_processed}", (15, 145), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Tiempo restante
                remaining = validation_time - (time.time() - start_time)
                cv2.putText(display_img, f"Tiempo: {remaining:.1f}s", (15, 170), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Leyenda
                cv2.putText(display_img, "Verde: Ruleta | Azul: Bola", (15, display_img.shape[0]-30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                cv2.putText(display_img, "'s': Exito | 'r': Reintentar | 'q': Salir", (15, display_img.shape[0]-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                
                # Mostrar ventana
                cv2.imshow(window_name, display_img)
                last_valid_frame = display_img
                
            else:
                # Mostrar último frame válido o mensaje de error
                if last_valid_frame is not None:
                    error_overlay = last_valid_frame.copy()
                    cv2.putText(error_overlay, "❌ ERROR TEMPORAL DE CAPTURA", (50, 100), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.imshow(window_name, error_overlay)
            
            # Control de teclado
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):  # Success - éxito
                print("✅ Validación exitosa - usuario confirmó")
                cv2.destroyAllWindows()
                return True
            elif key == ord('r'):  # Retry - reintentar
                print("🔄 Reintentando validación...")
                start_time = time.time()  # Reiniciar timer
                frames_processed = 0
                wheels_detected = 0
                balls_detected = 0
            elif key == ord('q'):  # Quit - salir
                print("⏹️ Validación cancelada por usuario")
                cv2.destroyAllWindows()
                return False
        
        # Fin del tiempo automático
        cv2.destroyAllWindows()
        
        # Análisis de resultados automáticos
        total_time = time.time() - start_time
        wheel_detection_rate = (wheels_detected / frames_processed * 100) if frames_processed > 0 else 0
        ball_detection_rate = (balls_detected / frames_processed * 100) if frames_processed > 0 else 0
        
        print(f"\n📊 RESULTADOS AUTOMÁTICOS:")
        print(f"   Tiempo: {total_time:.1f}s")
        print(f"   Frames: {frames_processed}")
        print(f"   FPS: {frames_processed/total_time:.1f}")
        print(f"   Ruedas detectadas: {wheels_detected} ({wheel_detection_rate:.1f}%)")
        print(f"   Bolas detectadas: {balls_detected} ({ball_detection_rate:.1f}%)")
        
        # Evaluación automática
        if wheel_detection_rate > 50:
            print("🎉 VALIDACIÓN EXITOSA - Sistema operativo")
            return True
        elif wheel_detection_rate > 20:
            print("⚠️  VALIDACIÓN PARCIAL - Sistema necesita ajustes")
            return False
        else:
            print("❌ VALIDACIÓN FALLIDA - Revisar configuración")
            return False
            
    except Exception as e:
        print(f"❌ Error en validación: {e}")
        import traceback
        traceback.print_exc()
        return False

def quick_validation():
    """Validación rápida de 5 segundos"""
    print("⚡ VALIDACIÓN RÁPIDA (5 segundos)")
    global validation_time
    validation_time = 5
    return validation_test()

if __name__ == "__main__":
    print("🎰 SISTEMA DE VALIDACIÓN DE RULETA")
    print("=" * 40)
    
    print("1. Validación completa (10 segundos)")
    print("2. Validación rápida (5 segundos)")
    
    choice = input("Selecciona opción (1-2): ").strip()
    
    if choice == "1":
        success = validation_test()
    else:
        success = quick_validation()
    
    if success:
        print("\n🎉 ¡VALIDACIÓN EXITOSA!")
        print("✅ El sistema está listo para uso")
        print("🚀 Ejecuta: python tests/test_single_window.py")
    else:
        print("\n❌ VALIDACIÓN FALLIDA")
        print("💡 Ejecuta: python tests/fix_zoom_issue.py")