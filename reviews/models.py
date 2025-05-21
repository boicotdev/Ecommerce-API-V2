from django.db import models

class ProductReview(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='user_review')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='reviewed_product')
    comment = models.TextField(max_length=600)
    rating = models.IntegerField(default=1)
    rated_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now_add=True)
    responses = models.ManyToManyField('ReviewResponse', related_name='user_responses', blank=True)

    def __str__(self) -> str:
        return f'Review from {self.user.first_name} - {self.rated_at}'


class ReviewResponse(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, blank=True, null=True)
    response = models.TextField(max_length=600)
    pub_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now_add=True)
    product_review = models.ForeignKey(ProductReview, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self) -> str:
        if self.user is not None:
            return f'Review Response from : {self.user.first_name} {self.user.last_name}'
        return f'Review Response from : Unassigned user'
