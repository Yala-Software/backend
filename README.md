# 💸 YALA - Sistema de Gestión de Cuentas y Transacciones
![Uso de la aplicación](./images/09.jpeg)
## 📋 Descripción del Proyecto

YALA es una plataforma financiera integral diseñada para simplificar la gestión de finanzas personales e internacionales. Nuestra aplicación permite a los usuarios:

- 💼 **Gestionar múltiples cuentas** en diferentes divisas desde una interfaz unificada
- 🔄 **Realizar transferencias instantáneas** entre cuentas propias y de terceros
- 💱 **Conversión automática de monedas** con tasas de cambio actualizadas en tiempo real
- 📊 **Seguimiento detallado** de todas las transacciones y movimientos financieros
- 🔐 **Seguridad avanzada** mediante autenticación JWT y notificaciones por correo electrónico

Desarrollada con tecnologías modernas como FastAPI y sistemas robustos de autenticación, YALA proporciona una experiencia fluida y segura para todas tus necesidades de transferencias nacionales e internacionales.

---
<details>
  <summary><strong>🚀 Configuración Inicial</strong></summary>

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
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=proyectodbp1@gmail.com
SMTP_PASSWORD=nsfr upkz ajfa ptar
EMAIL_FROM=proyectodbp1@gmail.com

EXCHANGE_API1_KEY=  # Se obtiene registrándose en https://www.exchangerate-api.com/
EXCHANGE_API2_KEY=  # No es necesario configurar esta variable
```

### 5️⃣ Ejecutar el servidor de desarrollo
```bash
uvicorn main:app --reload
```
</details>

---

<details>
  <summary><strong>⚙️ Requisitos de Implementación</strong></summary>

La implementación de transacciones debería:

1. ✅ Validar que la cuenta de origen pertenece al usuario actual
2. 💰 Comprobar si hay saldo suficiente en la cuenta de origen
3. 🔄 Utilizar el servicio de cambio para calcular la tasa de conversión si las monedas son diferentes
4. 📊 Actualizar los saldos de ambas cuentas
5. 📝 Crear un registro de transacción
6. 📧 Enviar notificaciones por correo electrónico tanto al remitente como al destinatario
</details>

---

<details>
  <summary><strong>🗄️ Esquema de Base de Datos</strong></summary>

- **👤 users**: Información de usuario (id, username, email, hashed_password, full_name)
- **💵 currencies**: Información de monedas (id, code, name)
- **🏦 accounts**: Cuentas de usuario (id, user_id, currency_id, balance)
- **💱 transactions**: Registros de transacciones (id, sender_id, receiver_id, source_account_id, destination_account_id, etc.)
</details>

---

<details>
  <summary><strong>🧪 Tutorial Bruno</strong></summary>

- **📁 collection**: una vez descargada la aplicación, haz clic en los 3 puntos en la esquina derecha de la aplicación, al costado del perro. Ahí selecciona **Open Collection** y elige la carpeta **YALA-test**
- **🔧 environment**: Una vez abierta la carpeta en Bruno, haz clic en la carpeta y luego selecciona un **environment**. Como no habrá ninguno, selecciona "create environment" y agrega la variable **jwt** en **Add Variable**.
</details>

---

<details>
  <summary><strong>📱 Uso visual de la aplicación</strong></summary>

Se presenta un recorrido por las secciones del frontend:

### **Visualización en la Aplicación:**
![Uso de la aplicación](./images/01.png)
![Uso de la aplicación](./images/02.png)
![Uso de la aplicación](./images/03.png)
![Uso de la aplicación](./images/04.png)
![Uso de la aplicación](./images/05.png)
![Uso de la aplicación](./images/06.png)

</details>
<h2 align="center">¡Cuéntanos! ¿Ya la tienes?</h2>

![Uso de la aplicación](./images/10.jpeg)
