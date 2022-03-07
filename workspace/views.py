import base64
import json
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from users.models import SocialAccount
from workspace.forms import CategoryForm, PostForm
from django.db.models import Count
from django.core import serializers

from workspace.models import Category, DayName, Post, SchedulePost

import os
import facebook
import requests
import datetime


class IndexView(LoginRequiredMixin, View):
    def get(self, request):
        next = request.GET.get("next")
        if next:
            return redirect(next)
        social_accounts = request.user.social_posts_accounts.all()
        context = {"social_accounts": social_accounts}
        return render(request, 'workspace/home.html', context)


class ContentView(View):
    def get(self, request):
        category_form = CategoryForm()
        categories = Category.get_categories_by_user(request.user).annotate(post_count=Count('post'))
        print(categories)

        obj_list = []

        # for category in categories:
        #     obj = {}
        #     post_by_cat = Post.objects.filter(user=request.user, category=category.id)
        #     for p in post_by_cat:
        #         count = 0
        #         types = []
        #         for i in p.type.all():
        #             count += 1
        #             types.append(i.type)

        #         obj = {
        #             "name": category.name,
        #             "data": {
        #                 'items': count,
        #                 'types': types
        #             }
        #         }
                
        #         # obj['name'] = {category.name: {
        #         #     'items': count,
        #         #     'type': types
        #         # }} 
        #         print("obj", obj)
                
        #     obj_list.append(obj)


        for category in categories:
            obj = {}
            socials = SocialAccount.get_social_by_user(request.user)
            total_post_count = Post.objects.filter(user=request.user, category=category.id).count()

            for social in socials:
                count = 0
                post_by_type = Post.objects.filter(user=request.user, category=category.id, type=social.id)
                types = []
                for p in post_by_type:
                    # FB = {"name": "FB", "val": 0}
                    # IG = {"name": "IG", "val": 0}
                    # TW = {"name": "TW", "val": 0}
                    count += 1
                    for i in p.type.all():

                        types.append({"name": i.type, "val": count})

                obj = {
                    "name": category.name,
                    "data": {
                        'items': total_post_count,
                        'types': types
                    }
                }

                print("obj", obj)
                    
            obj_list.append(obj)
                

        print("obj_list", obj_list)
        context = {"categories": categories, "category_form": category_form, "counter": obj_list}
        return render(request, 'workspace/content.html', context)

    def post(self, request):
        action = request.POST.get("action")
        if action == "create":
            form = CategoryForm(request.POST)
            if form.is_valid():
                category = form.save(commit=False)
                category.user = request.user
                category.save()
                messages.success(request, "Category has been created")
                previous_url = request.META.get('HTTP_REFERER')
                if previous_url:
                    return redirect(previous_url)
            else:
                messages.error(request, "Category can't be created")
        return redirect("workspace:ContentView")
    

class SingleContentView(View):
    template_name = 'workspace/posts.html'
    
    def get(self, request, id):
        user = request.user
        posts = Post.objects.filter(user=user, category_id=id)
        categories = Category().get_categories_by_user(user)
        socials = SocialAccount().get_social_by_user(user)
        # print("Categories", categories)
        # print("Socials", socials)
        # print(SocialAccount().SOCIAL_MEDIA_CHOICES)
        # for i in SocialAccount().SOCIAL_MEDIA_CHOICES:
        #     print(i)
        # for post in posts:
        #     print("="*20)
        #     for p in post.type.all():
        #         print(p)
        # for post in posts.type.all():
        #     print("="*20)
        #     print(post.type)

        return render(request, self.template_name, {'posts': posts, 'categories': categories, 'socials': socials, 'current_cat_id': id})


class AddPostView(View):
    def post(self, request):
        form = PostForm(request.POST, request.FILES)
        print(form)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your post has been added')
        else:
            messages.error(request, 'Unable to add post')
        # return redirect("workspace:ContentView")
        previous_url = request.META.get('HTTP_REFERER')
        if previous_url:
            return redirect(previous_url)


class DeletePostView(View):
    def post(self, request):
        post_id = request.POST.get('post_id')
        obj = Post(id=post_id)
        try:
            obj.delete()
            messages.success(request, 'Post deleted successfully')
        except:
            messages.error(request, 'Unable to delete the post!')
        
        # return redirect("workspace:ContentView")
        previous_url = request.META.get('HTTP_REFERER')
        if previous_url:
            return redirect(previous_url)


class EditCategoryView(View):
    error_message = "Unable to update the category!"
    def post(self, request):
        post_data = request.POST
        cat_id = post_data.get('id')
        form = CategoryForm(post_data)

        if form.is_valid():
            name = form.cleaned_data.get('name')
            desc = form.cleaned_data.get('description')
            try:
                Category.objects.filter(id=cat_id, user=request.user).update(name=name, description=desc)
                messages.success(request, 'Category updated')
            except:
                messages.error(request, self.error_message)
        else:
            messages.error(request, self.error_message)
        
        previous_url = request.META.get('HTTP_REFERER')
        if previous_url:
            return redirect(previous_url)


class DeleteCategoryView(View):
    def post(self, request):
        cat_id = request.POST.get('id')
        obj = Category(id=cat_id, user=request.user)
        try:
            obj.delete()
            messages.success(request, 'Category deleted successfully')
        except Exception as e:
            messages.error(request, 'Error: You might have some posts under this category, delete those posts first before deleting this category!')
            # print(e)
        
        previous_url = request.META.get('HTTP_REFERER')
        if previous_url:
            return redirect(previous_url)



class SchedulePostView(View):
    def get(self, request):
        social_accounts = request.user.social_posts_accounts.all()
        categories = request.user.categories.all()
        schedules = request.user.schedules.all().order_by("time")
        context = {
            "social_accounts": social_accounts,
            "categories": categories,
            "schedules": schedules,
        }
        return render(request, "workspace/schedule-setup.html", context)
    def post(self, request):
        print(request.POST)
        category = request.POST.get("category", None)
        category = Category.objects.get(id = category)

        social_accounts = request.POST.getlist("social_accounts", None)
        social_accounts = SocialAccount.objects.filter(id__in = social_accounts)

        days = request.POST.getlist("day", None)
        day_instance_ids = []
        for day in days:
            day_instance = DayName.objects.filter(name__iexact = day).first()
            if day_instance:
                day_instance_ids.append(day_instance.id)
        days = DayName.objects.filter(id__in = day_instance_ids)


        hour = request.POST.get("hour", None)
        minute = request.POST.get("minute", None)
        time = datetime.time(hour=int(hour), minute=int(minute))

        print(
            social_accounts,
            category,
            days,
            time,
        )

        for day in days:
            schedule, created = SchedulePost.objects.get_or_create(
                user = request.user,
                time = time,
                day = day
            )
            schedule.accounts.set(social_accounts)
            schedule.category = category
            schedule.save()
        return redirect("workspace:SchedulePostView")

class FbSelectPagesView(View):
    def get(self, request):
        token_instance = request.user.long_lived_tokens.filter(backend="facebook").first()
        token = token_instance.token
        previous_account_ids = request.user.social_posts_accounts.filter(backend="facebook", type="Page").values_list("unique_id", flat=True)
        # Sample Data
        # {
        #     'name': 'Lets code',
        #     'picture': {
        #         'data': {'height': 50,
        #             'is_silhouette': False,
        #             'url': '',
        #             'width': 50}
        #         },
        #     'access_token': '',
        #     'can_post': True,
        #     'category': 'Community',
        #     'id': '101465384542827'
        # }

        res = requests.get(
            url=f"https://graph.facebook.com/v13.0/me/accounts?fields=name,picture,can_post,category,access_token&access_token={token}"
        )
        # print(res.json())
        context = {"data": res.json()["data"], "previous_account_ids": previous_account_ids}
        return render(request, "workspace/facebook-pages-select.html", context)

    def post(self, request):
        
        name_inputs = request.POST.getlist("name", None)
        page_id_inputs = request.POST.getlist("page_id", None)
        token_inputs = request.POST.getlist("token", None)
        add_inputs = request.POST.getlist("add", None)
        image_inputs = request.POST.getlist("image", None)

        for index, add in enumerate(add_inputs):
            token = token_inputs[index]
            name = name_inputs[index]
            page_id = page_id_inputs[index]
            image_url = image_inputs[index]

            if add == "true":
                account, created = SocialAccount.objects.get_or_create(
                    user = request.user,
                    unique_id = page_id,
                    backend = 'facebook',
                )
                account.name = name
                account.token = token
                account.type = "Page"
                account.image = image_url
                account.save()
            elif add == "false":
                account = SocialAccount.objects.filter(
                    user = request.user,
                    unique_id = page_id,
                    backend = 'facebook',
                )
                account.delete()

        return redirect("workspace:FbSelectPagesView")

class FbSelectGroupsView(View):
    def get(self, request):
        token_instance = request.user.long_lived_tokens.filter(backend="facebook").first()
        token = token_instance.token
        previous_account_ids = request.user.social_posts_accounts.filter(backend="facebook", type="Group").values_list("unique_id", flat=True)

        res = requests.get(
            url=f"https://graph.facebook.com/v13.0/me/groups?admin_only=true&fields=name,picture,access_token&access_token={token}"
        )
        # print(res.json())
        context = {"data": res.json()["data"], "previous_account_ids": previous_account_ids}
        return render(request, "workspace/facebook-groups-select.html", context)

    def post(self, request):
        
        name_inputs = request.POST.getlist("name", None)
        group_id_inputs = request.POST.getlist("group_id", None)
        token_inputs = request.POST.getlist("token", None)
        add_inputs = request.POST.getlist("add", None)
        image_inputs = request.POST.getlist("image", None)

        for index, add in enumerate(add_inputs):
            token = token_inputs[index]
            name = name_inputs[index]
            page_id = group_id_inputs[index]
            image_url = image_inputs[index]

            if add == "true":
                account, created = SocialAccount.objects.get_or_create(
                    user = request.user,
                    unique_id = page_id,
                    backend = 'facebook',
                )
                account.name = name
                account.token = token
                account.type = "Group"
                account.image = image_url
                account.save()
            elif add == "false":
                account = SocialAccount.objects.filter(
                    user = request.user,
                    unique_id = page_id,
                    backend = 'facebook',
                )
                account.delete()

        return redirect("workspace:FbSelectGroupsView")

# id = res.json()["data"][0]["id"]
# name = res.json()["data"][0]["name"]
# access_token = res.json()["data"][0]["access_token"]
# graph = facebook.GraphAPI(access_token)
# graph.put_object(id, "feed", message=f"a test post on {name} for development purpose using API :)")




class TestPublishPost(View):
    def post(self, request):
        from requests_oauthlib import OAuth1Session, OAuth1
        accounts = request.user.social_posts_accounts.all()
        post_count = 0
        for account in accounts:
            if account.backend == "twitter":
                # media_init_url = f"https://upload.twitter.com/1.1/media/upload.json?command=INIT&total_bytes=10240&media_type=image/jpeg"
                # media_init_url = f"https://upload.twitter.com/1.1/media/upload.json"
                media_chunk_size = 500
                media_post_url = "https://upload.twitter.com/1.1/media/upload.json"
                post_url = 'https://api.twitter.com/1.1/statuses/update.json'

                token_instance = request.user.long_lived_tokens.filter(backend="twitter").first()
                token = json.loads(token_instance.token)

                oauth_token = token["oauth_token"]
                oauth_token_secret = token["oauth_token_secret"]

                session = OAuth1Session(settings.SOCIAL_AUTH_TWITTER_KEY,
                    client_secret=settings.SOCIAL_AUTH_TWITTER_SECRET,
                    resource_owner_key=oauth_token,
                    resource_owner_secret=oauth_token_secret)

                for post in account.posts.all():
                    try:
                        media_id = None
                        if post.image:
                            image_path = f"{settings.BASE_DIR}{post.image.url}"
                            with open(image_path, "rb") as file:
                                # Read the whole file at once
                                binary_data = file.read()
                                file_name, file_extension = os.path.splitext(image_path)
                                file_size = os.path.getsize(image_path) # in bytes
                                print(file_size)
                                name = f"From webapp {file_name}"
                                media_post_params = {
                                    "Name": name,
                                    "command": "INIT",
                                    "total_bytes": f"{file_size}",
                                    "media_type": f"{file_extension}",
                                }
                                media_post_headers = {
                                    'Content-Type': "application/form-data",
                                }
                                res = session.post(url=media_post_url, params=media_post_params, headers=media_post_headers)
                        if post.description:
                            post_params = {
                                'status': post.description,
                            }
                            if media_id:
                                post_params['media_ids'] = f'{media_id}'
                            res = session.post(url=post_url, params=post_params)
                            print("Posted: ", res)
                    except:
                        pass
                    post_count += 1
            elif account.backend == "facebook":
                token_instance = request.user.long_lived_tokens.filter(backend="facebook").first()
                token = token_instance.token
                if account.type == "Page":
                    graph = facebook.GraphAPI(account.token)
                elif account.type == "Group":
                    graph = facebook.GraphAPI(token)
                for post in account.posts.all():
                    try:
                        if post.image and account.type == "Page":
                            image_path = f"{settings.BASE_DIR}{post.image.url}"
                            graph.put_photo(image=open(image_path, 'rb'),
                                            message=post.description)
                        elif post.description:
                            graph.put_object(account.unique_id, "feed", message=f"{post.description}")
                    except:
                        pass
                    post_count += 1
        messages.success(request, f"Successfully, Published {post_count} Posted")
        return redirect("workspace:IndexView")