from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.urls import reverse_lazy, reverse
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Category, Post, User, Comment
from .forms import CommentForm, PostForm, UserForm


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class AuthorPermissionMixin(UserPassesTestMixin):

    def test_func(self):
        return self.get_object().author == self.request.user
    
    def handle_no_permission(self):
        return reverse_lazy('blog:post_detail', kwargs={'post_pk': self.get_object().id})


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


class PostEditView(LoginRequiredMixin, PostMixin, AuthorPermissionMixin, UpdateView):
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse_lazy('blog:index')


class PostDeleteView(LoginRequiredMixin, AuthorPermissionMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('blog:index')


class PostListView(ListView):
    template_name = 'blog/index.html'
    queryset = Post.published_posts.annotate(comment_count=Count("comment")).order_by('-pub_date')
    paginate_by = 10


class CategoryListView(ListView):
    paginate_by = 10
    template_name = 'blog/category.html'
    context_object_name = 'category'

    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs['category_slug'], is_published=True)
        return Post.published_posts.filter(category=category)
    

class ProfileListView(ListView):
    paginate_by = 10
    template_name = 'blog/profile.html'

    def get_queryset(self):
        author = get_object_or_404(User, username=self.kwargs['username'])
        if author != self.request.user:
            return Post.published_posts.filter(author=author).annotate(comment_count=Count("comment")).order_by('-pub_date')
        return Post.objects.filter(author=author).annotate(comment_count=Count("comment")).order_by('-pub_date')
    
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


class CommentMixin:
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'
    
    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs['pk'], is_published=True)
        return Comment.objects.filter(post_id=post.id)

    def get_success_url(self, **kwargs):
        return reverse('blog:post_detail', kwargs={'post_pk': self.kwargs['pk']})


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse('blog:post_detail', kwargs={'post_pk': self.kwargs['post_id']})


class CommentEditView(LoginRequiredMixin, CommentMixin, AuthorPermissionMixin, UpdateView):
    form_class = CommentForm
    pass


class CommentDeleteView(LoginRequiredMixin, CommentMixin, AuthorPermissionMixin, DeleteView):

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     print(context)
    pass
