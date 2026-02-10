from django.db import transaction
from orders.models import StockMovement
from products.models import Product
from purchases.models import SuggestedRetailPrice


class StockMoventSignal:
    def __init__(self, type: str='IN') -> None:
        self.movement_type = type
    
    def bulk_create(self, items):
        parsed_items = []
        for prod in items:
            if not isinstance(prod.product, Product):
                raise TypeError('prod must be an Product instance')
            product = prod.product
            parsed_items.append(
                StockMovement(
                product=product,
                movement_type = self.movement_type,
                quantity = prod.quantity,
                reason='SOURCING'
                )
            )
        with transaction.atomic():
            StockMovement.objects.bulk_create(parsed_items)



class RetailSuggestedPriceService:

    def __init__(self) -> None:
        pass
    
    def bulk_create(self, purchase_items):
        items = []
        for prod in purchase_items:
            if not isinstance(prod.product, Product):
                raise TypeError('prod must be an Product instance')
            items.append(
                SuggestedRetailPrice(
                purchase_item=prod,
                suggested_price = prod.sale_price_per_weight(),
                )
            )
        with transaction.atomic():
            SuggestedRetailPrice.objects.bulk_create(items)


