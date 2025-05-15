from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from carts.models import Cart, ProductCart


class CartSerializer(ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class ProductCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCart
        fields = ['id', 'cart', 'product', 'quantity']
        depth = 1

    def create(self, validated_data):
        """
        Si el producto ya está en el carrito, actualiza la cantidad en lugar de crear un nuevo objeto.
        """
        product = validated_data.get('product')
        quantity = validated_data.get('quantity', 0)

        # Buscar si el producto ya está en el carrito
        existing_item = ProductCart.objects.filter(product=product).first()

        if existing_item:
            existing_item.quantity += quantity  # Sumar la nueva cantidad
            existing_item.save()
            return existing_item  # Retornar el objeto actualizado
        else:
            return super().create(validated_data)  # Crear un nuevo registro si no existe
