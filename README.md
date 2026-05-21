# E-commerce Backend (Django) - Setup y Estructura Base

Este es el backend para el proyecto de E-commerce, desarrollado con Django y Django REST Framework.

## Requisitos Previos

Asegúrate de tener instalado Python 3.10 o superior.

## Configuración del Entorno de Desarrollo (Clase 1 - Dev 1)

Sigue estos pasos para inicializar el proyecto en tu máquina local:

### 1. Clonar el repositorio y acceder al directorio

```bash
cd Proyecto_Ecommerce
```

### 2. Crear y activar el entorno virtual (venv)

En Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

En macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar las dependencias del proyecto

Una vez activado el entorno virtual, instala las dependencias desde el archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Configurar y Migrar la Base de Datos (SQLite)

El proyecto está configurado para utilizar SQLite en desarrollo local. Aplica las migraciones necesarias para crear el esquema inicial:

```bash
python manage.py migrate
```

Esto creará el archivo de base de datos local `db.sqlite3` y aplicará las tablas de la tienda, de la autenticación básica y de los tokens de Django REST Framework.

### 5. Crear un Superusuario para el panel de administración

Para acceder al panel de administración de Django (`/admin/`), puedes crear un superusuario. 
Para pruebas locales rápidas, ya se ha creado un superusuario por defecto con los siguientes datos:

* **Usuario**: `admin`
* **Contraseña**: `adminpass`
* **Email**: `admin@example.com`

Si deseas crear otro superusuario personalizado, ejecuta:

```bash
python manage.py createsuperuser
```

### 6. Levantar el servidor de desarrollo

Para iniciar el servidor de desarrollo de Django, ejecuta:

```bash
python manage.py runserver
```

El servidor estará disponible en [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

* **API Base**: [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)
* **Django Admin**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## Estructura del Proyecto

* **[kr_cases_project](file:///c:/Users/rsosa/Desktop/luego%20eliminar/prueba_antigravity/Proyecto_Ecommerce/kr_cases_project)**: Configuración principal del proyecto Django, incluyendo variables de entorno, middleware, y mapeo de URLs globales.
* **[store](file:///c:/Users/rsosa/Desktop/luego%20eliminar/prueba_antigravity/Proyecto_Ecommerce/store)**: Aplicación principal de la tienda.
  * `models.py`: Definición del modelo de datos (Productos, Variantes, Órdenes, Cupones, Reseñas).
  * `views.py`: Vistas REST para el procesamiento de pagos, listado de productos, y reviews.
  * `serializers.py`: Serialización de datos de entrada/salida para las APIs.
  * `urls.py`: Rutas secundarias para los endpoints del backend.
  * `utils.py`: Herramientas auxiliares, como la generación de facturas en PDF.
