from django.db import models

from orders.models import Order


# Create your models here.
class Payment(models.Model):
    PAYMENT_METHODS = (
        ("CASH", "CASH"),
        ("DEBIT_CARD", "DEBIT_CARD"),
        ("CREDIT_CARD", "CREDIT_CARD"),
        ("BANK_TRANSFER", "BANK_TRANSFER"),
        ("NEQUI", "NEQUI")
    )

    PAYMENT_STATUS = (
        ("APPROVED", "APPROVED"),
        ("PENDING", "PENDING"),
        ("IN_PROCESS", "IN_PROCESS"),
        ("REJECTED", "REJECTED"),
        ("CANCELED", "CANCELED"),
        ("REFUNDED", "REFUNDED"),
        ("CHARGED_BACK", "CHARGED_BACK"),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_amount = models.FloatField(verbose_name="payment_amount")
    payment_date = models.DateTimeField(auto_created=True)
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHODS)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS)
    last_updated = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"Payment {self.id} | {self.payment_status} | ${self.payment_amount}"


class Coupon(models.Model):
    created_by = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.CASCADE)
    coupon_code = models.CharField(max_length=15)
    discount = models.IntegerField()
    creation_date = models.DateTimeField(auto_now=True)
    expiration_date = models.DateField()
    is_active = models.BooleanField(default=True)
    discount_type = models.CharField(choices=(("PERCENTAGE", "PERCENTAGE"), ("FIXED", "FIXED")), max_length=12)

    def is_valid(self):
        from django.utils.timezone import now

        current_date = now().date()
        return self.is_active and self.expiration_date > current_date

    def __str__(self):
        if self.discount_type == "FIXED":
            return f"Coupon {self.coupon_code} | {self.discount_type} | ${self.discount} | Expires: {self.expiration_date}"
        else:
            return f"Coupon {self.coupon_code} | {self.discount_type} | {self.discount}% | Expires: {self.expiration_date}"
