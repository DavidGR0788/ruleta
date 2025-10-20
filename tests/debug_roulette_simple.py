"""
DEBUG SUPER SIMPLE - Solo detección de ruleta - VERSIÓN OPTIMIZADA
"""
import cv2
import sys
import os
import time

# Agregar ruta del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    print("🔍 DEBUG SIMPLIFICADO - SOLO RULETA")
    print("=" * 50)
    
    try:
        from core.screen_capture import ScreenCapture
        from core.roulette_detector import RouletteDetector
        
        # 1. Inicializar capturador
        capture = ScreenCapture()
        
        # 2. Inicializar detector
        detector = RouletteDetector()
        
        print("🎯 Objetivo: Detectar solo la ruleta")
        print("📝 Configuración cargada correctamente")
        print("▶️  Iniciando en 3 segundos...")
        
        for i in range(3, 0, -1):
            print(f"   {i}...")
            time.sleep(1)
        
        frame_count = 0
        detections = 0
        last_time = time.time()
        
        print("🚀 Iniciando detección en tiempo real...")
        print("   Presiona 'q' para salir")
        print("   Presiona 'p' para pausar")
        
        while True:
            try:
                current_time = time.time()
                
                # Capturar pantalla
                frame, success = capture.capture_screen()
                
                if not success or frame is None:
                    print("❌ Error en captura")
                    continue  # Continuar en lugar de romper
                    
                frame_count += 1
                
                # Calcular FPS
                fps = 1.0 / (current_time - last_time) if frame_count > 1 else 0
                last_time = current_time
                
                # Intentar detectar ruleta
                roulette_circle = detector.detect_roulette(frame)
                
                if roulette_circle:
                    detections += 1
                    x, y, r = roulette_circle
                    
                    # Dibujar círculo verde para ruleta
                    cv2.circle(frame, (x, y), r, (0, 255, 0), 3)
                    cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
                    cv2.putText(frame, f"RULETA r={r}", (x-50, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
                    # Mostrar mensaje solo cada 30 frames para no saturar consola
                    if frame_count % 30 == 0:
                        print(f"✅ Frame {frame_count}: Ruleta detectada - Radio: {r}, FPS: {fps:.1f}")
                else:
                    # Mostrar mensaje solo cada 50 frames
                    if frame_count % 50 == 0:
                        print(f"❌ Frame {frame_count}: Buscando ruleta... FPS: {fps:.1f}")
                    
                    cv2.putText(frame, "RULETA NO DETECTADA", (50, 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                # Mostrar información en pantalla
                cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f"Frames: {frame_count}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, f"Detecciones: {detections}", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Mostrar frame
                cv2.imshow("DEBUG - Solo Ruleta", frame)
                
                # Control de teclado - TIEMPO REDUCIDO para mejor respuesta
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("⏹️ Salida solicitada por usuario")
                    break
                elif key == ord('p'):
                    print("⏸️ Pausa - Presiona cualquier tecla para continuar...")
                    cv2.waitKey(0)
                
                # Estadísticas cada 60 frames
                if frame_count % 60 == 0:
                    accuracy = (detections / frame_count) * 100
                    print(f"📊 Estadísticas: {detections}/{frame_count} frames ({accuracy:.1f}%)")
                    
            except KeyboardInterrupt:
                print("⏹️ Interrupción por teclado")
                break
            except Exception as e:
                print(f"💥 Error en bucle: {e}")
                # Continuar en lugar de romper
                continue
        
        # Resumen final
        final_accuracy = (detections / frame_count) * 100 if frame_count > 0 else 0
        total_time = time.time() - (last_time - (1.0/fps if fps > 0 else 0))
        avg_fps = frame_count / total_time if total_time > 0 else 0
        
        print("=" * 50)
        print(f"🎯 RESUMEN FINAL:")
        print(f"   Frames procesados: {frame_count}")
        print(f"   Tiempo total: {total_time:.1f}s")
        print(f"   FPS promedio: {avg_fps:.1f}")
        print(f"   Detecciones exitosas: {detections}")
        print(f"   Precisión: {final_accuracy:.1f}%")
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
    except Exception as e:
        print(f"💥 Error general: {e}")
    
    cv2.destroyAllWindows()
    print("✅ Programa terminado correctamente")

if __name__ == "__main__":
    main()