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