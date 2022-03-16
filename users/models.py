from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.dispatch import receiver
from django.db.models.signals import post_save

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    image = models.ImageField(default='profile_pics/default.jpg', upload_to='profile_pics/')
    bio = models.TextField()
    contributors = models.ManyToManyField(User, related_name="contributing_to")

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

    @property
    def get_contributors(self):
        try:
            return self.contributors.all()
        except:
            return None

    @property
    def get_categories(self):
        try:
            return self.user.categories.all()
        except:
            return None

    @property
    def get_posts(self):
        try:
            return self.user.posts.all()
        except:
            return None

    @property
    def get_image_url(self):
        try:
            return self.image.url
        except:
            return ''

@receiver(post_save, sender=User)
def create_profile(sender, created, instance, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class SocialLongLivedToken(models.Model):
    SOCIAL_MEDIA_CHOICES = (
        ("facebook", "Facebook"),
        ("instagram", "Instagram"),
        ("twitter", "Twitter"),
        ("linkedin-oauth2", "LinkedIn"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="long_lived_tokens")
    backend = models.CharField(max_length=255, choices=SOCIAL_MEDIA_CHOICES)
    token = models.CharField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.backend}"


class SocialAccount(models.Model):
    SOCIAL_MEDIA_CHOICES = (
        ("facebook", "Facebook"),
        ("instagram", "Instagram"),
        ("twitter", "Twitter"),
        ("linkedin-oauth2", "LinkedIn"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="social_posts_accounts")
    backend = models.CharField(max_length=255, choices=SOCIAL_MEDIA_CHOICES)
    unique_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    token = models.CharField(max_length=1000, null=True, blank=True)
    image = models.CharField(max_length=1000, null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.backend}"

    @staticmethod
    def get_social_by_user(user):
        return SocialAccount.objects.filter(user=user)

    @staticmethod
    def get_user_social_by_backend(user, backend):
        return SocialAccount.objects.filter(user=user, backend=backend)