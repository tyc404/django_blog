from .models import ArticlePost
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import ArticlePostForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from comment.models import Comment
import markdown

# Create your views here.

# 文章
def article_list(request):
    search = request.GET.get('search')
    order = request.GET.get('order')
    # 用户搜索逻辑
    if search:
        if order == 'total_views':
            article_list = ArticlePost.objects.filter(
                Q(title__icontains=search) |
                Q(body__icontains=search)
            ).order_by('-total_views')
        else:
            article_list = ArticlePost.objects.filter(
                Q(title__icontains=search) |
                Q(body__icontains=search)
            )
    else:
        # 将 search 参数重置为空
        search = ''
        if order == 'total_views':
            article_list = ArticlePost.objects.all().order_by('-total_views')
        else:
            article_list = ArticlePost.objects.all()

    paginator = Paginator(article_list, 3)
    page = request.GET.get('page')
    articles = paginator.get_page(page)
    context = { 'articles': articles, 'order': order, 'search': search }
    
    return render(request, 'article/list.html', context)
    

    

# 文章详情
def article_detail(request, id):
    article = ArticlePost.objects.get(id=id)
    article.total_views += 1
    article.save(update_fields=['total_views'])

    comments = Comment.objects.filter(article=id)
    # 将markdown语法渲染成html样式
    md = markdown.Markdown(
        extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        ]
    )
    article.body = md.convert(article.body)
    context = { 'article': article, 'toc': md.toc, 'comments': comments }
    return render(request, 'article/detail.html', context)

# 写文章
def article_create(request):
    if request.method == "POST":
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            new_article = article_post_form.save(commit=False)
            new_article.author = User.objects.get(id=request.user.id)
            new_article.save()
            return redirect("article:article_list")
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    else:
        article_post_form = ArticlePostForm()
        context = { 'article_post_form': article_post_form }
        return render(request, 'article/create.html', context)
    
# 删文章
def article_delete(request, id):
    if request.user != article.author:
        return HttpResponse("抱歉，你无权删除这篇文章。")
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        article.delete()
        return redirect("article:article_list")
    else:
        return redirect("article:article_list")
        return HttpResponse("仅允许post请求")
    
# 更新文章
def article_update(request, id):

    article = ArticlePost.objects.get(id=id)
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")
    if request.method == "POST":
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            article.title = request.POST['title']
            article.body = request.POST['body']
            article.save()
            return redirect("article:article_detail", id=id)
        else:
            return HttpResponse("表单内容有误，请重新填写。")

    else:
        article_post_form = ArticlePostForm()
        context = { 'article': article, 'article_post_form': article_post_form }
        return render(request, 'article/update.html', context)
    

