# Ecommerce API

Welcome to the **Ecommerce API**. This project provides a robust and
scalable RESTful API for managing an e-commerce platform, including
products, users, shopping carts, orders, and payments.

The API is designed with clean architecture principles, performance in
mind, and is suitable both for learning purposes and as a foundation for
real-world projects.

------------------------------------------------------------------------

## General Information

-   **Current Version**: 1.1.1
-   **Release Date**: January 2026
-   **License**: MIT
-   **Author**: Carlos Alberto Guzmán\
    📧 Email: carlos.guzmanscg7@gmail.com\
    🔗 GitHub: https://github.com/boicotdev

------------------------------------------------------------------------

## Key Features

-   **Product Management**\
    Create, retrieve, update, and delete products.

-   **User Management**\
    User registration, authentication, and profile management.

-   **Shopping Cart**\
    Add, update, and remove products from the cart.

-   **Orders**\
    Create and manage customer orders.

-   **Payments**\
    Track payment status and order fulfillment.

------------------------------------------------------------------------

## Technology Stack

-   **Backend**: Django + Django REST Framework (DRF)
-   **Database**: PostgreSQL
-   **Authentication**: Token Authentication / JWT (JSON Web Tokens)

------------------------------------------------------------------------

## Requirements

-   Python 3.10 or higher
-   Django 4.9 or higher
-   PostgreSQL
-   Django REST Framework

------------------------------------------------------------------------

## Installation

1.  **Clone the repository**

``` bash
git clone https://github.com/boicotdev/Ecommerce-API-V2.git
```

2.  **Navigate to the project directory**

``` bash
cd Ecommerce-API-V2
```

3.  **Create and activate a virtual environment**

``` bash
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
```

4.  **Install dependencies**

``` bash
pip install -r requirements.txt
```

5.  **Configure environment variables**

Create a `.env` file and define variables such as database name, user
credentials, secret key, etc.

6.  **Apply database migrations**

``` bash
python manage.py migrate
```

7.  **Create a superuser**

``` bash
python manage.py createsuperuser
```

8.  **Run the development server**

``` bash
python manage.py runserver
```

------------------------------------------------------------------------

## API Endpoints

### Authentication

-   User login
-   User registration
-   Token / JWT handling

### Products

-   List products
-   Retrieve product details
-   Create, update, and delete products

### Categories

-   Manage product categories

### Orders

-   Create orders
-   View order history
-   Update order status

### Payments

-   Manage payment status
-   Track order fulfillment

------------------------------------------------------------------------

## Versioning

The API follows semantic versioning:

    MAJOR.MINOR.PATCH

------------------------------------------------------------------------

## License

This project is licensed under the **MIT License**. You are free to use,
modify, and distribute it.

------------------------------------------------------------------------

## Contributions

Contributions are welcome! Feel free to open issues or submit pull
requests.

------------------------------------------------------------------------

## Disclaimer

This project is intended for educational and development purposes and
may require additional security and optimization for production use.
