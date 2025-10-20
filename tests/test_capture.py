import sys
import os

# Agregar la carpeta raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.screen_capture import ScreenCapture

def main():
    print("🎥 Iniciando prueba de captura de pantalla...")
    
    try:
        capture = ScreenCapture()
        print("✅ Módulo de captura inicializado correctamente")
        
        # Probar captura única
        print("📸 Probando captura única...")
        img, success = capture.capture_screen()
        
        if success:
            print(f"✅ Captura exitosa - Resolución: {img.shape[1]}x{img.shape[0]}")
            
            # Probar captura continua
            input("Presiona Enter para iniciar prueba de captura continua (5 segundos)...")
            capture.test_capture(duration=5)
            
        else:
            print("❌ Falló la captura de pantalla")
            
    except Exception as e:
        print(f"❌ Error en prueba de captura: {e}")

if __name__ == "__main__":
    main()