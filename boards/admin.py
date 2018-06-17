from django.contrib import admin

from .models import Category, Post, Thread

admin.site.register(Category)
admin.site.register(Thread)
admin.site.register(Post)
