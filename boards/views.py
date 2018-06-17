from typing import NamedTuple, List, Optional

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods

from boards.forms import PostForm, ThreadForm, RegisterForm
from .models import Category, Thread, Post


@require_GET
def index(request):
    categories = Category.objects.filter(parent_category=None)
    threads = Thread.objects.filter(category=None)

    total_threads = Thread.objects.count()
    total_posts = Post.objects.count()

    return render(request, 'boards/index.html', {
        'categories': categories,
        'threads': threads,
        'total_threads': total_threads,
        'total_post': total_posts
    })


@require_GET
def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    breadcrumbs = _category_breadcrumb(category, last_active=False)

    return render(request, 'boards/category/detail.html', {
        'category': category,
        'breadcrumbs': breadcrumbs
    })


@require_http_methods(['GET', 'POST'])
def thread_detail(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return login_required()

        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.thread = thread
            post.author = request.user
            post.save()

            return HttpResponseRedirect(reverse('thread_detail', args=[thread_id]))

    else:  # GET
        form = PostForm()

    breadcrumbs = _category_breadcrumb(thread.category, last_active=True)

    return render(request, 'boards/thread/detail.html', {
        'thread': thread,
        'reply_form': form,
        'breadcrumbs': breadcrumbs
    })


@require_http_methods(['GET', 'POST'])
@login_required
def thread_create(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        category = None

    if request.method == 'POST':
        thread_form = ThreadForm(request.POST)
        post_form = PostForm(request.POST)

        if thread_form.is_valid() and post_form.is_valid():
            with transaction.atomic():
                post = post_form.save(commit=False)
                post.author_id = request.user.id
                post.thread_id = 0
                post.save()

                thread = thread_form.save(commit=False)
                thread.original_post_id = post.id
                thread.save()

                post.thread_id = thread.id
                post.save()

            return HttpResponseRedirect(reverse('thread_detail', args=[thread.id]))

    else:
        thread_form = ThreadForm(initial={'category': category})
        post_form = PostForm()

    return render(request, 'boards/thread/create.html', {
        'thread_form': thread_form,
        'post_form': post_form
    })


@require_http_methods(['GET', 'POST'])
@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        form = PostForm(request.POST)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse('thread_detail', args=[post.thread_id]))

    else:  # GET
        form = PostForm(instance=post)

    return render(request, 'boards/post/edit.html', {'post': post, 'post_form': form})


@require_http_methods(['GET', 'POST'])
@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.pk == post.thread.original_post.pk:
        # An original post cannot be deleted.
        # A thread itself must be deleted instead.
        raise Http404()

    if request.method == 'POST' and 'confirm_delete' in request.POST:
        thread_id = post.thread_id
        post.delete()
        return HttpResponseRedirect(reverse('thread_detail', args=[thread_id]))

    return render(request, 'boards/post/delete.html', {'post': post})


@require_GET
def user_detail(request, username):
    user = get_object_or_404(User, username=username)
    user_threads = Thread.objects.filter(original_post__author=user)
    user_thread_count = len(user_threads)
    user_post_count = user.post_set.count()

    return render(request, 'boards/user/detail.html', {
        'user': user,
        'user_threads': user_threads,
        'user_thread_count': user_thread_count,
        'user_post_count': user_post_count
    })


@require_http_methods(['GET', 'POST'])
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('login'))

    else:
        form = RegisterForm()

    return render(request, 'boards/auth/register.html', {'form': form})


class BreadcrumbItem(NamedTuple):
    label: str
    url: Optional[str] = None


def _category_breadcrumb(category: Optional[Category], last_active: bool) -> List[BreadcrumbItem]:
    items = [
        BreadcrumbItem(label='Home', url=reverse('index'))
    ]

    if category:
        for cat in category.get_path():
            items.append(BreadcrumbItem(
                label=cat.name,
                url=reverse('category_detail', args=[cat.id])
            ))

    if not last_active:
        items[-1] = BreadcrumbItem(
            label=items[-1].label,
            url=None
        )

    return items
