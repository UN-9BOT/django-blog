from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User


class PublishedManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):

    class Status(models.TextChoices):
        """Status code. Based on enum."""

        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title: models.CharField = models.CharField(max_length=255)
    slug: models.SlugField = models.SlugField(max_length=255,
                                              unique_for_date='publish')
    body: models.TextField = models.TextField()
    publish: models.DateField = models.DateField(default=timezone.now)
    created: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated: models.DateTimeField = models.DateTimeField(auto_now=True)
    status: models.CharField = models.CharField(max_length=255,
                                                choices=Status.choices,
                                                default=Status.DRAFT)
    author: models.ForeignKey = models.ForeignKey(User,
                                                  on_delete=models.CASCADE,
                                                  related_name='blog_posts')
    objects: models.Manager = models.Manager()
    published: PublishedManager = PublishedManager()

    class Meta:
        ordering: list[str] = ["-publish"]
        indexes: list[models.Index] = [models.Index(fields=["-publish"])]

    def __str__(self) -> str:
        return f"{self.title}"

    def get_absolute_url(self) -> str:
        return reverse('blog:post_detail', args=[self.publish.year,
                                                 self.publish.month,
                                                 self.publish.day,
                                                 self.slug])


class Comment(models.Model):
    post: models.ForeignKey = models.ForeignKey(Post,
                                                on_delete=models.CASCADE,
                                                related_name='comments')
    name: models.CharField = models.CharField(max_length=80)
    email: models.EmailField = models.EmailField()
    body: models.TextField = models.TextField()
    created: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated: models.DateTimeField = models.DateTimeField(auto_now=True)
    active: models.BooleanField = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [models.Index(fields=['created'])]

    def __str__(self) -> str:
        return f"Comment by {self.name} on {self.post}"
