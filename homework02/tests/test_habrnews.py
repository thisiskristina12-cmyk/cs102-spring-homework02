from bottle import route, run, template, request, redirect

from scraputils import get_news
from db import News, session
from bayes import NaiveBayesClassifier

"/news"


def news_list():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    return template("news_template", rows=rows)


"/add_label/"


def add_label():
    label = request.query.get("label")
    news_id = request.query.get("id")

    s = session()
    news = s.query(News).filter(News.id == news_id).first()

    if news is not None:
        news.label = label
        s.commit()

    redirect("/news")


"/update"


def update_news():
    s = session()
    fresh = get_news("https://habr.com/ru/articles/", n_pages=15)

    for item in fresh:
        exists = s.query(News).filter(News.url == item["url"]).first()
        if exists is None:
            s.add(
                News(
                    title=item["title"],
                    author=item["author"],
                    url=item["url"],
                    complexity=item["complexity"],
                    habr_id=item["habr_id"],
                )
            )
    s.commit()


"/classify"


def classify_news():
    s = session()

    labeled = s.query(News).filter(News.label != None).all()
    unlabeled = s.query(News).filter(News.label == None).all()

    if not labeled:
        return unlabeled

    X_train = [n.title for n in labeled]
    y_train = [n.label for n in labeled]

    clf = NaiveBayesClassifier()
    clf.fit(X_train, y_train)

    def rank(news):
        label = clf.predict([news.title])[0]
        news.label = label
        return {"good": 0, "maybe": 1, "never": 2}.get(label, 3)

    ranked = sorted(unlabeled, key=rank)
    s.commit()

    return ranked
