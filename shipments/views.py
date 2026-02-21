from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from shipments.models import Shipment, DeliveryAddress
from shipments.serializers import ShipmentSerializer, DeliveryAddressSerializer


class DeliveryAddressesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        user = request.user
        if pk:
            if DeliveryAddress.objects.filter(customer=user).exists():
                address = DeliveryAddress.objects.filter(customer=user)
                serializer = DeliveryAddressSerializer(data=address)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                {"error": "Not address related with current user."},
                status=status.HTTP_404_NOT_FOUND,
            )
        else:
            if DeliveryAddress.objects.filter(customer=user).exists():
                queryset = DeliveryAddress.objects.filter(customer=user)
                serializer = DeliveryAddressSerializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Not address related with current user."},
                    status=status.HTTP_404_NOT_FOUND,
                )

    def post(self, request):
        serializer = DeliveryAddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            user = request.user
            address = DeliveryAddress.objects.filter(pk=pk, customer=user).first()
            address.delete()
            return Response(
                {"message": "Shipment address was deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ShipmentUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    """
    Update a single `Shipment` object, special permissions are required to access this view
    """

    def put(self, request):
        shipment_id = request.data.get("shipment")
        if not shipment_id:
            return Response(
                {"message": "Shipment ID is missing, try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        shipment = get_object_or_404(Shipment, pk=shipment_id)

        serializer = ShipmentSerializer(shipment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            print(f"Shipment {shipment_id} updated successfully.")
            return Response(serializer.data, status=status.HTTP_200_OK)
        print(f"Shipment update failed for ID {shipment_id}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShipmentListView(APIView):
    """
    Retrieve all shipments into the ecommerce
    Superuser permissions are required to access this view
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            shipments = Shipment.objects.all()
            serializer = ShipmentSerializer(shipments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ShipmentCreateView(APIView):
    permission_classes = [IsAuthenticated]
    """
    Handle all operations related to create a shipment order
    """

    def post(self, request):
        customer_id = request.data.get("customer", None)
        order_id = request.data.get("order", None)
        print(request.data)

        if not customer_id or not order_id:
            return Response(
                {"message": "Customer ID and Order ID are required!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Shipment.objects.filter(order__id=order_id).exists():
            return Response(
                {"error": "Ya existe un envío asociado a esta orden."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            serializer = ShipmentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
