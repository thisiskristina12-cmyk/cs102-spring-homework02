from bottle import route, run, template, request, redirect

from scraputils import get_news
from db import News, session
from bayes import NaiveBayesClassifier


@route("/news")
def news_list():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    return template("news_template", rows=rows)


@route("/add_label/")
def add_label():
    label = request.query.get("label")
    news_id = request.query.get("id")

    s = session()
    news = s.query(News).filter(News.id == news_id).first()

    if news is not None:
        news.label = label
        s.commit()



@route("/update")
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


@route("/classify")
def classify_news():
    s = session()
    labeled = s.query(News).filter(News.label != None).all()
    unlabeled = s.query(News).filter(News.label == None).all()

    if not labeled:
        return unlabeled

    clf = NaiveBayesClassifier()
    clf.fit([n.title for n in labeled], [n.label for n in labeled])

    def rank(news):
        news.label = clf.predict([news.title])[0]
        return {"good": 0, "maybe": 1, "never": 2}.get(news.label, 3)

    ranked = sorted(unlabeled, key=rank)
    s.commit()
    return ranked


if __name__ == "__main__":
    run(host="localhost", port=8080)
