import hashlib
import logging

from bs4 import BeautifulSoup
from newspaper import Article

from memorious import operations
from memorious.helpers.rule import Rule

log = logging.getLogger(__name__)


def crawl(context, data):
    with context.http.rehash(data) as result:
        news_article = Article(url=data["url"])
        news_article.download()
        news_article.parse()
        data["entity_id"] = hashlib.md5(data["url"].encode("utf-8")).hexdigest()
        soup = BeautifulSoup(news_article.html)
        title = soup.find("div", {"id": "PRHeadline"})
        published_at = soup.find("div", {"class": "mB15 f15"})
        text = soup.find("span", {"id": "pressrelease"})

        if title and published_at and text:
            data["properties"] = {"title": str(title.get_text(separator=' ', strip=True)),
                                  "published_at": str(published_at.get_text(separator=' ', strip=True)),
                                  "text": str(text.get_text(separator=' ', strip=True))}
        else:
            data["properties"] = {}
        if result.html is not None:
            operations.parse.parse_html(context, data, result)

        rules = context.params.get("match") or {"match_all": {}}
        if Rule.get_rule(rules).apply(result):
            context.emit(rule="store", data=data)
