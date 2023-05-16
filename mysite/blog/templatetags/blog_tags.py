from django import template
from django.db.models import QuerySet
from ..models import Post

register = template.Library()


@register.simple_tag
def total_posts() -> int:
    return Post.published.count()


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count: int = 5) -> dict[str, QuerySet]:
    latest_posts: QuerySet[Post] = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}
