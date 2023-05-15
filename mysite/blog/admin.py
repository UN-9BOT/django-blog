from django.contrib import admin

from blog.models import Comment, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display: list = ['title', 'slug', 'author', 'publish', 'status']
    prepopulated_fields: dict = {'slug': ('title',)}  # предзаполнение поля
    # raw_id_fields: list = ['author']
    date_hierarchy: str = 'publish'  # навигация по датам
    ordering: list = ['status', 'publish']  # сортировка


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'post', 'created', 'active']
    list_filter = ['active', 'created', 'updated']
    search_fields = ['name', 'email', 'body']
