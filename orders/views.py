from django.db import transaction
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView, Response

from orders.models import Order, OrderProduct
from orders.serializers import OrderSerializer, OrderProductSerializer
from payments.models import Payment
from products.models import UnitOfMeasure, Product
from products.permissions import CanViewOrder
from users.models import User


# create
class OrderCreateView(APIView):
    def post(self, request):
        check_status_list = ["PENDING", "DELIVERED", "CANCELLED", "APPROVED"]
        status_order = request.data.get("status", None)
        user_id = request.data.get("user", None)['id']

        # check if required fields are fulfilled
        return Response({"message": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)
        # check if the given status is valid
        if not status_order in check_status_list:
            return Response({"message": f"The given status {status_order} isn't valid"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer = OrderSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=User.objects.get(pk=user_id))
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminOrderCreateView(APIView):
    """
    Create a new `Order` and a new `OrderProduct`.
    If `is_paid` is True in request.data, create a `Payment` and a `Shipment` instance.
    Only superusers can access this view.
    """

    permission_classes = [IsAdminUser]

    def post(self, request):
        data = request.data
        required_fields = {'client', 'order_items', 'is_paid'}

        # Check if all required fields are present
        if not required_fields.issubset(data):
            return Response({'message': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the user
        user_id = data['client']
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is a superuser
        if user.is_superuser:
            return Response({'message': 'A superuser cannot create an order for himself.'},
                            status=status.HTTP_403_FORBIDDEN)

        # Create the Order
        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                status="PENDING"
            )

            # Process order items
            order_items_data = data['order_items']
            order_items = []

            for item in order_items_data:
                try:
                    product = Product.objects.get(pk=item['sku'])  # Ajusta el nombre de la clave si es diferente
                except Product.DoesNotExist:
                    return Response({'message': f"Product with ID {item['product_id']} not found"},
                                    status=status.HTTP_404_NOT_FOUND)

                # Validar la unidad de medida si existe en los datos
                unit = None
                if 'measure_unity' in item:
                    try:
                        unit = UnitOfMeasure.objects.get(pk=item['measure_unity'])
                    except UnitOfMeasure.DoesNotExist:
                        return Response({'message': f"UnitOfMeasure with ID {item['unity']} not found"},
                                        status=status.HTTP_404_NOT_FOUND)

                order_items.append(OrderProduct(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=item['price'],
                    measure_unity=unit  # Asignamos la unidad de medida si existe
                ))

            OrderProduct.objects.bulk_create(order_items)

        # handle Payment creation
        if data['is_paid']:
            payment = Payment.objects.create(
                order=order,
                payment_amount=data.get('payment_amount', 0),
                payment_date=data.get("payment_date", None),
                payment_method=data.get("payment_method", "CASH"),
                payment_status="APPROVED" if data['is_paid'] else "PENDING"

            )
            payment.save()

        return Response({'message': 'Order created successfully'}, status=status.HTTP_201_CREATED)


# retrieve all orders of a single user
class OrderUserList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.query_params.get("user", None)
        if not user_id:
            return Response({"message": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(dni=user_id)
            orders = Order.objects.filter(user=user)
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderUserCancelView(APIView):
    def put(self, request):
        order_id = request.data.get("order")
        user_id = request.data.get("user")
        new_status = request.data.get("status")

        if not order_id or not user_id or not new_status:
            return Response({"message": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar la orden que pertenezca al usuario
        order = Order.objects.filter(pk=order_id, user_id=user_id).first()

        if not order:
            return Response({"message": "Order not found or does not belong to user"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Verificar si la orden tiene un pago asociado
        has_payment = Payment.objects.filter(order=order).exists()

        # Definir los estados en los que se puede cancelar la orden
        cancelable_status = {"PENDING", "ON_HOLD"}
        if has_payment:
            cancelable_status.update({"PENDING", "FAILED"})

        if order.status not in cancelable_status:
            return Response({"message": f"No se puede cancelar en este estado {order.status}"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Actualizar el estado de la orden a CANCELLED
        serializer = OrderSerializer(order, data={"status": "CANCELLED"}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# delete
class OrderUserRemove(APIView):
    def delete(self, request):
        order_id = request.data.get("order")
        user_id = request.data.get("user")

        if not order_id or not user_id:
            return Response({"message": "All fields are required"}, status=status.HTTP_200_OK)
        try:
            user = User.objects.get(pk=user_id)
            order = Order.objects.filter(user=user, pk=order_id)
            order.delete()

            return Response({"message": "Order deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_400_BAD_REQUEST)


        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# order list with superuser permissions
class OrdersDashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            queryset = Order.objects.all()
            paginator = LimitOffsetPagination()
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            serializer = OrderSerializer(paginated_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderDashboardDetailsView(APIView):
    permission_classes = [IsAuthenticated, CanViewOrder]

    def get(self, request):
        order_id = request.query_params.get("order", None)
        if not order_id:
            return Response({"message": "Order ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(pk=order_id)

            # Verificar permisos a nivel de objeto
            self.check_object_permissions(request, order)

            serializer = OrderSerializer(order).data
            return Response(serializer, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderDashboardUpdateView(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request):
        STATUS = ["PENDING", "PROCESSING", "SHIPPED", "OUT_FOR_DELIVERY", "DELIVERED", "CANCELLED", "RETURNED",
                  "FAILED", "ON_HOLD"]

        order_id = request.data.get("order")
        new_status = request.data.get("status")
        if not order_id or not new_status:
            return Response({"message": "Order ID is missing, try again"}, status=status.HTTP_400_BAD_REQUEST)
        if new_status not in STATUS:
            return Response({
                                'message': 'Order status options are - ["PENDING","PROCESSING", "SHIPPED", "OUT_FOR_DELIVERY", "DELIVERED", "CANCELLED", "RETURNED","FAILED","ON_HOLD"]'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            order = Order.objects.get(id=order_id)
            serializer = OrderSerializer(order, data=request.data, partial=True)
        except Order.DoesNotExist:
            return Response({"message": f"Order with ID {order_id} not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderProductCreateView(APIView):
    def post(self, request):
        order_id = request.data.get("order", None)
        product_id = request.data.get("product", None)
        product_price = request.data.get("price", None)
        product_quantity = request.data.get("price", None)

        if not order_id or not product_id or not product_price or not product_quantity:
            return Response({"message": "All fields are required!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(pk=order_id)
            product = Product.objects.get(pk=product_id)
            serializer = OrderProductSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # handling exceptions
        except Product.DoesNotExist:
            return Response({"message": "Product doesn't exists!"}, status=status.HTTP_400_BAD_REQUEST)

        except Order.DoesNotExist:
            return Response({"message": "Order doesn't exists!"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckOrderStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            order = Order.objects.get(id=request.query_params.get('external_reference'))
            payment = Payment.objects.filter(order=order).first()
            if payment.payment_status == "APPROVED":
                return Response({
                    'payment_id': payment.payment_id,
                    'status': payment.payment_status,
                    'external_reference': order.id}, status=status.HTTP_200_OK)
            return Response({'details': 'Payment not completed'}, status=status.HTTP_404_NOT_FOUND)
        except Order.DoesNotExist:
            return Response({'error': 'Not order with the given ID'}, status=status.HTTP_404_NOT_FOUND)
