import json
from django.conf import settings
from users.models import SocialAccount, SocialLongLivedToken
from django.contrib.auth.models import User
import requests


def custom_details(backend, details, response, user, *args, **kwargs):
    if backend.name == "twitter":
        access_token = response["access_token"]
        token_instance, created = SocialLongLivedToken.objects.get_or_create(user = user, backend = backend.name)
        token_instance.token = json.dumps(access_token)
        token_instance.save()
        
        user_id = response["id"]
        screen_name = response["screen_name"]
        profile_image_url = response["profile_image_url"]
        account, created = SocialAccount.objects.get_or_create(
            user = user,
            unique_id = user_id,
            backend = 'twitter',
        )
        account.name = screen_name
        account.token = json.dumps(access_token)
        account.type = "Account"
        account.image = profile_image_url
        account.save()

    elif backend.name == "facebook":
        access_token = response["access_token"]
        res = requests.post(
            url=f"https://graph.facebook.com/v13.0/oauth/access_token?grant_type=fb_exchange_token&client_id={settings.SOCIAL_AUTH_FACEBOOK_KEY}&client_secret={settings.SOCIAL_AUTH_FACEBOOK_SECRET}&fb_exchange_token={access_token}"
        )
        if res.status_code == 200:
            access_token = res.json()['access_token']
            token_instance, created = SocialLongLivedToken.objects.get_or_create(user = user, backend = backend.name)
            token_instance.token = access_token
            token_instance.save()
