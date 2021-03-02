from .models import News_Category, Feed, Article
from .views import create_new_entry
from datetime import datetime, timedelta, tzinfo, timezone

counter = 0

def update_latest_articles():
    global counter
    print("running every minute" + str(counter))
    counter += 1
    print(counter)
    # create_new_entry()
    all_feeds = Feed.objects.all()
    #print(all_feeds)
    for feed_entry in all_feeds:
        feed_url = feed_entry.url
        if feed_entry.isActive:
            create_new_entry(feed_entry, feed_url)


def delete_old_articles():
    print("Deleting ....")
    startdate = datetime.today() - timedelta(days=3)
    enddate = datetime.today() - timedelta(days=2)
    Article.objects.filter(publication_date__range=[startdate, enddate]).delete()