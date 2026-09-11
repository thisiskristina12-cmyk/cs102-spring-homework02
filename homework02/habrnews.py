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

    redirect("/news")


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
    redirect("/news")


@route("/classify")
def classify_news():
    s = session()

    labeled = s.query(News).filter(News.label != None).all()
    if not labeled:
        return redirect("/news")

    X_train = [n.title for n in labeled]
    y_train = [n.label for n in labeled]

    clf = NaiveBayesClassifier()
    clf.fit(X_train, y_train)

    unlabeled = s.query(News).filter(News.label == None).all()
    for news in unlabeled:
        news.label = clf.predict([news.title])[0]

    s.commit()
    redirect("/news")


if __name__ == "__main__":
    run(host="localhost", port=8080)
