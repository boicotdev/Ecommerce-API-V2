import uuid
from io import BytesIO

from django.db.transaction import atomic
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.response import Response
from weasyprint import HTML

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView, Response
from rest_framework import status

import mercadopago
from decouple import config
from products.models import (
    Product
)
from carts.models import Cart, ProductCart
from orders.models import Order, OrderProduct
from products.permissions import AdminPermissions
from shipments.models import Shipment
from payments.models import Payment, Coupon
from .serializers import PaymentSerializer, CouponSerializer

MP_ACCESS_TOKEN = config('MERCADO_PAGO_ACCESS_TOKEN')

class CreatePaymentPreference(APIView):
    def post(self, request):
        sdk = mercadopago.SDK(config('MERCADO_PAGO_ACCESS_TOKEN'))
        user = request.user
        items = request.data.get('items', [])
        shipping_info = request.data.pop('shipping_info', None)
        notification_url = request.data.get('notification_url')

        # Obtener o crear la orden pendiente
        order, _ = Order.objects.get_or_create(user=user, status='PENDING')
        cart, _ = Cart.objects.get_or_create(user=user)

        for item in items:
            product = Product.objects.get(sku=item['id'])

            # OrderProduct
            order_product, created = OrderProduct.objects.get_or_create(
                order=order,
                product=product,
                defaults={'price': item['unit_price'], 'quantity': item['quantity']},
            )
            if not created:
                order_product.quantity = item['quantity']
                order_product.save()

            # ProductCart
            product_cart, created = ProductCart.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': item['quantity']}
            )
            if not created:
                product_cart.quantity = item['quantity']
                product_cart.save()

        # Ahora sí, construir preference_data fuera del bucle
        preference_data = {
            'items': items,
            'payer': {
                'name': 'Carlos',
                'surname': 'Guzman',
                'email': 'carlos.guzmanscg7@gmail.com',
                'phone': {
                    'area_code': '57',
                    'number': '3236283340'
                },
                'identification': {
                    'type': 'CC',
                    'number': '1005827946'
                },
                'address': {
                    'zip_code': '110111',
                    'street_name': 'Calle 123',
                    'street_number': 45
                }
            },
            'back_urls': {
                'success': 'https://c090-2800-484-d584-6100-3cfc-6883-c1ed-f501.ngrok-free.app/api/api/v1/pago-exitoso/',
                'failure': 'https://c090-2800-484-d584-6100-3cfc-6883-c1ed-f501.ngrok-free.app/api/api/v1/pago-fallido/',
                'pending': 'https://c090-2800-484-d584-6100-3cfc-6883-c1ed-f501.ngrok-free.app/api/api/v1/pago-pendiente/'
            },
            'auto_return': 'approved',
            'notification_url': notification_url or 'https://c090-2800-484-d584-6100-3cfc-6883-c1ed-f501.ngrok-free.app/api/v1/webhook/mercadopago/',
            'statement_descriptor': 'AVOBERRY',
            'external_reference': f'{order.id}',
            'expires': False,
            'payment_methods': {
                'excluded_payment_methods': [],
                'excluded_payment_types': [],
                'installments': 1,
                'default_installments': 1
            },
            'currency_id': 'COP'
        }

        try:
            preference_response = sdk.preference().create(preference_data)
            if preference_response['status'] != 201:
                return Response(
                    {'error': preference_response['message']},
                    status=status.HTTP_400_BAD_REQUEST
                )

            preference = preference_response['response']
            return Response(
                {'preference_id': preference.get('id'), 'order': order.id},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'detail': 'Error creating preference!', 'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class MercadoPagoPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get_idempotency_key(self, request):
        return request.data.get('idempotency_key', str(uuid.uuid4()))

    def build_payment_data(self, request):
        try:
            payer_data = request.data.get('payer', {})
            identification = payer_data.get('identification', {})
            return {
                'transaction_amount': float(request.data.get('transaction_amount')),
                'token': request.data.get('token'),
                'description': 'Compra de productos',
                'installments': int(request.data.get('installments')),
                'payment_method_id': request.data.get('payment_method_id'),
                'issuer_id': request.data.get('issuer_id'),
                'payer': {
                    'email': payer_data.get('email'),
                    'identification': {
                        'type': identification.get('type'),
                        'number': identification.get('number')
                    }
                },
                'external_reference': str(uuid.uuid4()),  # Opcional pero recomendado para conciliación
            }


        except (TypeError, ValueError, KeyError) as e:
            raise ValueError(f'Datos inválidos: {e}')

    def post(self, request, *args, **kwargs):
        sdk = mercadopago.SDK(MP_ACCESS_TOKEN)
        request_options = mercadopago.config.RequestOptions()
        request_options.custom_headers = {
            'x-idempotency-key': self.get_idempotency_key(request)
        }

        try:
            user = request.user  # Usuario autenticado
            payment_data = self.build_payment_data(request)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:

            response = sdk.payment().create(payment_data, request_options)
            payment = response.get('response', {})

            if payment.get('status') != 'approved':
                return Response(
                    {'error': 'Pago no aprobado', 'details': response},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Asociar la orden si existe
            order = Order.objects.filter(user=user, status='PENDING').first()
            if not order:
                return Response(
                    {'error': 'No se encontró una orden asociada al usuario'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # (Opcional) Aquí podrías actualizar el estado de la orden

            return Response(payment, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': 'Error al procesar el pago', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


#cart details
class PaymentDetailsViewView(APIView):
    def get(self, request):
        order_id = request.query_params.get('order', None)
        if not  order_id:
            return Response({'message': 'Payment ID is required'}, status = status.HTTP_400_BAD_REQUEST)
        try:
            payment = Payment.objects.get(order = order_id)
            serializer = PaymentSerializer(payment, many=False)
            #if serializer.is_valid():
            return Response(data=serializer.data, status = status.HTTP_200_OK)
          #  return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        except Payment.DoesNotExist:
            return Response({'message': 'Payment not found'}, status = status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'message': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

class GenerateSalesReportView(APIView):
    def get(self, request, order_id):
        '''Genera un reporte PDF para una venta específica.'''
        try:
            sale = Payment.objects.select_related('order').get(order__id=order_id)
            order = sale.order  # Ya se obtuvo con select_related
            order_products = order.orderproduct_set.all()
            total = sum([item.price * item.quantity for item in order_products])
            total += 5000
            # Formatear el total con separación cada 3 cifras (estilo colombiano)
            total_formatted = '{:,.0f}'.format(sale.payment_amount).replace(',', '.')
        except Payment.DoesNotExist:
            return HttpResponse('Pago no encontrado', status=404)
        except Order.DoesNotExist:
            return HttpResponse('Orden no encontrada', status=404)

        # Renderizar la plantilla HTML con datos
        html_string = render_to_string('sales_report.html', {'sale': sale,
                                                                                'items': order_products,
                                                                                'total': total_formatted})

        # Generar PDF
        pdf_file = BytesIO()
        HTML(string=html_string).write_pdf(pdf_file)

        # Responder con el PDF
        pdf_file.seek(0)
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=\'Factura_{order.id}.pdf'
        return response



class MercadoPagoWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            event_type = request.data.get('type')
            if event_type != 'payment':
                return Response({'message': 'Evento ignorado'}, status=status.HTTP_200_OK)

            # Extraer ID del pago
            payment_id = request.data.get('data', {}).get('id')
            if not payment_id:
                return Response({'error': 'ID de pago no proporcionado'}, status=status.HTTP_400_BAD_REQUEST)
            print('Payment ID', payment_id)
            # Instanciar SDK
            try:
                sdk = mercadopago.SDK(MP_ACCESS_TOKEN)
            except Exception as e:
                return Response({'error': f'Error al instanciar SDK: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Obtener detalles del pago
            try:
                payment = sdk.payment().get(payment_id)
                payment_data = payment.get('response', {})
                if not payment_data:
                    raise ValueError('Datos de pago vacíos')
            except Exception as e:
                return Response({'error': f'Error al obtener datos del pago: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Extraer información relevante
            info = self.extract_payment_data(payment_data)

            # Buscar orden pendiente del usuario
            order = Order.objects.filter(id='AVBLC-839838').first()
            if not order:
                return Response({'error': 'No se encontró una orden pendiente para este usuario'}, status=status.HTTP_404_NOT_FOUND)

            # Actualizar estado de orden
            order.status = 'PROCESSING'
            order.save()

            # Crear el pago
            Payment.objects.create(
                order=order,
                payment_amount=float(info.get('transaction_amount', 0)),
                payment_date=timezone.now(),
                payment_method='CASH',
                payment_status='APPROVED',
                last_updated=info.get('date_approved') or timezone.now()
            )

            # Crear el envío
            Shipment.objects.create(
                customer=order.user,
                order=order,
                shipment_address=f'{info.get('payer_street_name', '')} - {info.get('payer_street_number', '')}'.strip(),
                shipment_city='Bogotá',
                shipment_date_post_code=info.get('payer_zip_code', '110111'),
            )

            # Actualizar el stock de productos comprados
            with atomic():
                for item in info['items']:
                    try:
                        product = Product.objects.select_for_update().get(sku=item['id'])
                        if product.stock >= int(item['quantity']):
                            product.stock -= int(item['quantity'])
                            product.save()
                        else:
                            # Si quieres notificar algo, puedes lanzar una excepción o registrar un warning
                            raise ValueError(f'Stock insuficiente para el producto {product.name}')
                    except Product.DoesNotExist:
                        raise ValueError(f'Producto con SKU {item['id']} no encontrado')

            return Response({
                'message': 'Pago recibido exitosamente',
                'payment_id': payment_id,
                'status': info.get('status'),
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print('Error general:', e)
            return Response({'error': f'Error general: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def extract_payment_data(self, payment_data: dict) -> dict:
        '''Extrae la información relevante de una respuesta de pago de MercadoPago.'''
        payer_info = payment_data.get('payer', {})
        additional_info = payment_data.get('additional_info', {})
        shipping_info = additional_info.get('payer', {}).get('address', {})

        extracted_data = {
            'payment_id': payment_data.get('id'),
            'order_id': payment_data.get('order', {}).get('id'),
            'external_reference': payment_data.get('external_reference'),
            'status': payment_data.get('status'),
            'status_detail': payment_data.get('status_detail'),
            'date_approved': payment_data.get('date_approved'),
            'transaction_amount': payment_data.get('transaction_amount'),
            'net_received_amount': payment_data.get('transaction_details', {}).get('net_received_amount'),
            'taxes_amount': payment_data.get('taxes_amount'),
            'currency_id': payment_data.get('currency_id'),

            # Medio de pago
            'payment_type_id': payment_data.get('payment_type_id'),
            'payment_method_id': payment_data.get('payment_method_id'),

            # Datos del pagador
            'payer_email': payer_info.get('email'),
            'payer_id': payer_info.get('id'),
            'payer_identification_type': payer_info.get('identification', {}).get('type'),
            'payer_identification_number': payer_info.get('identification', {}).get('number'),

            # Dirección del pagador
            'payer_street_name': shipping_info.get('street_name'),
            'payer_street_number': shipping_info.get('street_number'),
            'payer_zip_code': shipping_info.get('zip_code'),

            # Datos del producto
            'items': additional_info.get('items', []),

            # Fee / comisión
            'fee_amount': next(
                (fee.get('amount') for fee in payment_data.get('fee_details', []) if
                 fee.get('type') == 'mercadopago_fee'),
                None
            ),
        }

        return extracted_data


class CouponsCreateView(APIView):
    permission_classes = [AdminPermissions]
    def post(self, request):
        coupon_code = request.data.get('coupon_code', None)
        discount = request.data.get('discount', None)
        discount_type = request.data.get('discount_type', None)
        expiration_date = request.data.get('expiration_date', None)

        if not  coupon_code or not discount or not discount_type or not expiration_date:
            return Response({'message': 'Todos los campos son obligatorios'}, status = status.HTTP_400_BAD_REQUEST)

        try:
            serializer = CouponSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status = status.HTTP_201_CREATED)
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CouponsAdminRetrieveView(APIView):
    """
    Only admin user can access
    - Retrieve all coupons available
    """
    permission_classes = [AdminPermissions]

    def get(self, request):
        try:
            coupons = Coupon.objects.all()
            coupons_serializer = CouponSerializer(coupons, many= True)
            return Response(coupons_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class CouponUpdateView(APIView):
    permission_classes = [AdminPermissions]
    def put(self, request):
        coupon_id = request.data.get("id", None)
        if not coupon_id:
            return Response({'message': 'Coupon ID is required'}, status = status.HTTP_400_BAD_REQUEST)
        try:
            coupon = Coupon.objects.get(pk = coupon_id)
            serializer = CouponSerializer(coupon, data= request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status = status.HTTP_200_OK)
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

        except Coupon.DoesNotExist:
            return Response({'message': f'Coupon ID {coupon_id} not found!'})
        except Exception as e:
            return Response({'message': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class CouponDeleteView(APIView):
    permission_classes = [AdminPermissions]
    def post(self, request):
        coupon_code = request.data.get("coupon_code", None)

        if not coupon_code:
            return Response({'message': 'Coupon code is required'}, status = status.HTTP_400_BAD_REQUEST)
        try:
            coupon = Coupon.objects.get(coupon_code = coupon_code)
            coupon.delete()
            return Response({'message': f'Coupon deleted successfully.'}, status = status.HTTP_204_NO_CONTENT)

        except Coupon.DoesNotExist:
            return Response({'message': f'Coupon code {coupon_code} not found!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class CouponCodeCheckView(APIView):
    """
    Validates a given discount coupon and returns the applicable discount.

    If the discount type is "FIXED", the function returns the total discount amount.
    If the discount type is "PERCENTAGE", it returns the percentage discount.

    Returns:
        dict: A dictionary containing:
            - 'discount' (str): The discount value (amount or percentage).
            - 'valid' (bool): Indicates whether the coupon is valid.
            - 'type' (str): Indicates the discount type
    """

    def post(self, request):
        coupon_code = request.data.get("coupon_code", None)
        if not coupon_code:
            return Response({'message': 'Coupon code is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            coupon = Coupon.objects.get(coupon_code=coupon_code)
            if coupon.is_valid():
                return Response({'valid': True, 'type':coupon.discount_type, 'discount': coupon.discount}, status=status.HTTP_200_OK)
            return Response({'valid': False, 'error': 'Cupón expirado o inactivo'}, status=status.HTTP_400_BAD_REQUEST)

        except Coupon.DoesNotExist:
            return Response({'message': f'Coupon code {coupon_code} not found!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
