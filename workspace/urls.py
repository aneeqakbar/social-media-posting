from django.urls import path
from . import views

app_name = "workspace"

urlpatterns = [
    path('', views.IndexView.as_view(), name='IndexView'),
    path('content/', views.ContentView.as_view(), name='ContentView'),
    path('content/<int:id>/', views.SingleContentView.as_view(), name='SingleContentView'),
    path('content/add-post/', views.AddPostView.as_view(), name='AddPost'),
    path('content/delete-post/', views.DeletePostView.as_view(), name='DeletePost'),
    path('content/edit-category/', views.EditCategoryView.as_view(), name='EditCategory'),
    path('content/delete-category/', views.DeleteCategoryView.as_view(), name='DeleteCategory'),
    path('schedule/', views.SchedulePostView.as_view(), name='SchedulePostView'),

    path('select-fb-pages/', views.FbSelectPagesView.as_view(), name='FbSelectPagesView'),
    path('select-fb-groups/', views.FbSelectGroupsView.as_view(), name='FbSelectGroupsView'),
    
    

    path('for-testing/', views.TestPublishPost.as_view(), name='TestPublishPost'),
]
