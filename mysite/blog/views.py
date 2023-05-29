"""Views for pages."""
from typing import Optional

from django.db.models import QuerySet, Count
from django.forms import SlugField
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from django.views.decorators.http import require_POST
# from django.contrib.postgres.search import (
#     SearchVector, SearchQuery, SearchRank)
from django.contrib.postgres.search import TrigramSimilarity


from taggit.models import Tag

from blog.models import Post
from blog.forms import CommentForm, SearchForm


class PostListView(ListView):
    """Альтернативное представление списка постов."""

    queryset = Post.published.all()
    context_object_name = 'posts'
    template_name = 'blog/post/list.html'


def post_list(request: HttpRequest,
              tag_slug: Optional[SlugField] = None) -> HttpResponse:
    """View for all post. """
    posts: QuerySet = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags__in=[tag])
    return render(request, 'blog/post/list.html', {'posts': posts,
                                                   'tag': tag})


def post_detail(request: HttpRequest, year: int, month: int, day: int,
                post: Post) -> HttpResponse:
    """View for 1 post. """
    post = get_object_or_404(
        Post, status=Post.Status.PUBLISHED, slug=post, publish__year=year,
        publish__month=month, publish__day=day)
    comments = post.comments.filter(active=True)  # type: ignore
    form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(
        tags__in=post_tags_ids).exclude(
        id=post.id)  # type: ignore
    similar_posts = similar_posts.annotate(
        same_tags=Count('tags')).order_by(
        '-same_tags', '-publish')

    return render(
        request, 'blog/post/detail.html',
        {'post': post, 'comments': comments, 'form': form,
         'similar_posts': similar_posts})


@require_POST
def post_comment(request: HttpRequest, post_id: int) -> HttpResponse:
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    return render(
        request, 'blog/post/comment.html',
        {'post': post, 'form': form, 'comment': comment})


def post_search(request: HttpRequest):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # search_query = SearchQuery(query)
            # search_vector = SearchVector('title', 'body')
            # results = Post.published.annotate(
            #     search=search_vector,
            #     rank=SearchRank(search_vector, search_query)).filter(
            #     search=search_query).order_by('-rank')
            results = Post.published.annotate(
                similarity=TrigramSimilarity('title', query),
            ).filter(similarity__gt=0.1).order_by('-similarity')

    return render(request, "blog/post/search.html", {
        'form': form, 'query': query, 'results': results
    })
