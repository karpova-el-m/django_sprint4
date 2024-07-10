from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Category, Post, User
from .forms import CommentForm, PostForm, UserForm


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


class PostDetailView(DetailView):
    model = Post
    pk_url_kwarg = 'post_pk'
    template_name = 'blog/detail.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comment.select_related('author')
        )
        return context


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = User.objects.get(username=self.request.user)
        post.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        username = User.objects.get(username=self.request.user)
        return reverse('blog:profile', kwargs={'username': username})


class PostEditView(LoginRequiredMixin, PostMixin, UpdateView):
    pk_url_kwarg = 'post_id'


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('blog:index')


class PostListView(ListView):
    model = Post
    paginate_by = 10
    template_name = 'blog/index.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_obj'] = Post.objects.all()
        context['comment_count'] = Post.objects.annotate(Count('comment'))
        # context['comment_count'] = Post.comment.count()
        print(context['comment_count'])
        return context


class CategoryListView(ListView):
    paginate_by = 10
    template_name = 'blog/category.html'
    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        return Post.objects.filter(category=category)
    def get_context_data(self,**kwargs):
        context = super(CategoryListView,self).get_context_data(**kwargs)
        context['category'] = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        return context
    

class ProfileListView(ListView):
    paginate_by = 10
    template_name = 'blog/profile.html'
    def get_queryset(self):
        author = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.filter(author=author)
    def get_context_data(self,**kwargs):
        context = super(ProfileListView,self).get_context_data(**kwargs)
        context['profile'] = get_object_or_404(User, username=self.kwargs['username'])
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None, **kwargs):
        return self.request.user
    
    def get_success_url(self, **kwargs):
        return reverse('blog:profile', kwargs={'username': self.object})


def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:index') 
