"""
Script para tomar screenshot del dashboard con Playwright
"""

from playwright.sync_api import sync_playwright
import time
from pathlib import Path

def take_dashboard_screenshot(url="http://localhost:8505", output_path="dashboard_screenshot.png"):
    """
    Toma un screenshot del dashboard
    
    Args:
        url: URL del dashboard
        output_path: Ruta donde guardar el screenshot
    """
    with sync_playwright() as p:
        # Lanzar navegador (headless para no abrir ventana)
        browser = p.chromium.launch(headless=True)
        
        # Crear contexto con viewport específico
        context = browser.new_context(
            viewport={'width': 1440, 'height': 900},
            device_scale_factor=1
        )
        
        # Nueva página
        page = context.new_page()
        
        print(f"Navegando a {url}...")
        page.goto(url)
        
        # Esperar a que cargue el contenido
        print("Esperando que cargue el dashboard...")
        page.wait_for_load_state("networkidle")
        time.sleep(3)  # Espera adicional para que se carguen todos los elementos
        
        # Tomar screenshot
        print(f"Tomando screenshot...")
        page.screenshot(path=output_path, full_page=False)
        
        print(f"Screenshot guardado en: {output_path}")
        
        # Cerrar
        browser.close()
        
        return output_path

if __name__ == "__main__":
    # Crear carpeta para screenshots si no existe
    screenshots_dir = Path(__file__).parent / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)
    
    # Tomar screenshot
    output_file = screenshots_dir / "dashboard_current.png"
    take_dashboard_screenshot(output_path=str(output_file))
    
    print(f"\n✅ Screenshot completo guardado en: {output_file}")
    print(f"Puedes verlo en: {output_file.absolute()}")