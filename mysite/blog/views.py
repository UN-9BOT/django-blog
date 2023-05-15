from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from django.views.decorators.http import require_POST

from blog.models import Post
from blog.forms import CommentForm


class PostListView(ListView):
    """Альтернативное представление списка постов."""

    queryset = Post.published.all()
    context_object_name = 'posts'
    template_name = 'blog/post/list.html'


def post_list(request: HttpRequest) -> HttpResponse:
    posts: QuerySet = Post.published.all()
    return render(request, 'blog/post/list.html', {'posts': posts})


def post_detail(request: HttpRequest, year: int,
                month: int, day: int, post: Post) -> HttpResponse:
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    comments = post.comments.filter(active=True)  # type: ignore
    form = CommentForm()
    return render(request, 'blog/post/detail.html', {'post': post,
                                                     'comments': comments,
                                                     'form': form})


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
    return render(request, 'blog/post/comment.html',
                  {'post': post,
                   'form': form,
                   'comment': comment})
