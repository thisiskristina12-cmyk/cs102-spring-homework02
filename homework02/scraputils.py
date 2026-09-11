import requests
from bs4 import BeautifulSoup


def extract_news(parser):
    news_list = []

    articles = parser.find_all("article", class_="tm-articles-list__item")

    for art in articles:
        title_tag = art.find("a", class_="tm-title__link")
        if title_tag is None:
            continue

        title = title_tag.get_text(strip=True)
        href = title_tag.get("href", "")
        url = "https://habr.com" + href

        habr_id = art.get("id")

        author_tag = art.find("a", class_="tm-user-info__username")
        author = author_tag.get_text(strip=True) if author_tag else ""

        complexity_tag = art.find("span", class_="tm-article-snippet__complexity")
        complexity = complexity_tag.get_text(strip=True) if complexity_tag else ""

        news_list.append(
            {
                "title": title,
                "author": author,
                "url": url,
                "complexity": complexity,
                "habr_id": habr_id,
            }
        )

    return news_list


def extract_next_page(parser):
    next_btn = parser.find("a", id="pagination-next-page")
    if next_btn is not None:
        return next_btn.get("href")  # '/ru/articles/page2/'
    return None


def get_news(url, n_pages=1):
    news = []
    while n_pages:
        print("Collecting data from page: {}".format(url))

        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")

        news_list = extract_news(soup)
        news.extend(news_list)

        if n_pages > 1:
            next_page = extract_next_page(soup)
            if next_page is None:
                break
            url = "https://habr.com" + next_page

        n_pages -= 1

    return news
