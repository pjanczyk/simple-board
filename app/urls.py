from django.contrib.auth import views as auth_views
from django.urls import path

from app import views

urlpatterns = [
    path('login', auth_views.LoginView.as_view(template_name='app/auth/login.html'), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('change-password', auth_views.PasswordChangeView.as_view(template_name='app/auth/change_password.html'),
         name='password_change'),
    path('register', views.register, name='register'),

    path('', views.index, name='index'),
    path('categories/<int:category_id>', views.category_detail, name='category_detail'),
    path('categories/<int:category_id>/new-thread', views.thread_create, name='thread_create'),
    path('threads/<int:thread_id>', views.thread_detail, name='thread_detail'),
    path('users/<str:username>', views.user_detail, name='user_detail'),
    path('posts/<int:post_id>/edit', views.post_edit, name='post_edit'),
    path('posts/<int:post_id>/delete', views.post_delete, name='post_delete')
]
