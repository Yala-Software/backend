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
git clone https://github.com/Yala-Software/backend
cd backend
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

### 5. Ejecutar el servidor de desarrollo
```bash
uvicorn main:app --reload
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
