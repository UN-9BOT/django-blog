from django import template
from django.db.models import Count, QuerySet
from django.utils.safestring import SafeString, mark_safe
import markdown
import bleach

from ..models import Post


register = template.Library()


@register.simple_tag
def total_posts() -> int:
    """Счетчик всех постов."""
    return Post.published.count()


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count: int = 5) -> dict[str, QuerySet]:
    """Список последних постов."""
    latest_posts: QuerySet[Post] = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


@register.simple_tag
def get_most_commented_posts(count: int = 5) -> QuerySet[Post]:
    """Получение постов с наибольшим кол-вом комментов."""
    return Post.published.annotate(
        total_comments=Count('comments')).order_by('-total_comments')[:count]


@register.filter(name='markdown')
def markdown_format(text) -> SafeString:  # type: ignore
    """Написание постов в стиле markdown. Обработано через bleach."""
    sanitized_text: str = bleach.clean(text, tags=bleach.ALLOWED_TAGS)
    return mark_safe(markdown.markdown(sanitized_text))  # nosec
