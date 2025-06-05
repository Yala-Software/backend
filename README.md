# 💸 YALA - Sistema de Gestión de Cuentas y Transacciones

## 📋 Descripción del Proyecto
YALA es una aplicación de gestión financiera que permite a los usuarios administrar cuentas en diferentes monedas, realizar transacciones entre ellas y gestionar tipos de cambio.

---

## 🚀 Configuración Inicial

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/Yala-Software/backend
cd backend
```

### 2️⃣ Configurar entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3️⃣ Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4️⃣ Configurar variables de entorno
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

### 5️⃣ Ejecutar el servidor de desarrollo
```bash
uvicorn main:app --reload
```

---

## ⚙️ Requisitos de Implementación

La implementación de transacciones debería:

1. ✅ Validar que la cuenta de origen pertenece al usuario actual
2. 💰 Comprobar si hay saldo suficiente en la cuenta de origen
3. 🔄 Utilizar el servicio de cambio para calcular la tasa de conversión si las monedas son diferentes
4. 📊 Actualizar los saldos de ambas cuentas
5. 📝 Crear un registro de transacción
6. 📧 Enviar notificaciones por correo electrónico tanto al remitente como al destinatario

---

## 🗄️ Esquema de Base de Datos

- **👤 users**: Información de usuario (id, username, email, hashed_password, full_name)
- **💵 currencies**: Información de monedas (id, code, name)
- **🏦 accounts**: Cuentas de usuario (id, user_id, currency_id, balance)
- **💱 transactions**: Registros de transacciones (id, sender_id, receiver_id, source_account_id, destination_account_id, etc.)

---

## 🧪 Tutorial Bruno

- **📁 collection**: una vez descargada la aplicación, haz clic en los 3 puntos en la esquina derecha de la aplicación, al costado del perro. Ahí selecciona **Open Collection** y elige la carpeta **YALA-test**
- **🔧 environment**: Una vez abierta la carpeta en Bruno, haz clic en la carpeta y luego selecciona un **environment**. Como no habrá ninguno, selecciona "create environment" y agrega la variable **jwt** en **Add Variable**.

---

## 📱 Uso visual de la aplicación

Se presenta un recorrido por las secciones del frontend:

### **Visualización en la Aplicación:**
![Uso de la aplicación](./images/01.png)
![Uso de la aplicación](./images/02.png)
![Uso de la aplicación](./images/03.png)
![Uso de la aplicación](./images/04.png)
![Uso de la aplicación](./images/05.png)
![Uso de la aplicación](./images/06.png)
