from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Group, Post, Comment, Follow

User = get_user_model()


def paginator_post(posts_list, request):
    paginator = Paginator(posts_list, settings.COUNT_IN_PAGES)
    page_number = request.GET.get('page')
    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    post_list = Post.objects.all()
    page_obj = paginator_post(post_list, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.all()
    page_obj = paginator_post(posts_list, request)
    template = 'posts/group_list.html'
    context = {
        'posts': posts_list,
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    all_posts_user = author.posts.all()
    page_obj = paginator_post(all_posts_user, request)
    template = 'posts/profile.html',
    following = False
    exist_follow = Follow.objects.filter(
        user=request.user.is_authenticated,
        author=author).exists()
    if request.user != author and exist_follow:
        following = True
    context = {
        'page_obj': page_obj,
        'author': author,
        'all_posts_user': all_posts_user,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.filter(post=post)
    form = CommentForm(request.POST or None)
    count_post = post.author.posts.all().count()
    context = {
        'post': post,
        'count_post': count_post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required()
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        instance = form.save(commit=False)
        instance.author = request.user
        instance.save()
        return redirect('posts:profile', instance.author)
    context = {
        'form': form,
        'is_edit': False
    }
    return render(request, 'posts/create_post.html', context)


@login_required()
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = request.user
    if post.author != user:
        return redirect('posts:post_detail', post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)

    context = {
        'form': form,
        'is_edit': True,
        'post_id': post_id
    }
    return render(request, 'posts/create_post.html', context)


@login_required()
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required()
def follow_index(request):
    post_list = Post.objects.filter(
        author__following__user=request.user)

    page_obj = paginator_post(post_list, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required()
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user,
            author=author)
    return redirect('posts:profile', username=username)


@login_required()
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(
        user=request.user).filter(
        author=author).delete()
    return redirect('posts:profile', username=username)
