from django.shortcuts import get_object_or_404, render

from .models import Category, Post
from blogicum.constants import POSTS_NUMBER


def index(request):
    Posts = Post.published_posts.get_queryset()
    return render(
        request,
        'blog/index.html',
        {'post_list': Posts[:POSTS_NUMBER]}
    )


def post_detail(request, post_рк):
    Posts = Post.published_posts.get_queryset()
    post_detail = get_object_or_404(
        Posts,
        pk=post_рк
    )
    return render(
        request,
        'blog/detail.html',
        {'post': post_detail}
    )


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = category.posts.all()
    return render(
        request,
        'blog/category.html',
        {'post_list': post_list, 'category': category}
    )
