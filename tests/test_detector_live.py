import sys
import os

# Agregar la carpeta raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.screen_capture import ScreenCapture
from core.roulette_detector import RouletteDetector

def main():
    print("🎯 Iniciando prueba de detección de ruleta en vivo...")
    
    try:
        # Inicializar capturador y detector
        capture = ScreenCapture()
        detector = RouletteDetector()
        
        print("✅ Módulos inicializados correctamente")
        
        # Ejecutar prueba en vivo
        detector.live_detection_test(capture, duration=15)
            
    except Exception as e:
        print(f"❌ Error en prueba de detección: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()