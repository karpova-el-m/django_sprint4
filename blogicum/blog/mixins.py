from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy

from .forms import PostForm
from .models import Comment, Post


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"


class AuthorPermissionMixin(UserPassesTestMixin):

    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        return redirect("blog:post_detail", post_pk=self.get_object().id)


class CommentMixin:
    model = Comment
    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_id"

    def get_queryset(self):
        return Comment.objects.select_related('post')

    def get_success_url(self, **kwargs):
        return reverse_lazy(
            "blog:post_detail",
            kwargs={"post_pk": self.kwargs["pk"]}
        )
