from django.db import transaction
from django.shortcuts import get_object_or_404
from products.services.excel_file_handler import ExcelProductParser, ProductBulkCreateService
from products.services.filter_service import ProductFilterService
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView, Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import LimitOffsetPagination

from orders.models import Order, OrderProduct
from reviews import serializers
from users.models import User
from .models import Category, Product, UnitOfMeasure
from carts.models import Cart, ProductCart
from .serializers import (
    ProductSerializer,
    UnitOfMeasureSerializer,
    ProductImportSerializer
)
from carts.serializers import ProductCartSerializer

class ProductFilterAPIView(APIView):
    def get(self, request):
        results = self.get_queryset(request)
        paginator = LimitOffsetPagination()
        paginated_queryset = paginator.paginate_queryset(results, request)
        serializer = ProductSerializer(paginated_queryset, many=True)

        return paginator.get_paginated_response(serializer.data)

    def get_queryset(self, request):
        service = ProductFilterService(request.query_params)
        return service.search()

class UnitOfMeasureView(APIView):
    """
    API view to perform CRUD operations on UnitOfMeasure.
    Only accessible to admin users.
    """
    permission_classes = [IsAdminUser]

    def get(self, request, unit_id=None):
        """
        Retrieve all units of measure or a specific one by ID.
        - If `unit_id` is provided, fetch a single unit.
        - Otherwise, return a list of all units.
        """
        try:
            if unit_id:
                # Fetch a single unit or return a 404 error if not found
                unit = get_object_or_404(UnitOfMeasure, id=unit_id)
                serializer = UnitOfMeasureSerializer(unit)
            else:
                # Fetch all units
                units = UnitOfMeasure.objects.all()
                serializer = UnitOfMeasureSerializer(units, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """
        Create a new unit of measure.
        """
        serializer = UnitOfMeasureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, unit_id):
        """
        Update an existing unit of measure.
        - Uses `partial=True` to allow partial updates.
        - Returns 404 if the unit is not found.
        """
        unit = get_object_or_404(UnitOfMeasure, id=unit_id)
        serializer = UnitOfMeasureSerializer(unit, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, unit_id):
        """
        Delete an existing unit of measure.
        - Returns 204 status if successful.
        - Returns 404 if the unit is not found.
        """
        unit = get_object_or_404(UnitOfMeasure, id=unit_id)
        unit.delete()
        return Response({"message": "Unit of measure successfully deleted"}, status=status.HTTP_204_NO_CONTENT)

class ProductImportView(APIView):
    def post(self, request):
        serializer = ProductImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        excel_file = serializer.validated_data["file"]

        parser = ExcelProductParser()
        products_data = parser.parse(excel_file)

        service = ProductBulkCreateService()
        result = service.execute(products_data)

        return Response({
            "message": "Products imported successfully",
            **result
        }, status=status.HTTP_201_CREATED)


class AdminProductAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, sku=None):
        if sku:
            product = get_object_or_404(Product, sku=sku)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        else:
            queryset = Product.objects.all()
            paginator = LimitOffsetPagination()
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            serializer = ProductSerializer(paginated_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)


    def post(self, request):
        sku = request.data.get("sku", None)
        name = request.data.get("name", None)
        description = request.data.get("description", None)
        price = request.data.get("price", None)
        stock = request.data.get("stock", None)
        category = request.data.get("category_id", None)

        # check if all fields are fulfilled
        if not all([sku, name, description, price, stock, category]):
            return Response({"message": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if Product.objects.filter(sku=sku).exists():
                return Response({"message": f"Product with SKU {sku} already exists"},
                                status=status.HTTP_400_BAD_REQUEST)
            if Product.objects.filter(name = name).exists():
                return Response({"message": f"Product with name {name} already exists"},
                                status=status.HTTP_400_BAD_REQUEST)

            if not Category.objects.filter(pk=category).exists():
                return Response({"message": "Category does not exist!"}, status=status.HTTP_400_BAD_REQUEST)

            # Serialize and save the given product
            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def put(self, request, sku):
        try:
            product = get_object_or_404(Product, sku=sku)
            serializer = ProductSerializer(product, data = request.data, partial = True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status = status.HTTP_200_OK)
            
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"message" : str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


    def delete(self, request, sku):
        product = get_object_or_404(Product, sku=sku)
        product.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


#retrieve all products
class ProductListView(APIView):
    def get(self, request):
        try:
            queryset = Product.objects.all()
            paginator = LimitOffsetPagination()
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            serializer = ProductSerializer(paginated_queryset, many= True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class RetrieveLatestProducts(ListAPIView):
    def get(self, request):
        try:
            queryset = Product.objects.filter(recommended=True)[:3]
            paginator = LimitOffsetPagination()
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            serializer = ProductSerializer(paginated_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)



#retrieve all details of a single product
class ProductDetailsView(APIView):
    def get(self, request):
        sku = request.query_params.get("sku", None)
        
        if not sku:
            return Response({"message":"Sku is required"}, status = status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(sku = sku)
            serializer = ProductSerializer(product)
            return Response(serializer.data, status = status.HTTP_200_OK)

        except Product.DoesNotExist:
            return Response({"message": f"Product with SKU {sku}"}, status = status.HTTP_400_BAD_REQUEST)
            

        except Exception as e:
            return Response({"message" : str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductCartCreateView(APIView):
    def post(self, request):
        cart_id = request.data.get("cart")
        products = request.data.get("products", [])


        # Validación de campos obligatorios
        if not cart_id or not products:
            return Response({"message": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = Cart.objects.get(pk=cart_id)
        except Cart.DoesNotExist:
            return Response(
                {"message": "Cart not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            # Recuperar los productos en una sola consulta
            product_skus = [product["sku"] for product in products]
            products_db = Product.objects.filter(sku__in=product_skus)
            product_map = {product.sku: product for product in products_db}

            # Verificar que todos los SKUs sean válidos
            missing_skus = set(product_skus) - set(product_map.keys())
            if missing_skus:
                return Response(
                    {"message": f"Products not found for SKUs: {', '.join(missing_skus)}"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Crear ProductCart en una transacción atómica
            with transaction.atomic():
                product_carts = []
                for product_data in products:
                    sku = product_data["sku"]
                    quantity = product_data.get("quantity", 1)
                    product = product_map[sku]

                    product_cart = ProductCart.objects.create(
                        cart=cart, product=product, quantity=quantity
                    )
                    product_carts.append(product_cart)

                serializer = ProductCartSerializer(product_carts, many=True)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        #handling exceptions
        except Cart.DoesNotExist:
            return Response({"message": f"Cart with ID {cart_id} doesn't exists."},
                                                                status = status.HTTP_400_BAD_REQUEST)

        except Product.DoesNotExist:
            return Response({"message": f"Product doesn't exists."}, status = status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_400_BAD_REQUEST)


class ProductCartUserList(APIView):
    def get(self, request):
        cart_id = request.query_params.get("cart", None)
        user_id = request.query_params.get("user", None)

        if not cart_id or not user_id:
            return Response({"message": "Cart ID wasn't provided."}, status = status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk = user_id)
            cart = Cart.objects.filter(name = cart_id, user = user).first()
            products = ProductCart.objects.filter(cart = cart)
            serializer = ProductCartSerializer(products, many = True)
            return Response(serializer.data, status.HTTP_200_OK)


        except User.DoesNotExist:
            return Response({"message": "User doesn't exists."}, status = status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductCartHasChanged(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        items = request.data.get("items", None)
        user = request.user

        if not items:
            return Response({'message': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.filter(user=user, status="PENDING").first()
            order_products = OrderProduct.objects.filter(order=order)  # Filtrar todos los productos de la orden
        except Order.DoesNotExist:
            return Response({'changed': True, 'message': 'No active order found'}, status=status.HTTP_200_OK)

        # Convertir los productos de la orden en un diccionario {product_id: quantity}
        order_product_map = {op.product.sku: op.quantity for op in order_products}

        # Convertir los productos enviados en un diccionario {product_id: quantity}
        request_product_map = {item["sku"]: item["quantity"] for item in items}

        # Comparar si las claves (productos) o los valores (cantidades) han cambiado
        if order_product_map != request_product_map:
            return Response({'changed': True}, status=status.HTTP_200_OK)

        return Response({'changed': False}, status=status.HTTP_200_OK)


class ProductCartUserRemove(APIView):
    def delete(self, request):
        cart_id = request.data.get("cart", None)
        product_id = request.data.get("product", None)
        user_id = request.data.get("user", None)

        if not cart_id or not product_id or not user_id:
            return Response({"message": "All fields are required"}, status = status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk = user_id)
            cart = Cart.objects.filter(pk = cart_id, user = user).first()
            product = ProductCart.objects.filter(pk = product_id, cart = cart).first()

            #check if Cart or ProductCart not exists
            if not cart:
                raise Cart.DoesNotExist
            if not  product:
                raise ProductCart.DoesNotExist

            #deleting a product
            product.delete()
            return Response({"message": "Product cart was deleted successfully"}, status = status.HTTP_204_NO_CONTENT)

        except User.DoesNotExist:
            return Response({"message": f"User with ID {user_id} doesn't exists"}, status = status.HTTP_400_BAD_REQUEST)

        except Cart.DoesNotExist:
            return Response({"message": f"Cart with ID {cart_id} doesn't exists"}, status = status.HTTP_400_BAD_REQUEST)

        except ProductCart.DoesNotExist:
            return Response({"message": f"Product with ID {product_id} doesn't exists"}, status = status.HTTP_400_BAD_REQUEST)


        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
