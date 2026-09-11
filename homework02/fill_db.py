from scraputils import get_news
from db import News, session

s = session()

print("Начинаем сбор...")
news = get_news('https://habr.com/ru/articles/', n_pages=15)
print(f"Собрано с Habr: {len(news)}")

added = 0
for item in news:
    exists = s.query(News).filter(News.url == item['url']).first()
    if exists is None:
        s.add(News(
            title=item['title'],
            author=item['author'],
            url=item['url'],
            complexity=item['complexity'],
            habr_id=item['habr_id'],
        ))
        added += 1

s.commit()
print(f"Добавлено новых: {added}")
print(f"Всего в БД: {s.query(News).count()}")