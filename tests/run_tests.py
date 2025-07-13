import os
import sys
import pytest
import coverage

# Añadir el directorio raíz del proyecto al PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def run_tests_with_coverage():
    """
    Ejecuta todas las pruebas con un reporte de cobertura de código.
    """
    # Iniciar la cobertura
    cov = coverage.Coverage(
        source=['services'],
        omit=['*/__init__.py', '*/email_service.py']  # Omitir archivos de inicialización y servicio de email
    )
    cov.start()

    # Ejecutar las pruebas
    result = pytest.main(['-v', 'tests/unit'])

    # Detener la cobertura
    cov.stop()
    cov.save()

    # Generar informes
    print("\nCoverage Summary:")
    cov.report()
    
    # Generar informe HTML
    cov.html_report(directory='tests/coverage_html')
    
    print(f"\nDetailed HTML coverage report generated in tests/coverage_html/index.html")
    
    return result

if __name__ == '__main__':
    sys.exit(run_tests_with_coverage()) 