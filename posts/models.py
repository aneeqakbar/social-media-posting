from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError

# Create your models here.

class Post(models.Model):
    category = models.ForeignKey("workspace.Category", on_delete=models.CASCADE, related_name="posts")
    social_accounts = models.ManyToManyField("users.SocialAccount")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=255)
    body = models.TextField()
    image = models.ImageField(upload_to="post_images/", blank=True, null=True)

    @property
    def get_image_url(self):
        try:
            return self.image.url
        except:
            return ''

# class Category(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")
#     name = models.CharField(max_length=255)
#     posts = models.ManyToManyField(Post, related_name="category")