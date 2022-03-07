from django import forms
from workspace.models import Category, Post

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "description")


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = "__all__"