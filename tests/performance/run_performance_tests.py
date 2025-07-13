import os
import sys
import time
import subprocess
import argparse
from pathlib import Path

def run_performance_tests(users=10, spawn_rate=1, runtime=60):
    """
    Ejecuta pruebas de rendimiento usando Locust
    
    Args:
        users (int): Número máximo de usuarios simultáneos
        spawn_rate (int): Tasa de creación de usuarios por segundo
        runtime (int): Tiempo de ejecución en segundos
    """
    print(f"Ejecutando pruebas de rendimiento con {users} usuarios, {spawn_rate} usuarios/seg, durante {runtime} segundos...")
    
    # Directorio de este script
    script_dir = Path(__file__).resolve().parent
    
    # Comando para ejecutar locust en modo no-web (headless)
    cmd = [
        "locust",
        "-f", os.path.join(script_dir, "locustfile.py"),
        "--headless",
        "--users", str(users),
        "--spawn-rate", str(spawn_rate),
        "--run-time", f"{runtime}s",
        "--host", "http://localhost:8000"
    ]
    
    # Ejecutar locust
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Mostrar la salida en tiempo real
        while process.poll() is None:
            output = process.stdout.readline()
            if output:
                print(output.strip())
        
        # Mostrar cualquier error
        stderr = process.stderr.read()
        if stderr:
            print(f"Errores: {stderr}")
        
        # Obtener código de salida
        exit_code = process.returncode
        if exit_code != 0:
            print(f"Las pruebas de rendimiento fallaron con código de salida {exit_code}")
        else:
            print("Pruebas de rendimiento completadas con éxito")
        
    except Exception as e:
        print(f"Error al ejecutar las pruebas: {str(e)}")
    
    print("\nINFORME DE RESULTADOS:")
    print("====================")
    print("Para ver gráficos detallados, ejecute locust con la interfaz web:")
    print("locust -f tests/performance/locustfile.py --host http://localhost:8000")

if __name__ == "__main__":
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Ejecutar pruebas de rendimiento con Locust")
    parser.add_argument("--users", type=int, default=10, help="Número máximo de usuarios simultáneos")
    parser.add_argument("--spawn-rate", type=int, default=1, help="Tasa de creación de usuarios por segundo")
    parser.add_argument("--runtime", type=int, default=60, help="Tiempo de ejecución en segundos")
    
    args = parser.parse_args()
    
    # Ejecutar las pruebas
    run_performance_tests(args.users, args.spawn_rate, args.runtime) 