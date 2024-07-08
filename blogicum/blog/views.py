from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.urls import reverse_lazy
from django.core.paginator import Paginator

from .models import Category, Post, User
from .forms import PostForm


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


class PostDetailView(DetailView):
    model = Post
    pk_url_kwarg = 'post_pk'
    template_name = 'blog/detail.html'


class PostCreateView(PostMixin, CreateView):
    pass


class PostEditView(PostMixin, UpdateView):
    pk_url_kwarg = 'post_id'


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('blog:index')


class PostListView(ListView):
    model = Post
    paginate_by = 10
    template_name = 'blog/index.html'


class UserDetailView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    slug_field = 'username'
    context_object_name = 'profile'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = (
            self.object.posts.select_related('author')
        )
        paginator = Paginator(context['posts'], 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'page_obj': page_obj}
        return context
    