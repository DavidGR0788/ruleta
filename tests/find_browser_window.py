import sys
import os
import cv2
import pyautogui

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.screen_capture import ScreenCapture

def find_browser_window():
    """Encontrar y mostrar todas las ventanas disponibles"""
    print("🔍 Buscando ventanas del navegador...")
    
    try:
        # Obtener información de la pantalla
        screen_width, screen_height = pyautogui.size()
        print(f"📺 Resolución de pantalla: {screen_width}x{screen_height}")
        
        # Mostrar áreas comunes donde podría estar la ruleta
        common_regions = {
            'Mitad izquierda': (0, 0, screen_width//2, screen_height),
            'Mitad derecha': (screen_width//2, 0, screen_width//2, screen_height),
            'Centro': (screen_width//4, screen_height//4, screen_width//2, screen_height//2),
            'Navegador típico': (100, 100, 1200, 800),
            'Cuarto superior izquierdo': (0, 0, screen_width//2, screen_height//2),
            'Cuarto superior derecho': (screen_width//2, 0, screen_width//2, screen_height//2),
            'Cuarto inferior izquierdo': (0, screen_height//2, screen_width//2, screen_height//2),
            'Cuarto inferior derecho': (screen_width//2, screen_height//2, screen_width//2, screen_height//2)
        }
        
        capture = ScreenCapture()
        
        print("📸 Probando diferentes regiones...")
        print("💡 Instrucciones:")
        print("   - Presiona 's' para SELECCIONAR la región actual")
        print("   - Presiona 'n' para ver la SIGUIENTE región") 
        print("   - Presiona 'q' para SALIR")
        
        for region_name, (x, y, w, h) in common_regions.items():
            print(f"\n🎯 Probando: {region_name} - {x},{y} {w}x{h}")
            
            img, success = capture.capture_region((x, y, w, h))
            if success:
                # Mostrar la región
                display_img = cv2.resize(img, (800, 600))
                cv2.putText(display_img, region_name, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(display_img, f"Pos: {x},{y} Size: {w}x{h}", (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(display_img, "Presiona 's' para seleccionar, 'n' para siguiente", (10, 110), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                cv2.imshow("Seleccionar Region del Navegador", display_img)
                key = cv2.waitKey(0) & 0xFF
                cv2.destroyAllWindows()
                
                if key == ord('s'):
                    print(f"✅ Región seleccionada: {region_name}")
                    return (x, y, w, h)
                elif key == ord('q'):
                    print("⏹️ Salida solicitada por usuario")
                    break
                # Si presiona 'n' o cualquier otra tecla, continúa con la siguiente región
        
        print("❌ No se seleccionó ninguna región")
        return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    selected_region = find_browser_window()
    if selected_region:
        print(f"🎯 Región guardada: {selected_region}")
        # Guardar en configuración
        import json
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_file = os.path.join(project_root, 'config', 'settings.json')
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        config['capture']['region'] = selected_region
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
        
        print("✅ Configuración actualizada en settings.json")
    else:
        print("❌ No se seleccionó región")