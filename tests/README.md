# Tests para YALA

Este directorio contiene las pruebas unitarias y de rendimiento para el sistema YALA.

## Estructura

```
tests/
├── conftest.py             # Configuración común para pytest
├── run_tests.py            # Script para ejecutar pruebas con cobertura
├── performance/            # Pruebas de rendimiento con Locust
│   ├── locustfile.py       # Definición de pruebas de rendimiento
│   └── run_performance_tests.py  # Script para ejecutar pruebas de rendimiento
└── unit/                   # Pruebas unitarias con pytest
    ├── test_account_service.py
    ├── test_auth_service.py
    ├── test_exchange_service.py
    ├── test_transaction_service.py
    └── test_user_service.py
```

## Pruebas Unitarias

Las pruebas unitarias están implementadas con pytest y se centran en verificar el correcto funcionamiento de los servicios.

### Ejecutar Pruebas Unitarias

Para ejecutar las pruebas unitarias con un reporte de cobertura:

```bash
python tests/run_tests.py
```

Esto ejecutará todas las pruebas unitarias y generará un reporte de cobertura de código en formato de consola y HTML.

### Reporte de Cobertura

El reporte de cobertura HTML se genera en el directorio `tests/coverage_html/`. Puedes abrirlo con cualquier navegador para ver detalles de la cobertura.

## Pruebas de Rendimiento

Las pruebas de rendimiento están implementadas con Locust y simulan usuarios realizando operaciones como:

- Depósitos en cuentas PEN y USD
- Transferencias entre monedas (PEN a USD y viceversa)
- Consultas de tipos de cambio
- Consultas de transacciones y detalles de cuenta

### Configuración para las Pruebas de Rendimiento

Para las pruebas de rendimiento, se ha implementado un servicio mock (`exchange_service_mock.py`) que simula la API de tipos de cambio con un retraso de 500ms, como se solicitó en los requerimientos.

### Ejecutar Pruebas de Rendimiento

Para ejecutar las pruebas de rendimiento en modo headless:

```bash
python tests/performance/run_performance_tests.py --users 100 --spawn-rate 10 --runtime 300
```

Parámetros:
- `--users`: Número máximo de usuarios simultáneos (por defecto: 10)
- `--spawn-rate`: Tasa de creación de usuarios por segundo (por defecto: 1)
- `--runtime`: Duración de la prueba en segundos (por defecto: 60)

### Interfaz Web de Locust

Para ejecutar las pruebas de rendimiento con la interfaz web de Locust:

```bash
locust -f tests/performance/locustfile.py --host http://localhost:8000
```

Luego, abre un navegador en `http://localhost:8089` para acceder a la interfaz de Locust.

### Verificación de Consistencia

Al finalizar las pruebas de rendimiento, se verifica automáticamente la consistencia de la base de datos, comparando el estado final con las operaciones realizadas durante las pruebas.

## Nota Importante

Asegúrate de que la aplicación esté en ejecución antes de ejecutar las pruebas de rendimiento:

```bash
python main.py
``` 