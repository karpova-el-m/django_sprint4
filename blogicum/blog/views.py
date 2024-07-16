from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from blogicum.constants import POSTS_PER_PAGE
from .forms import CommentForm, UserForm
from .models import Category, Comment, Post
from .mixins import PostMixin, AuthorPermissionMixin, CommentMixin

User = get_user_model()


class PostDetailView(DetailView):
    model = Post
    pk_url_kwarg = "post_pk"
    template_name = "blog/detail.html"

    def get_object(self):
        if self.request.user.is_anonymous:
            post = get_object_or_404(
                Post.published_posts, Q(pk=self.kwargs[self.pk_url_kwarg])
            )
        else:
            post = get_object_or_404(
                Post.objects, (
                    (
                        Q(author=self.request.user)
                        | (
                            Q(is_published=True)
                            & Q(category__is_published=True)
                            & Q(pub_date__lte=timezone.now())
                        )
                    )
                    & Q(pk=self.kwargs[self.pk_url_kwarg])
                ),
            )
        return post

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            form=CommentForm(),
            comments=(self.object.comment.select_related("author"))
        )


class PostCreateView(
    LoginRequiredMixin, PostMixin, CreateView
):

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = User.objects.get(username=self.request.user)
        post.save()
        return super().form_valid(form)

    def get_success_url(self):
        username = User.objects.get(username=self.request.user)
        return reverse_lazy("blog:profile", kwargs={"username": username})


class PostEditView(
    LoginRequiredMixin, PostMixin, AuthorPermissionMixin, UpdateView
):
    pk_url_kwarg = "post_id"

    def get_success_url(self):
        return reverse_lazy("blog:index")


class PostDeleteView(
    LoginRequiredMixin, AuthorPermissionMixin, DeleteView
):
    model = Post
    template_name = "blog/create.html"
    pk_url_kwarg = "post_id"
    success_url = reverse_lazy("blog:index")


class PostListView(ListView):
    template_name = "blog/index.html"
    queryset = Post.published_posts_comments.all()
    paginate_by = POSTS_PER_PAGE


class CategoryListView(ListView):
    paginate_by = POSTS_PER_PAGE
    template_name = "blog/category.html"
    context_object_name = "category"

    def get_queryset(self):
        category = get_object_or_404(
            Category, slug=self.kwargs["category_slug"], is_published=True
        )
        return Post.published_posts.filter(category=category)


class ProfileListView(ListView):
    paginate_by = POSTS_PER_PAGE
    template_name = "blog/profile.html"

    def get_queryset(self):
        author = get_object_or_404(User, username=self.kwargs["username"])
        if self.request.user.is_anonymous:
            post = Post.published_posts_comments.filter(author=author)
        else:
            post = Post.post_comments.filter(
                Q(author=self.request.user)
                | (
                    Q(author=author)
                    & Q(is_published=True)
                    & Q(category__is_published=True)
                    & Q(pub_date__lte=timezone.now())
                )
            )
        return post

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            profile=get_object_or_404(User, username=self.kwargs["username"])
        )


class ProfileEditView(
    LoginRequiredMixin, UpdateView
):
    model = User
    form_class = UserForm
    template_name = "blog/user.html"
    success_url = reverse_lazy("blog:index")

    def get_object(self, queryset=None, **kwargs):
        return self.request.user

    def get_success_url(self, **kwargs):
        return reverse_lazy(
            "blog:profile",
            kwargs={"username": self.object}
        )


class CommentCreateView(
    LoginRequiredMixin, CreateView
):
    model = Comment
    form_class = CommentForm
    template_name = "blog/comment.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs["post_id"])
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse_lazy(
            "blog:post_detail", kwargs={"post_pk": self.kwargs["post_id"]}
        )


class CommentEditView(
    LoginRequiredMixin, CommentMixin, AuthorPermissionMixin, UpdateView
):
    form_class = CommentForm


class CommentDeleteView(
    LoginRequiredMixin, CommentMixin, AuthorPermissionMixin, DeleteView
):
    pass
