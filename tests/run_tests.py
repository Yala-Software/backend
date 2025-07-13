import os
import sys
import pytest
import coverage

# Añadir el directorio raíz del proyecto al PYTHONPATH
directorio_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, directorio_raiz)

def ejecutar_pruebas_con_cobertura():
    """
    Ejecuta todas las pruebas unitarias con un reporte de cobertura de código.
    """
    # Iniciar la cobertura
    cobertura = coverage.Coverage(
        source=['services'],
        omit=['*/__init__.py', '*/email_service.py']  # Omitir archivos de inicialización y servicio de email
    )
    cobertura.start()

    # Ejecutar las pruebas
    resultado = pytest.main(['-v', 'tests/unit'])

    # Detener la cobertura
    cobertura.stop()
    cobertura.save()

    # Generar informes
    print("\nResumen de Cobertura:")
    cobertura.report()
    
    # Generar informe HTML
    cobertura.html_report(directory='tests/coverage_html')
    
    print(f"\nReporte detallado de cobertura generado en tests/coverage_html/index.html")
    
    return resultado

if __name__ == '__main__':
    sys.exit(ejecutar_pruebas_con_cobertura()) 