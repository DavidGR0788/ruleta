import sys
import os
import cv2
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.screen_capture import ScreenCapture
from core.roulette_detector import RouletteDetector

def debug_black_screen():
    """Debug específico para el problema de pantalla negra"""
    print("🔧 DEBUG: PROBLEMA DE PANTALLA NEGRA")
    print("=" * 50)
    
    try:
        # Inicializar módulos
        capture = ScreenCapture()
        detector = RouletteDetector()
        
        print("✅ Módulos inicializados")
        print(f"🎯 Región configurada: {capture.monitor}")
        
        # Probar captura básica
        print("\n📸 Probando captura básica...")
        img, success = capture.capture_screen()
        
        if not success:
            print("❌ ERROR: No se pudo capturar la pantalla")
            return
        
        print(f"✅ Captura exitosa: {img.shape[1]}x{img.shape[0]} - Tipo: {img.dtype}")
        print(f"   Rango de valores: {img.min()} a {img.max()}")
        
        # Verificar si la imagen está completamente negra
        if img.max() == 0:
            print("❌ CRÍTICO: La imagen capturada está completamente NEGRA")
            print("   Posibles causas:")
            print("   - Región de captura incorrecta")
            print("   - Problema con los monitores")
            print("   - Permisos de captura de pantalla")
            return
        
        # Mostrar la captura original
        display_original = cv2.resize(img, (800, 600))
        cv2.putText(display_original, "CAPTURA ORIGINAL", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(display_original, f"Size: {img.shape[1]}x{img.shape[0]}", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow("1 - Captura Original", display_original)
        cv2.waitKey(0)
        
        # Probar detección
        print("\n🎯 Probando detección...")
        result_img, wheel, ball, detected = detector.test_detection(img)
        
        print(f"✅ Detección completada - Rueda: {wheel is not None}, Bola: {ball is not None}")
        
        # Mostrar resultado de detección
        display_result = cv2.resize(result_img, (800, 600))
        cv2.putText(display_result, "RESULTADO DETECCION", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow("2 - Resultado Detección", display_result)
        cv2.waitKey(0)
        
        # Análisis de la región configurada
        print(f"\n🔍 Análisis de región: {capture.monitor}")
        
        # Probar diferentes regiones si es necesario
        test_regions = [
            (0, 0, 1366, 768),  # Pantalla completa
            (341, 192, 683, 384),  # Actual
            (341, 0, 683, 768),   # Vertical centrado
            (0, 192, 1366, 384)   # Horizontal centrado
        ]
        
        for i, region in enumerate(test_regions):
            print(f"\n🔄 Probando región alternativa {i+1}: {region}")
            test_img, success = capture.capture_region(region)
            
            if success and test_img is not None and test_img.max() > 0:
                display_test = cv2.resize(test_img, (800, 600))
                cv2.putText(display_test, f"REGION {i+1}: {region}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imshow(f"Region Test {i+1}", display_test)
                
                key = cv2.waitKey(0)
                if key == ord('s'):
                    print(f"✅ Región {i+1} seleccionada")
                    # Actualizar configuración
                    update_region_config(region)
                    break
            else:
                print(f"❌ Región {i+1} no válida")
        
        cv2.destroyAllWindows()
        print("\n🎯 Debug completado")
        
    except Exception as e:
        print(f"❌ Error en debug: {e}")
        import traceback
        traceback.print_exc()

def update_region_config(region):
    """Actualizar la configuración con nueva región"""
    try:
        import json
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_file = os.path.join(project_root, 'config', 'settings.json')
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        config['capture']['region'] = region
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
        
        print(f"✅ Configuración actualizada: {region}")
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando configuración: {e}")
        return False

if __name__ == "__main__":
    debug_black_screen()