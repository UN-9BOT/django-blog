from django.contrib import admin

from blog.models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display: list = ['title', 'slug', 'author', 'publish', 'status']
    prepopulated_fields: dict = {'slug': ('title',)}  # предзаполнение поля
    # raw_id_fields: list = ['author']
    date_hierarchy: str = 'publish'  # навигация по датам
    ordering: list = ['status', 'publish']  # сортировка
