from django.db import models


class BlogPost(models.Model):
    user = models.ForeignKey(
        "users.User", null=True, on_delete=models.SET_NULL, related_name="publisher"
    )
    title = models.CharField(max_length=100)
    content = models.TextField()
    published_at = models.DateTimeField(auto_now=True)
    last_updated = models.DateTimeField(auto_now=True)
    slug = models.SlugField()
    thumbnail = models.ImageField(
        default="blog/thumbnails/thumbnail.png", upload_to="blog/thumbnails"
    )
    tags = models.ManyToManyField("Tag", blank=True)
    reading_count = models.IntegerField(default=0)
    reviews = models.ManyToManyField("BlogReview", blank=True)

    def __str__(self) -> str:
        return f"{self.title} - published at {self.published_at}"


class BlogReview(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    review = models.CharField(max_length=400)
    published_at = models.DateTimeField(auto_now=True)
    last_updated = models.DateTimeField(auto_now=True)
    rating = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"Review from {self.user.username}"


class Tag(models.Model):
    tagname = models.CharField(max_length=30)
    description = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.tagname}"
