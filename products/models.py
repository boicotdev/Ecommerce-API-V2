from django.db import models

options = (
    ("CANASTILLA", "CANASTILLA"),
    ("MANOJO", "MANOJO"),
    ("BULTO", "BULTO"),
    ("CAJA", "CAJA"),
    ("ATADOS", "ATADOS"),
    ("DOCENA", "DOCENA"),
    ("BOLSAS", "BOLSAS"),
    ("GUACAL", "GUACAL"),
    ("BANDEJA", "BANDEJA"),
    ("ESTUCHE", "ESTUCHE"),
    ("PONY", "PONY"),
    ("KG", "KG"),
)

class Category(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=50)

    def __str__(self):
        return f"Category: {self.name}"


class UnitOfMeasure(models.Model):
    """
    Represent a measure unity, a product can be related to `UnitOfMeasure`
    Set all choices are required by your application.
    """
    unity = models.CharField(max_length=30, choices=options)
    weight = models.IntegerField()

    def __str__(self):
        return f"Unit Of Measure {self.unity} | ID {self.id} | Weight {self.weight} Lbs"

class Product(models.Model):
    sku = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=1024)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    purchase_price = models.FloatField(default=0)

    stock = models.PositiveIntegerField(default=1)
    unit = models.ForeignKey(UnitOfMeasure, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="unit")
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)

    score = models.IntegerField(blank=True, null=True)  # Consider usar Decimal con validación
    recommended = models.BooleanField(default=False)
    best_seller = models.BooleanField(default=False)

    slug = models.SlugField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    main_image = models.ImageField(
        upload_to="products/", default="products/dummie_image.jpeg"
    )

    def __str__(self):
        return f"Product: {self.name} (SKU: {self.sku}, Stock: {self.stock} {self.unit}, Price: ${self.price})"
