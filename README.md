# Sistema Backend de Intercambio de Monedas

Un backend basado en FastAPI para operaciones de intercambio de monedas, que permite múltiples usuarios, cuentas en diferentes monedas y transacciones entre usuarios y monedas.

## Características

- Registro de usuarios y autenticación con JWT
- Múltiples cuentas en diferentes monedas para cada usuario
- Conversión de monedas utilizando dos APIs diferentes con sistema de respaldo
- Sistema de transacciones entre usuarios y monedas
- Estados de cuenta e historial de transacciones
- Notificaciones por correo electrónico para varios eventos
- Funcionalidad de exportación (CSV, XML)
- Patrones de diseño: Singleton, Adapter, Strategy, Observer

## Configuración e Instalación

1. Clona este repositorio
2. Instala los paquetes requeridos:
   ```
   pip install -r requirements.txt
   ```
3. Configura las variables de entorno en el archivo `.env`
4. Ejecuta la aplicación:
   ```
   uvicorn main:app --reload
   ```
5. Accede a la documentación de la API en http://localhost:8000/docs

## Estructura del Proyecto

```
backend/
├── api/
│   └── routes/
│       ├── auth.py          # Endpoints de autenticación
│       ├── users.py         # Endpoints de gestión de usuarios
│       ├── accounts.py      # Endpoints de gestión de cuentas
├── core/
│   ├── security.py          # Utilidades JWT y contraseñas
│   └── exchange/
│       ├── interface.py     # Interfaz de API de cambio
│       ├── api1_adapter.py  # Implementación de adaptador de API de cambio
│       └── api2_adapter.py  # Segunda implementación de adaptador de API de cambio
├── database/
│   ├── database.py          # Configuración de conexión a base de datos
│   └── models.py            # Modelos SQLAlchemy
├── data/                    # Archivos de base de datos SQLite
├── services/
│   ├── exchange_service.py  # Servicio de tipos de cambio
│   └── email_service.py     # Servicio de notificaciones por correo
├── .env                     # Variables de entorno
├── config.py                # Configuración de la aplicación
├── main.py                  # Punto de entrada principal de la aplicación
└── requirements.txt         # Dependencias del proyecto
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

## Patrones de Diseño

Este proyecto utiliza varios patrones de diseño:

1. **Patrón Singleton**: Utilizado para el ExchangeService para asegurar que solo exista una instancia
2. **Patrón Adapter**: Utilizado para las interfaces de API de cambio para unificar múltiples proveedores de API
3. **Patrón Strategy**: Utilizado para cambiar entre diferentes APIs de tipos de cambio
4. **Patrón Observer**: (Por implementar en el sistema de transacciones) Para actualizar el historial de transacciones

## Esquema de Base de Datos

- **users**: Información de usuario (id, username, email, hashed_password, full_name)
- **currencies**: Información de monedas (id, code, name)
- **accounts**: Cuentas de usuario (id, user_id, currency_id, balance)
- **transactions**: Registros de transacciones (id, sender_id, receiver_id, source_account_id, destination_account_id, etc.)