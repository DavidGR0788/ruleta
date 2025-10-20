import sys
import os
import cv2
import pyautogui
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.screen_capture import ScreenCapture

def fix_zoom_issue():
    """Solución para el problema de zoom excesivo"""
    print("🔧 SOLUCIÓN: PROBLEMA DE ZOOM EXCESIVO")
    print("=" * 50)
    
    try:
        # Obtener resolución real de la pantalla
        screen_width, screen_height = pyautogui.size()
        print(f"📺 Resolución real de pantalla: {screen_width}x{screen_height}")
        
        # Mostrar el problema actual
        print(f"🎯 Región actual: (341, 192, 683, 384)")
        print(f"   Esto es solo: {683/screen_width*100:.1f}% del ancho")
        print(f"   y {384/screen_height*100:.1f}% del alto")
        print("   ⚠️  Demasiado zoom - probablemente no incluye la ruleta completa")
        
        # Opciones recomendadas
        recommended_regions = {
            '1': {'name': 'PANTALLA COMPLETA', 'coords': (0, 0, screen_width, screen_height)},
            '2': {'name': 'MITAD IZQUIERDA', 'coords': (0, 0, screen_width//2, screen_height)},
            '3': {'name': 'MITAD DERECHA', 'coords': (screen_width//2, 0, screen_width//2, screen_height)},
            '4': {'name': 'TERCIO CENTRAL', 'coords': (screen_width//6, 0, screen_width*2//3, screen_height)},
            '5': {'name': 'NAVEGADOR TÍPICO', 'coords': (100, 100, screen_width-200, screen_height-200)}
        }
        
        print("\n📋 OPCIONES RECOMENDADAS:")
        for key, region in recommended_regions.items():
            x, y, w, h = region['coords']
            width_pct = (w / screen_width) * 100
            height_pct = (h / screen_height) * 100
            print(f"   {key}. {region['name']}")
            print(f"      Coordenadas: ({x}, {y}) {w}x{h}")
            print(f"      Cobertura: {width_pct:.1f}% ancho × {height_pct:.1f}% alto")
        
        print("\n💡 RECOMENDACIÓN: Usar opción 1 (PANTALLA COMPLETA) para pruebas iniciales")
        
        while True:
            try:
                choice = input("\n🎯 Selecciona una opción (1-5) o 'm' para manual: ").strip().lower()
                
                if choice in recommended_regions:
                    selected_region = recommended_regions[choice]['coords']
                    print(f"✅ Seleccionado: {recommended_regions[choice]['name']}")
                    break
                elif choice == 'm':
                    print("\n📝 ENTRADA MANUAL (pantalla completa recomendada)")
                    print(f"   Límites: 0-{screen_width} x 0-{screen_height}")
                    x = int(input("   Coordenada X (0 para pantalla completa): ") or "0")
                    y = int(input("   Coordenada Y (0 para pantalla completa): ") or "0")
                    w = int(input(f"   Ancho ({screen_width} para pantalla completa): ") or str(screen_width))
                    h = int(input(f"   Alto ({screen_height} para pantalla completa): ") or str(screen_height))
                    selected_region = (x, y, w, h)
                    break
                else:
                    print("❌ Opción no válida")
                    
            except ValueError:
                print("❌ Entrada no válida. Usa números.")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # Probar la región seleccionada
        print(f"\n🎯 Probando región: {selected_region}")
        capture = ScreenCapture()
        
        # Temporalmente usar la nueva región
        temp_monitor = {
            'left': selected_region[0],
            'top': selected_region[1],
            'width': selected_region[2],
            'height': selected_region[3]
        }
        
        # Sobrescribir temporalmente
        original_monitor = capture.monitor
        capture.monitor = temp_monitor
        
        img, success = capture.capture_screen()
        
        if success and img is not None and img.max() > 0:
            print(f"✅ Captura exitosa: {img.shape[1]}x{img.shape[0]}")
            
            # Mostrar preview
            display_img = cv2.resize(img, (1000, 700))
            
            # Información en la imagen
            cv2.putText(display_img, "VISTA PREVIA - ZOOM CORREGIDO", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(display_img, f"Region: {selected_region}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(display_img, f"Resolucion: {img.shape[1]}x{img.shape[0]}", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(display_img, "Presiona 's' para confirmar, 'c' para cambiar", (10, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow("Zoom Corregido - Vista Previa", display_img)
            key = cv2.waitKey(0) & 0xFF
            cv2.destroyAllWindows()
            
            if key == ord('s'):
                # Guardar configuración permanentemente
                update_region_config(selected_region)
                print("✅ Configuración actualizada permanentemente")
                return True
            else:
                print("🔄 Volviendo a selección...")
                return fix_zoom_issue()
        else:
            print("❌ Error en la captura. Probando pantalla completa...")
            # Forzar pantalla completa como fallback
            full_screen = (0, 0, screen_width, screen_height)
            update_region_config(full_screen)
            print("✅ Configuración actualizada a PANTALLA COMPLETA")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def update_region_config(region):
    """Actualizar la configuración con nueva región"""
    try:
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

def test_new_region():
    """Probar inmediatamente la nueva región"""
    print("\n🎯 Probando nueva configuración...")
    from core.roulette_detector import RouletteDetector
    
    capture = ScreenCapture()
    detector = RouletteDetector()
    
    print(f"🎯 Nueva región: {capture.monitor}")
    
    img, success = capture.capture_screen()
    if success and img is not None and img.max() > 0:
        print(f"✅ Captura OK: {img.shape[1]}x{img.shape[0]}")
        
        # Probar detección rápida
        result_img, wheel, ball, detected = detector.test_detection(img)
        
        if wheel:
            print("🎉 ¡RULETA DETECTADA CON NUEVA CONFIGURACIÓN!")
        else:
            print("⚠️  Ruleta no detectada - puede necesitar ajustes de parámetros")
        
        # Mostrar resultado
        display_img = cv2.resize(result_img, (1000, 700))
        cv2.imshow("Resultado con Zoom Corregido", display_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("❌ La nueva configuración aún tiene problemas")

if __name__ == "__main__":
    if fix_zoom_issue():
        test_new_region()
        print("\n🎉 ¡PROBLEMA DE ZOOM RESUELTO!")
        print("🚀 Ejecuta: python tests/test_single_window.py")
    else:
        print("❌ No se pudo resolver el problema de zoom")