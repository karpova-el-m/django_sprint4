from django.db import models
from django.utils import timezone
from django.db.models import Count


class PostsManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                pub_date__lte=timezone.now(),
                is_published=True,
                category__is_published=True,
                location__is_published=True,
            )
        )


class CommentManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(comment_count=Count("comment"))
            .order_by("-pub_date")
        )


class PublishedPostsCommentManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                pub_date__lte=timezone.now(),
                is_published=True,
                category__is_published=True,
                location__is_published=True,
            )
            .annotate(comment_count=Count("comment"))
            .order_by("-pub_date")
        )
