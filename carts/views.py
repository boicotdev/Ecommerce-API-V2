from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from carts.models import Cart, ProductCart
from carts.serializers import CartSerializer, ProductCartSerializer
from products.models import Product
from users.models import User


# Create your views here.
class CartCreateView(APIView):
    def post(self, request):
        user = request.data.get("user", None)
        name = request.data.get("name", None)
        description = request.data.get("description", None)

        if not user or not name or not description:
            return Response(
                {"message": "All fields are required!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # check if given order name already exists
        try:
            cart = Cart.objects.get(name=name)
            if cart:
                return Response(
                    {"message": f"Cart with name {name} already exists!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Cart.DoesNotExist:
            serializer = CartSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CartExistView(APIView):
    def get(self, request):
        cart_name = request.query_params.get("cart", None)
        if not cart_name:
            return Response(
                {"message": "Cart ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            cart = Cart.objects.get(name=cart_name)
            return Response({"exists": True}, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({"exists": False}, status=status.HTTP_404_NOT_FOUND)


class CartItemCreateView(APIView):
    def post(self, request):
        data = request.data.get("data")

        # Validar que `data` contenga `cart_id` y `items`
        if not data or "cart_id" not in data or "items" not in data:
            return Response(
                {"message": "You need to provide a valid cart_id and items list"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_id = data.get("cart_id")
        cart_items = data["items"]

        # Validar que `items` sea una lista válida
        if not isinstance(cart_items, list) or len(cart_items) == 0:
            return Response(
                {"message": "Items must be a non-empty list"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Verificar si el carrito existe
            cart = Cart.objects.get(name=cart_id)
            updated_items = []

            for item in cart_items:
                product_id = item.get("product")
                quantity = item.get("quantity")

                if not product_id or not quantity:
                    return Response(
                        {"message": "Each item must have a product and quantity"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Verificar si el producto existe
                product = Product.objects.filter(sku=product_id).first()
                if not product:
                    return Response(
                        {"message": f"Product with ID {product_id} not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                # Buscar si el producto ya está en el carrito
                product_cart, created = ProductCart.objects.get_or_create(
                    cart=cart, product=product
                )

                if created:
                    product_cart.quantity = quantity
                else:
                    product_cart.quantity += (
                        quantity  # Incrementa la cantidad si ya existe
                    )

                product_cart.save()

                updated_items.append(ProductCartSerializer(product_cart).data)

            return Response(updated_items, status=status.HTTP_201_CREATED)

        except Cart.DoesNotExist:
            return Response(
                {"message": f"Cart with ID {cart_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CartUserListView(APIView):
    def get(self, request):
        user_id = request.query_params.get("user", None)
        if not user_id:
            return Response(
                {"message": "User field are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(pk=user_id)
            carts = Cart.objects.filter(user__id=user.id)
            serializer = CartSerializer(carts, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except Cart.DoesNotExist:
            return Response(
                {"message": f"Carts with {user} not exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except User.DoesNotExist:
            return Response(
                {"message": f"User with {user_id} not exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CartUserDelete(APIView):
    def delete(self, request):
        user_id = request.data.get("user", None)
        cart_name = request.data.get("cart_name", None)

        if not user_id or not cart_name:
            return Response(
                {"message": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(pk=user_id)
            cart = Cart.objects.get(user=user, name=cart_name)
            cart.delete()
            return Response(
                {"message": "Cart was deleted successfully."},
                status=status.HTTP_204_NO_CONTENT,
            )

        except Cart.DoesNotExist:
            return Response(
                {"message": f"Cart with name {cart_name} not exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except User.DoesNotExist:
            return Response(
                {"message": f"User with {user_id} not exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return Response(
                {"message": "Cart was deleted successfully."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
