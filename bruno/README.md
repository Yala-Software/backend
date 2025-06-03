# Colecciones de Bruno para la API de Intercambio de Monedas

Esta carpeta contiene colecciones para [Bruno](https://www.usebruno.com/), una herramienta de código abierto para probar APIs.

## Cómo usar

1. Descarga e instala Bruno desde [usebruno.com](https://www.usebruno.com/)
2. Abre Bruno y selecciona "Abrir una colección"
3. Navega hasta esta carpeta y selecciona los archivos .bruno

## Colecciones disponibles

* **auth.bruno** - Endpoints de autenticación (login y registro)
* **users.bruno** - Endpoints de usuarios
* **accounts.bruno** - Endpoints de cuentas y estados de cuenta
* **exchange.bruno** - Endpoints de tipos de cambio

## Variables de entorno

Algunas solicitudes requieren un token de autenticación. Para configurarlo:

1. Primero ejecuta la solicitud "Iniciar Sesión" para obtener un token
2. Copia el valor del token de la respuesta
3. Ve a la pestaña "Env" (Ambiente) en Bruno
4. Reemplaza "PEGAR_AQUI_TU_TOKEN_DE_ACCESO" con el token copiado

## Flujo de trabajo típico

1. Registra un usuario o inicia sesión para obtener un token
2. Configura el token en el ambiente
3. Consulta la información del usuario
4. Lista las cuentas disponibles
5. Consulta los detalles de una cuenta específica
6. Consulta tipos de cambio o exporta estados de cuenta

## Notas

* Las colecciones están preconfiguradas para una instancia local en `http://localhost:8000`
* Si tu API está en una ubicación diferente, actualiza las URLs en las solicitudes
