from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from core.models import BaseModel
from blogicum.constants import MAX_LENGTH, MAX_NAME_LENGTH

User = get_user_model()


class PostsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
            location__is_published=True,
        )


class Location(BaseModel):
    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Название места'
    )

    class Meta(BaseModel.Meta):
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:MAX_NAME_LENGTH]


class Category(BaseModel):
    title = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        ),
    )

    class Meta(BaseModel.Meta):
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:MAX_NAME_LENGTH]


class Post(BaseModel):
    title = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Заголовок'
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        editable=True,
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем '
            '— можно делать отложенные публикации.'
        ),
    )
    author = models.ForeignKey(
        User,
        related_name='posts',
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        editable=False,
    )
    location = models.ForeignKey(
        Location,
        related_name='posts',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='posts',
        null=True,
        verbose_name='Категория',
    )
    image = models.ImageField(
        'Фото',
        blank=True,
        upload_to='post_images'
    )

    published_posts = PostsManager()
    objects = models.Manager()

    class Meta():
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date']
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'text', 'author',),
                name='Unique post constraint',
            ),
        )
    
    def __str__(self):
        return self.title[:MAX_NAME_LENGTH]


class Comment(models.Model):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE,
        related_name='comment',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['created_at',]
