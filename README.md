# Ecommerce API

Bienvenido a la **Ecommerce API**. Esta API permite gestionar productos, usuarios, carritos de compras, pedidos, y más, en una plataforma de ecommerce.

### General:
- **Versiones**:
    Versión actual: 1.0.0
    Fecha de lanzamiento: Octubre 2024
- **Licencia**: M.I.T.
- **Desarrollador**: Carlos Alberto Guzmán, carlos.guzmanscg7@gmail.com y enlace a GitHub.


## Características principales
- **Gestión de productos**: Crear, leer, actualizar y eliminar productos.
- **Gestión de usuarios**: Registro de usuarios, inicio de sesión y manejo de perfiles.
- **Carrito de compras**: Agregar y eliminar productos del carrito.
- **Pedidos**: Crear y gestionar pedidos.
- **Pago**: Gestión de estados de pago y seguimiento de pedidos.

## Tecnologías
- **Backend**: Django + Django REST Framework (DRF)
- **Base de datos**: PostgreSQL
- **Autenticación**: Token Authentication / JWT (Json Web Tokens)
  
## Requisitos
- Python 3.8 o superior
- Django 3.2 o superior
- PostgreSQL
- Django REST Framework

## Instalación

1. Clona este repositorio:

   ```bash
   git clone https://github.com/usuario/ecommerce-api.git

2. Navega al directorio del proyecto:
   ```bash
   cd ecommerce-api

3. Crea y activa un entorno virtual:
    ```bash
   python -m venv env
    source env/bin/activate  # En Windows usa: env\Scripts\activate

4. Instala las dependencias:
    ```bash
    pip install -r requirements.txt

5. Configura las variables de entorno en un archivo .env (como el nombre de la base de datos, credenciales de usuario, etc.).

6. Realiza las migraciones:
    ```bash
    python manage.py migrate

7. Crea un superusuario para acceder al panel de administración:
    ```bash
   python manage.py createsuperuser

8. Inicia el servidor de desarrollo:
    ```bash
   python manage.py runserver


# Endpoints

### Autenticación

### Productos

### Categorias

### Ordenes

### Pagos
