import json
from django.conf import settings
import facebook
import requests

class FacebookPosting():
    def __init__(self, account, token):
        self.token = token
        self.account = account

    def make_posts(self):
        graph = facebook.GraphAPI(self.token)
        for post in self.account.posts.all():
            try:
                if post.image and self.account.type == "Page":
                    image_path = f"{settings.BASE_DIR}{post.image.url}"
                    graph.put_photo(image=open(image_path, 'rb'),
                                    message=post.description)
                    print("FB: Posted Media")
                elif post.description:
                    graph.put_object(self.account.unique_id, "feed", message=f"{post.description}")
                    print("FB: Posted Text")
            except:
                pass

class LinkedInPosting():
    def __init__(self, account, token):
        self.url = "https://api.linkedin.com/v2/ugcPosts"
        self.image_share_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
        self.token = token
        self.account = account
        self.user_id = account.unique_id

    def make_posts(self):
        for post in self.account.posts.all():
            text = post.description
            if post.image:
                image_path = f"{settings.BASE_DIR}{post.image.url}"
                self.make_media_post(text=text, image_path=image_path)
            else:
                self.make_text_post(text=text)

    def make_text_post(self, text):
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            "X-Restli-Protocol-Version": "2.0.0"
        }
        data = {
            "author": f"urn:li:person:{self.user_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": f"{text}"
                    },
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        res = requests.post(self.url, data = json.dumps(data), headers=headers)
        if res.status_code == 201:
            print("LI: Posted Text")

    def make_media_post(self, text, image_path):
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            "X-Restli-Protocol-Version": "2.0.0"
        }
        data = {
            "registerUploadRequest": {
                "recipes": [
                    "urn:li:digitalmediaRecipe:feedshare-image"
                ],
                "owner": f"urn:li:person:{self.user_id}",
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        res = requests.post(self.image_share_url, data = json.dumps(data), headers=headers)

        res_json = res.json()
        image_upload_url = res_json["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
        image_upload_asset = res_json["value"]["asset"]

        # image_path = f"{settings.BASE_DIR}{post.image.url}"
        with open(image_path, "rb") as file:
            headers = {
                "Authorization": f'Bearer {self.token}',
                "Content-Type":"application/binary",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            binary_data = file.read()
            requests.post(image_upload_url, data=binary_data, headers=headers)

        data = {
            "author": f"urn:li:person:{self.user_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": f"{text}"
                    },
                    "shareMediaCategory": "IMAGE",
                    "media": [{
                        "status": "READY",
                        "description": {
                            "text": f"{text} - Posted Using SocialArk"
                        },
                        "media": f"{image_upload_asset}",
                        "title": {
                            "text": f"{text}"
                        }
                    }],
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        res = requests.post(self.url, data = json.dumps(data), headers=headers)

        if res.status_code == 201:
            print("LI: Posted Media")