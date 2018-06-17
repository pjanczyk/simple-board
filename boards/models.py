from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone


class Category(models.Model):
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=200)
    description = models.TextField()
    parent_category = models.ForeignKey("Category", null=True, blank=True, on_delete=models.SET_NULL,
                                        related_name='category_set')

    def get_path(self):
        path = [self]
        c = self.parent_category
        while c:
            path.append(c)
            c = c.parent_category
        path.reverse()
        return path

    def __str__(self):
        return ' » '.join(c.name for c in self.get_path())


class Thread(models.Model):
    class Meta:
        ordering = ['-created_at']

    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField()
    original_post = models.ForeignKey('Post', on_delete=models.PROTECT, related_name='+')

    def save(self, *args, **kwargs):
        if not self.id and not self.created_at:
            self.created_at = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def original_author(self):
        return self.original_post.author


class Post(models.Model):
    class Meta:
        ordering = ['created_at']

    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    text = models.TextField(validators=[MinLengthValidator(1)])
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    created_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.id and not self.created_at:
            self.created_at = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.text

    def is_original_post(self):
        return self.pk == self.thread.original_post.pk
