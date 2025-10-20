import mss
import mss.tools
import cv2
import numpy as np
import time
from PIL import Image
import json
import os

class ScreenCapture:
    def __init__(self, config_file=None):
        if config_file is None:
            # Buscar config file desde la raíz del proyecto
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_file = os.path.join(project_root, 'config', 'settings.json')
        self.config = self.load_config(config_file)
        self.sct = mss.mss()
        self.setup_capture()
        
    def load_config(self, config_file):
        """Cargar configuración desde archivo JSON"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                print(f"✅ Configuración cargada desde: {config_file}")
                return config
        except Exception as e:
            print(f"❌ Error cargando configuración desde {config_file}: {e}")
            return {}
    
    def setup_capture(self):
        """Configurar la captura (pantalla completa o región específica)"""
        try:
            # Verificar si hay una región específica configurada
            capture_config = self.config.get('capture', {})
            region = capture_config.get('region')
            
            if region and len(region) == 4:
                # Usar región específica - CORREGIDO: coordenadas absolutas
                x, y, width, height = region
                self.monitor = {
                    'left': x,        # ✅ COORDENADAS ABSOLUTAS
                    'top': y,         # ✅ NO se suma con monitor_x/monitor_y
                    'width': width,
                    'height': height
                }
                print(f"🎯 Región específica configurada: {self.monitor}")
            else:
                # Usar monitor completo (comportamiento original)
                monitors = self.sct.monitors
                print("🖥️ Monitores detectados:")
                for i, monitor in enumerate(monitors):
                    print(f"  Monitor {i}: {monitor}")
                
                monitor_id = capture_config.get('monitor', 1)
                self.monitor = monitors[monitor_id]
                
                # Aplicar límite de ancho si está configurado
                max_width = capture_config.get('max_capture_width')
                if max_width and self.monitor['width'] > max_width:
                    scale_factor = max_width / self.monitor['width']
                    self.monitor['width'] = max_width
                    self.monitor['height'] = int(self.monitor['height'] * scale_factor)
                
                print(f"🎯 Monitor seleccionado: {self.monitor}")
            
        except Exception as e:
            print(f"❌ Error configurando captura: {e}")
            # Usar monitor por defecto
            self.monitor = self.sct.monitors[1]
    
    def capture_screen(self):
        """Capturar la pantalla completa o región configurada"""
        try:
            # Capturar según configuración
            screenshot = self.sct.grab(self.monitor)
            
            # Convertir a array de numpy para OpenCV
            img = np.array(screenshot)
            
            # Convertir de BGRA a BGR (OpenCV usa BGR)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            return img, True
            
        except Exception as e:
            print(f"❌ Error capturando pantalla: {e}")
            return None, False
    
    def capture_region(self, region=None):
        """Capturar una región específica de la pantalla (sobrescribe la configuración)"""
        try:
            if region is None:
                return self.capture_screen()
            
            # ✅ CORREGIDO: Usar coordenadas absolutas directamente
            x, y, width, height = region
            
            capture_region = {
                'left': x,        # ✅ COORDENADA ABSOLUTA X
                'top': y,         # ✅ COORDENADA ABSOLUTA Y
                'width': width,
                'height': height
            }
            
            screenshot = self.sct.grab(capture_region)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            return img, True
            
        except Exception as e:
            print(f"❌ Error capturando región: {e}")
            return None, False
    
    def show_preview(self, img, window_name="Captura de Pantalla"):
        """Mostrar una vista previa de la captura en una ventana específica"""
        try:
            # Redimensionar si es muy grande para la pantalla
            height, width = img.shape[:2]
            max_height = 800
            if height > max_height:
                scale = max_height / height
                new_width = int(width * scale)
                img = cv2.resize(img, (new_width, max_height))
            
            cv2.imshow(window_name, img)
            cv2.waitKey(1)  # Actualizar ventana
            
        except Exception as e:
            print(f"❌ Error mostrando preview: {e}")
    
    def test_capture(self, duration=5):
        """Probar la captura de pantalla por un tiempo determinado"""
        print("🧪 Iniciando prueba de captura de pantalla...")
        print("⏰ Duración: 5 segundos")
        print("🛑 Presiona 'q' para salir anticipadamente")
        
        # Crear UNA sola ventana
        window_name = "Prueba de Captura"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        start_time = time.time()
        frame_count = 0
        
        try:
            while time.time() - start_time < duration:
                # Capturar pantalla
                img, success = self.capture_screen()
                
                if success:
                    frame_count += 1
                    
                    # Mostrar información
                    height, width = img.shape[:2]
                    fps = frame_count / (time.time() - start_time)
                    
                    # Mostrar preview en la MISMA ventana
                    display_img = img.copy()
                    cv2.putText(display_img, f"FPS: {fps:.1f}", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(display_img, f"Resolucion: {width}x{height}", (10, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    # Mostrar información de la región
                    region_info = f"Region: {self.monitor['left']},{self.monitor['top']} {self.monitor['width']}x{self.monitor['height']}"
                    cv2.putText(display_img, region_info, (10, 110), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    
                    cv2.imshow(window_name, display_img)
                
                # Salir si se presiona 'q'
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
        
        finally:
            cv2.destroyAllWindows()
        
        print(f"✅ Prueba completada: {frame_count} frames capturados")
        print(f"📊 FPS promedio: {frame_count/duration:.1f}")

    def get_capture_info(self):
        """Obtener información sobre la configuración actual de captura"""
        return {
            'monitor': self.monitor,
            'region_configured': 'region' in self.config.get('capture', {}),
            'config_file': self.config_file if hasattr(self, 'config_file') else 'default'
        }

if __name__ == "__main__":
    # Probar la captura de pantalla
    print("🎯 Iniciando prueba de captura...")
    capture = ScreenCapture()
    
    # Mostrar información de configuración
    info = capture.get_capture_info()
    print(f"📋 Configuración actual: {info}")
    
    # Probar captura
    capture.test_capture()