# 🪙 AppCoin Backend

Este es el backend de la API de un sistema de monedero digital, desarrollado con el framework Flask de Python. La API maneja la gestión de usuarios, cuentas, préstamos y transacciones, proporcionando una base sólida para una plataforma financiera descentralizada.

## 🚀 Características Principales
- **Autenticación JWT**: Seguridad en los endpoints mediante tokens de acceso.
- **Gestión de Usuarios y Roles**: Diferentes permisos para usuarios, administradores y superadministradores.
- **Manejo de Cuentas**: Creación y gestión de cuentas de usuario.
- **Transacciones**: Endpoints para transferencias entre cuentas, así como inyección y retiro de monedas por el administrador.
- **Préstamos**: Funcionalidad para solicitar, aprobar y pagar préstamos.
- **Control de Errores**: Manejo de excepciones y respuestas claras de la API.

## 🛠️ Requisitos e Instalación

### Requisitos Previos
Asegúrate de tener instalado lo siguiente en tu sistema:
- Python 3.x
- PIP (gestor de paquetes de Python)
- MySQL (para la base de datos)
- Postman (o una herramienta similar para probar la API)

### Pasos de Instalación
1. Clonar el repositorio:
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd <NOMBRE_DE_TU_CARPETA>
   ```

2. Crear y activar un entorno virtual (opcional, pero recomendado):
   ```bash
   python -m venv venv
   # En Windows
   venv\Scripts\activate
   # En macOS/Linux
   source venv/bin/activate
   ```

3. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configurar la base de datos:
   - Crea una base de datos MySQL.
   - Actualiza las credenciales de la base de datos en el archivo de configuración (config.py o similar).
   - Ejecuta el script SQL para crear las tablas necesarias (el script se encuentra en la carpeta `database/schema.sql`).

## 🏃 Ejecución del Servidor
Para iniciar el servidor de desarrollo de Flask, ejecuta el siguiente comando:
```bash
flask run
```
El servidor estará disponible en `http://127.0.0.1:5000`.

## 📚 Endpoints de la API
A continuación se listan los principales endpoints de la API. Se requiere un token JWT en el encabezado `Authorization: Bearer <token>` para los endpoints protegidos.

| Método | Endpoint                     | Descripción                                      |
|--------|------------------------------|--------------------------------------------------|
| POST   | /api/users/register          | Registra un nuevo usuario.                        |
| POST   | /api/users/login             | Inicia sesión y obtiene un token JWT.            |
| GET    | /api/accounts/balance        | Consulta el saldo de la cuenta del usuario autenticado. |
| POST   | /api/loans/request           | Solicita un nuevo préstamo.                      |
| POST   | /api/loans/repay             | Realiza un pago a un préstamo.                   |
| POST   | /api/admin/inject_coins      | (Admin) Inyecta o retira monedas del sistema.   |
| POST   | /api/transactions/transfer   | Transfiere monedas entre dos cuentas.            |

## 🧑‍💻 Autores
Tu Nombre - [link a tu GitHub o LinkedIn]

## 📄 Licencia
Este proyecto está bajo la Licencia MIT.

--- 
