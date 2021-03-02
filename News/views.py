from django.shortcuts import render, HttpResponseRedirect, reverse, HttpResponse, redirect
import feedparser
from django.utils import timezone, dateparse
from django import forms
from .models import Article, Feed, News_Category
from datetime import datetime, timedelta, tzinfo, timezone
from django.core.paginator import Paginator
from django.views.generic import ListView
import sched, pytz, schedule, time
import dateutil.parser
from tzlocal import get_localzone
from time import gmtime, strftime

date_group = ["1","2","3","7","15","30"]

class articles(ListView):
    model = Article
    paginate_by = 21

def remove_html_markup(s):
    tag = False
    quote = False
    out = ""
    for c in s:
            if c == '<' and not quote:
                tag = True
            elif c == '>' and not quote:
                tag = False
            elif (c == '"' or c == "'") and tag:
                quote = not quote
            elif not tag:
                out = out + c
    return out

# Create your views here.

def get_img_list(all_articles):
    img_src_list = []
    for each in all_articles:
        if "img" in each.summary:
            start = each.summary.find("<img")
            end = each.summary.find("/>",start) + 2
            img_src_list.append(each.summary[start:end])
        else:
            img_src_list.append("")
    return img_src_list

def gettime():
    d = datetime.now()
    curr_d = d.strftime('%Y-%m-%d %H:%M:%S %z %Z')
    datestring = "2021-02-19T09:14:57+05:30"
    print(curr_d)
    print(strftime("%z", gmtime()))
    dm = dateutil.parser.parse(datestring)
    print(dm)
    #print(str(d.replace(timezone.utc)))
    #print(d.utcoffset())
    #d = d.replace(timezone.utc) - d.utcoffset()
       

def articles(request,category):
    category = category.capitalize()
    news_category = News_Category.objects.filter(category=category)
    if news_category:
        all_articles = Article.objects.filter(feed__feed_category__category=category).order_by('-publication_date')
    elif category in date_group:
        enddate = datetime.today()
        startdate = enddate - timedelta(days=int(category))
        all_articles = Article.objects.filter(publication_date__range=[startdate, enddate]).order_by('feed__feed_category__id').order_by('-publication_date')
        category = "All Articles"
    else:
        return HttpResponse(f"<h1>News Category - '{category}' is not available.</h1>")
    img_src_list = get_img_list(all_articles)
    paginator, paginator_img = Paginator(all_articles, 21), Paginator(img_src_list, 21)
    try:
        page = request.GET['page']
    except Exception as e:
        page = 1 # The Default value when erros comes
    all_articles, img_src_list = paginator.get_page(page), paginator_img.get_page(page)
    page_range = list(i for i in range(1,paginator.num_pages))

    articles = zip(all_articles, img_src_list)
    print(all_articles)
    return render(request, "news/index.html",{
        "category" : category,
        "articles" : articles,
        "all_articles" : all_articles,
        "img_src_list" : img_src_list,
        'page_range': page_range,
    })


def feeds(request):
    all_feeds = Feed.objects.all()
    if request.method == "POST":
        form = NewFeedForm(request.POST)
        if "btn-add-feed" in request.POST:
            if form.is_valid():
                feed = form.save(commit=False)
                #Check whether feed already exists in DB
                existing_feed = Feed.objects.filter(url=feed.url)
                if len(existing_feed) == 0:
                    #create new feed and create new article entries
                    title = feedparser.parse(feed.url).feed["title"]
                    feed.title = title
                    feed.isActive = True
                    feed.save()
                feed_entry = Feed.objects.get(url=feed.url)
                create_new_entry(feed_entry,feed.url)
                category = str(feed.feed_category)
                return HttpResponseRedirect(reverse('feeds'))
        elif "feed-id" in request.POST:
            Feed.objects.filter(id=request.POST["feed-id"]).delete()
            return HttpResponseRedirect(reverse('feeds'))
        else:
            return render(request, "news/feeds.html",{
                "feeds" : all_feeds,
                "form" : form
            })
    return render(request, "news/feeds.html",{
        "feeds" : all_feeds,
        "form" : NewFeedForm()
    })


def create_new_entry(feed_entry, feed_url):
    entries = feedparser.parse(feed_url).entries
    titles = Article.objects.filter(feed=feed_entry).order_by("-publication_date").values_list("title")
    for entry in entries:
        if any(entry["title"] in title for title in titles):
            break
        else:
            date_string = datetime.now()
            if entry['published_parsed']:
                d = datetime(*(entry.published_parsed[0:6]))
                #print(entry.published[-3:])
                #print(entry['published'])
                date_string = d.strftime('%Y-%m-%d %H:%M:%S')
            description=""
            summary=str(entry["summary"]).split("</a>")
            if len(summary) > 1 and summary[1]:
                description = remove_html_markup(entry["summary"])
                summary = summary[0]
            article = Article.objects.create(
                feed=feed_entry,
                title=entry["title"],
                url=entry["link"],
                summary=entry["summary"],
                description=description,
                publication_date=date_string
            )
            article.save()
            remove_extras(article.id)
    
    return True


class NewFeedForm(forms.ModelForm):
    class Meta:
        model = Feed
        fields = ('url','feed_category',)
        #url.widget.attrs.update({'class': 'feed-input'})
        #widgets = {
        #    'url': forms.TextInput(attrs={'class': 'feed-input'}),
        #    'feed_category': forms.CharField(attrs={'class': 'feed-input'}),
        #}

def remove_extras(article_id):
    article = Article.objects.get(id=article_id)
    if article.summary[:2] == "rr":
        temp = article.summary[2:-2]
        print("=========================== New Article =================================")
        print(article.summary)
        article.summary = temp
        article.save(update_fields=['summary'])
