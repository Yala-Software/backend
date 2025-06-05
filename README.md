# YALA - Sistema de Gestión de Cuentas y Transacciones

## Descripción del Proyecto
YALA es una aplicación de gestión financiera que permite a los usuarios administrar cuentas en diferentes monedas, realizar transacciones entre ellas y gestionar tipos de cambio.

## Requisitos Previos
- Python 3.8+ instalado
- Base de datos PostgreSQL
- Gestor de paquetes pip

## Configuración Inicial

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/yala-backend.git
cd yala-backend
```

### 2. Configurar entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:
```
DATABASE_URL=postgresql://usuario:contraseña@localhost/nombre_db
SECRET_KEY=tu_clave_secreta_para_jwt
MAIL_SERVER=smtp.ejemplo.com
MAIL_PORT=587
MAIL_USERNAME=tu_email@ejemplo.com
MAIL_PASSWORD=tu_contraseña
MAIL_FROM=noreply@ejemplo.com
```

### 5. Inicializar la base de datos
```bash
python scripts/init_db.py
```

### 6. Ejecutar el servidor de desarrollo
```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en `http://localhost:8000`

### 7. Documentación API
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Ejecución de pruebas
```bash
pytest
```

## Endpoints de la API

### Autenticación

- **POST /api/login**

  - Descripción: Autenticar usuario y obtener token JWT
  - Cuerpo de la Solicitud:
    ```json
    {
      "username": "string",
      "password": "string"
    }
    ```
  - Respuesta:
    ```json
    {
      "access_token": "string",
      "token_type": "bearer"
    }
    ```

- **POST /api/register**
  - Descripción: Registrar nuevo usuario
  - Cuerpo de la Solicitud:
    ```json
    {
      "username": "string",
      "email": "string",
      "password": "string",
      "full_name": "string"
    }
    ```
  - Respuesta:
    ```json
    {
      "access_token": "string",
      "token_type": "bearer"
    }
    ```

### Usuarios

- **GET /api/users/me**

  - Descripción: Obtener información del usuario actual
  - Encabezado Requerido: `Authorization: Bearer {token}`
  - Respuesta:
    ```json
    {
      "id": 0,
      "username": "string",
      "email": "string",
      "full_name": "string"
    }
    ```

- **GET /api/users/{user_id}**
  - Descripción: Obtener información del usuario por ID
  - Encabezado Requerido: `Authorization: Bearer {token}`
  - Respuesta:
    ```json
    {
      "id": 0,
      "username": "string",
      "email": "string",
      "full_name": "string"
    }
    ```

### Cuentas

- **GET /api/accounts/**

  - Descripción: Obtener todas las cuentas del usuario actual
  - Encabezado Requerido: `Authorization: Bearer {token}`
  - Respuesta:
    ```json
    [
      {
        "id": 0,
        "currency": {
          "id": 0,
          "code": "string",
          "name": "string"
        },
        "balance": 0.0
      }
    ]
    ```

- **GET /api/accounts/{account_id}**

  - Descripción: Obtener detalles de la cuenta con transacciones
  - Encabezado Requerido: `Authorization: Bearer {token}`
  - Respuesta:
    ```json
    {
      "account": {
        "id": 0,
        "currency": {
          "id": 0,
          "code": "string",
          "name": "string"
        },
        "balance": 0.0
      },
      "transactions": [
        {
          "id": 0,
          "source_amount": 0.0,
          "source_currency_id": 0,
          "destination_amount": 0.0,
          "destination_currency_id": 0,
          "exchange_rate": 0.0,
          "description": "string",
          "timestamp": "string"
        }
      ]
    }
    ```

- **POST /api/accounts/{account_id}/export**
  - Descripción: Exportar estado de cuenta (CSV o XML)
  - Encabezado Requerido: `Authorization: Bearer {token}`
  - Parámetros de Consulta: `format=csv` o `format=xml`
  - Respuesta:
    ```json
    {
      "message": "El estado de cuenta ha sido enviado a tu correo electrónico"
    }
    ```

### Tipos de Cambio

- **GET /api/exchange-rates/{from_currency}/{to_currency}**

  - Descripción: Obtener tipo de cambio entre dos monedas
  - Respuesta:
    ```json
    {
      "from": "string",
      "to": "string",
      "rate": 0.0
    }
    ```

- **GET /api/supported-currencies**
  - Descripción: Obtener lista de monedas soportadas
  - Respuesta:
    ```json
    {
      "USD": "Dólar Estadounidense",
      "EUR": "Euro",
      "PEN": "Sol Peruano",
      "...": "..."
    }
    ```

## Endpoints de Transacciones (Por Implementar)

La funcionalidad de transacciones debe ser implementada en un módulo separado. Así es como debería funcionar:

### Endpoints a implementar

- **POST /api/transactions/**

  - Descripción: Crear una nueva transacción
  - Encabezado Requerido: `Authorization: Bearer {token}`
  - Cuerpo de la Solicitud:
    ```json
    {
      "source_account_id": 0,
      "destination_account_id": 0,
      "amount": 0.0,
      "description": "string"
    }
    ```
  - Respuesta:
    ```json
    {
      "id": 0,
      "source_amount": 0.0,
      "source_currency_id": 0,
      "destination_amount": 0.0,
      "destination_currency_id": 0,
      "exchange_rate": 0.0,
      "description": "string",
      "timestamp": "string"
    }
    ```

- **GET /api/transactions/**
  - Descripción: Obtener todas las transacciones del usuario actual
  - Encabezado Requerido: `Authorization: Bearer {token}`
  - Respuesta:
    ```json
    [
      {
        "id": 0,
        "source_amount": 0.0,
        "source_currency_id": 0,
        "destination_amount": 0.0,
        "destination_currency_id": 0,
        "exchange_rate": 0.0,
        "description": "string",
        "timestamp": "string"
      }
    ]
    ```

### Requisitos de Implementación

La implementación de transacciones debería:

1. Validar que la cuenta de origen pertenece al usuario actual
2. Comprobar si hay saldo suficiente en la cuenta de origen
3. Utilizar el servicio de cambio para calcular la tasa de conversión si las monedas son diferentes
4. Actualizar los saldos de ambas cuentas
5. Crear un registro de transacción
6. Enviar notificaciones por correo electrónico tanto al remitente como al destinatario

## Esquema de Base de Datos

- **users**: Información de usuario (id, username, email, hashed_password, full_name)git
- **currencies**: Información de monedas (id, code, name)
- **accounts**: Cuentas de usuario (id, user_id, currency_id, balance)
- **transactions**: Registros de transacciones (id, sender_id, receiver_id, source_account_id, destination_account_id, etc.)

## Tutorial Bruno

- **collection**: una vez descargada la aplicacion apretar en los 3 puntos en la esquina derecha de la aplicacion, al costado del perro. Ahi apretar en **Open Collection** y seleccionar la carpeta **YALA-test**
- **environment**: Una ves abierta la carpeta en bruno, apretar en la carpeta en bruno y luego seleccionar un **environment**, como no habra ninguno seleccionar create environment y agregar la variable **jwt** en **Add Variable**.


## Uso visual de la aplicacion

Se presenta un recorrido por las secciones del frontend

* **Visualización en la Aplicación:**
![Uso de la aplicacion](./images/01.png)
![Uso de la aplicacion](./images/02.png)
![Uso de la aplicacion](./images/03.png)
![Uso de la aplicacion](./images/04.png)
![Uso de la aplicacion](./images/05.png)
![Uso de la aplicacion](./images/06.png)
