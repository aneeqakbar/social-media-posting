from django.db import models
from django.contrib.auth.models import User
from users.models import SocialAccount

import os
from uuid import uuid4
from datetime import datetime


def rename_on_upload(self, file_name):
    upload_dir = 'media/post_images'
    ext_name = file_name.split('.')[-1]
    datetime_now = datetime.now()
    file_name_string = '{}{}.{}'.format(datetime_now.strftime("%Y%m%d%H%M%S"), uuid4().hex, ext_name)
    return os.path.join(upload_dir, file_name_string)


# Create your models here.

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return f"{self.user.username}'s {self.name}"

    @staticmethod
    def get_categories_by_user(user):
        return Category.objects.filter(user = user)


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts_users")
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to=rename_on_upload, blank=True, null=True)
    # type = models.ForeignKey(SocialAccount, on_delete=models.PROTECT, related_name="social_type")
    type = models.ManyToManyField(SocialAccount, related_name="posts")
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    description = models.TextField()
    
    @staticmethod
    def get_posts_by_user(user):
        return Post.objects.filter(user = user)


class DayName(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class SchedulePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="schedules")
    day = models.ForeignKey(DayName, on_delete=models.CASCADE, related_name="schedules")
    accounts = models.ManyToManyField(SocialAccount, related_name="schedules")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="schedules", null=True, blank=True)
    time = models.TimeField(auto_now=False, auto_now_add=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def get_posts_by_user(user):
        return Post.objects.filter(user = user)


