from products.models import Product


class ProductFilterService:
    def __init__(self, options: dict) -> None:
        self.options = options
        self.results = Product.objects.all()

    def search(self):
        filters = {}

        # Category
        if self.options.get("category"):
            filters["category_id"] = self.options["category"]

        # Price range
        if self.options.get("price_min"):
            filters["price__gte"] = self._to_float(self.options["price_min"])

        if self.options.get("price_max"):
            filters["price__lte"] = self._to_float(self.options["price_max"])

        # Stock
        if self.options.get("in_stock") is not None:
            if self._to_bool(self.options["in_stock"]):
                filters["stock__gt"] = 0

        # Flags
        if self.options.get("recommended") is not None:
            filters["recommended"] = self._to_bool(self.options["recommended"])

        if self.options.get("score") is not None:
            filters["score__gt"] = int(self.options["score"])

        if self.options.get("best_seller") is not None:
            filters["best_seller"] = self._to_bool(self.options["best_seller"])

        # Quality
        if self.options.get("quality"):
            filters["quality__iexact"] = self.options["quality"]

        # Tag
        if self.options.get("tag"):
            filters["tag__iexact"] = self.options["tag"]

        # Weight range (related model)
        if self.options.get("weight_min"):
            filters["weight__value__gte"] = self._to_float(self.options["weight_min"])

        if self.options.get("weight_max"):
            filters["weight__value__lte"] = self._to_float(self.options["weight_max"])

        # Name related model
        if self.options.get("name"):
            filters["name__icontains"] = self.options["name"]



        self.results = self.results.filter(**filters)

        return self.results

    def _to_bool(self, value):
        if isinstance(value, bool):
            return value
        return str(value).lower() in ("true", "1", "yes")

    def _to_float(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
