import sys
import os
import cv2
import pyautogui
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.screen_capture import ScreenCapture

def select_region_manual():
    """Selección MANUAL de la región donde está la ruleta"""
    print("🎯 SELECCIÓN MANUAL DE REGIÓN")
    print("=" * 50)
    
    try:
        # Mostrar información de pantalla
        screen_width, screen_height = pyautogui.size()
        print(f"📺 Resolución de pantalla: {screen_width}x{screen_height}")
        
        # Instrucciones claras
        print("\n💡 INSTRUCCIONES:")
        print("1. Coloca la ruleta visible en tu pantalla")
        print("2. Usa las coordenadas para definir la región")
        print("3. Puedes usar estas regiones predefinidas o ingresar coordenadas manuales")
        
        # Regiones predefinidas basadas en resolución común 1366x768
        predefined_regions = {
            '1': {'name': 'Navegador izquierdo', 'coords': (0, 0, 683, 768)},
            '2': {'name': 'Navegador derecho', 'coords': (683, 0, 683, 768)},
            '3': {'name': 'Navegador centro', 'coords': (341, 0, 684, 768)},
            '4': {'name': 'Mitad superior', 'coords': (0, 0, 1366, 384)},
            '5': {'name': 'Mitad inferior', 'coords': (0, 384, 1366, 384)},
            '6': {'name': 'Cuarto superior izquierdo', 'coords': (0, 0, 683, 384)},
            '7': {'name': 'Cuarto superior derecho', 'coords': (683, 0, 683, 384)},
            '8': {'name': 'Cuarto inferior izquierdo', 'coords': (0, 384, 683, 384)},
            '9': {'name': 'Cuarto inferior derecho', 'coords': (683, 384, 683, 384)}
        }
        
        print("\n📋 REGIONES PREDEFINIDAS:")
        for key, region in predefined_regions.items():
            x, y, w, h = region['coords']
            print(f"   {key}. {region['name']} - ({x}, {y}) {w}x{h}")
        
        print("\n🔧 OPCIÓN MANUAL: 0")
        
        while True:
            try:
                choice = input("\n🎯 Selecciona una opción (0-9): ").strip()
                
                if choice == '0':
                    # Entrada manual
                    print("\n📝 ENTRADA MANUAL DE COORDENADAS")
                    print("   Formato: x y ancho alto")
                    print(f"   Ejemplo: 100 50 800 600")
                    print(f"   Límites: 0-{screen_width} x 0-{screen_height}")
                    
                    coords_input = input("   Ingresa coordenadas (x y ancho alto): ").strip()
                    coords = tuple(map(int, coords_input.split()))
                    
                    if len(coords) == 4:
                        x, y, w, h = coords
                        if (0 <= x < screen_width and 0 <= y < screen_height and 
                            w > 0 and h > 0 and x + w <= screen_width and y + h <= screen_height):
                            region = (x, y, w, h)
                            break
                        else:
                            print("❌ Coordenadas fuera de los límites de la pantalla")
                    else:
                        print("❌ Formato incorrecto. Deben ser 4 números")
                
                elif choice in predefined_regions:
                    region = predefined_regions[choice]['coords']
                    break
                else:
                    print("❌ Opción no válida")
                    
            except ValueError:
                print("❌ Entrada no válida. Usa números solamente.")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # Probar la región seleccionada
        print(f"\n🎯 Probando región seleccionada: {region}")
        capture = ScreenCapture()
        
        img, success = capture.capture_region(region)
        if success:
            # Mostrar preview
            display_img = cv2.resize(img, (800, 600))
            x, y, w, h = region
            cv2.putText(display_img, "REGION SELECCIONADA", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(display_img, f"Coords: ({x}, {y}) {w}x{h}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(display_img, "Presiona 's' para confirmar, 'c' para cambiar", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow("Confirmar Region", display_img)
            key = cv2.waitKey(0) & 0xFF
            cv2.destroyAllWindows()
            
            if key == ord('s'):
                print("✅ Región confirmada!")
                return region
            else:
                print("🔄 Volviendo a selección...")
                return select_region_manual()
        else:
            print("❌ Error capturando la región")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def update_config(region):
    """Actualizar la configuración con la nueva región"""
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

if __name__ == "__main__":
    print("🎰 CONFIGURADOR DE REGIÓN DE RULETA")
    print("=" * 50)
    
    selected_region = select_region_manual()
    
    if selected_region:
        if update_config(selected_region):
            print("\n🎉 ¡CONFIGURACIÓN COMPLETADA!")
            print("📍 Ahora el sistema capturará solo la región seleccionada")
            print("🚀 Ejecuta: python tests/test_detector_live.py")
        else:
            print("❌ Error guardando la configuración")
    else:
        print("❌ No se seleccionó ninguna región")