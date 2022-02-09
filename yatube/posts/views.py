from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
# from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, Comment, Follow

User = get_user_model()
POST_CNT = 10


# @cache_page(20)
def index(request):
    post_list = Post.objects.all().order_by('-pub_date')

    paginator = Paginator(post_list, POST_CNT)

    page_number = request.GET.get('page')
    title = 'Главная страница'
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):

    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')
    paginator = Paginator(posts, POST_CNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = 'Посты группы ' + str(group)
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, 'posts/group.html', context)


def group_list(request):
    template = 'posts/group_list.html'
    return render(request, template)


def profile(request, username):
    author = User.objects.get(username=username)
    posts = Post.objects.filter(author=author).order_by('-pub_date')
    paginator = Paginator(posts, POST_CNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    count = Post.objects.filter(author=author).count()
    title = 'Профайл пользователя ' + str(author)
    context = {
        'page_obj': page_obj,
        'author': author,
        'count': count,
        'title': title,
        'following': False,
    }
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            author=author, user=request.user
        ).exists()
        context.update({
            'following': following,
            'user': request.user,
        })
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    text = post.text
    title = text[:30]
    pub_date = post.pub_date
    author = post.author
    count_posts = author.posts.all().count()
    group = post.group
    comments = Comment.objects.filter(post=post_id)
    form = CommentForm(request.POST or None)
    context = {
        'text': text,
        'title': title,
        'pub_date': pub_date,
        'author': author,
        'count_posts': count_posts,
        'group': group,
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    author = get_object_or_404(User, username=request.user)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if request.method == "POST":
        if form.is_valid():
            deform = form.save(commit=False)
            deform.author = author
            deform.save()
            return redirect("posts:profile", username=author)
    context = {"form": form}
    return render(request, "posts/post_create.html", context)


@login_required
def post_edit(request, post_id):
    author = get_object_or_404(User, username=request.user)
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if author != post.author:
        return redirect("posts:post_detail", post_id=post_id)
    if request.method == "POST":
        if form.is_valid():
            deform = form.save(commit=False)
            deform.author = author
            deform.save()
            return redirect("posts:post_detail", post_id=post_id)
    context = {"form": form, "is_edit": True}
    return render(request, "posts/post_create.html", context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if request.GET or not form.is_valid():
        return render(
            request,
            'posts/comments.html', {
                'post': post,
                'form': form}
        )
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    authors_list = Follow.objects.filter(
        user=request.user
    ).values_list('author')
    post_list = Post.objects.filter(
        author__in=authors_list
    ).order_by('-pub_date')
    paginator = Paginator(post_list, POST_CNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'paginator': paginator,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(author=author, user=user).exists()
    if user != author and not following:
        follow = Follow.objects.create(
            user=user,
            author=author
        )
        follow.save()
    return redirect(reverse('posts:profile', kwargs={'username': username}))


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    following = Follow.objects.select_related('user').filter(
        author=author,
        user=user
    )
    if user != author:
        if following.exists():
            following.delete()
    return redirect(reverse('posts:profile', kwargs={'username': username}))
