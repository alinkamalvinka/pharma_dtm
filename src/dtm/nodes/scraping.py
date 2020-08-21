from pyquery import PyQuery
import urllib
import lxml.html as html
import pandas as pd
import numpy as np


def get_journal_links(
    publisher_link: str, journal_id, journal_volumes, journal_max_issues, start_year
):
    links, years = [], []
    year = start_year
    print("Getting journal links")

    for volume in range(1, journal_volumes + 1):
        for issue in range(1, journal_max_issues + 1):
            link = (
                publisher_link
                + "/journal/"
                + journal_id
                + "/"
                + str(volume)
                + "/"
                + str(issue)
            )
            links.append(link)
            years.append(year)

            link = link + "/page/2"
            links.append(link)
            years.append(year)

        year = year + 1

    return links, years


def get_article_links(journal_link):
    print(journal_link)
    try:
        data = urllib.request.urlopen(journal_link).read()
        pq = PyQuery(data)
        articles = pq("h3.title>a").map(lambda _, x: x.attrib["href"])
    except:
        articles = []
        pass
    print("Getting article links")
    return articles


def get_all_links(
    publisher_link, period_start, period_end, journal_links, journal_years
):
    period = np.arange(period_start, period_end)
    articles_list_links, articles_years = [], []

    for link, year in zip(journal_links, journal_years):
        if year in period:
            articles_links = get_article_links(link)
            for a_l in articles_links:
                article_link = publisher_link + a_l
                articles_list_links.append(article_link)
                articles_years.append(year)

    print("length  links  ", len(articles_list_links))

    return articles_list_links, articles_years


def extract_data(article_link):
    print("extract data")

    test = PyQuery(["test"])
    title, tip, date, abstract, abbreviations, funding, keywords = (
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )

    try:
        while test.length > 0:
            html_data = urllib.request.urlopen(article_link).read()
            pq = PyQuery(html_data)
            test = pq("h1.ArticleTitle").map(lambda _, x: x.text)

        tree = html.fromstring(html_data)

        title_xpath = '//*[@id="main-content"]/div/main/article/div[1]/header/h1/text()'
        title = tree.xpath(title_xpath)

        path_type = (
            '//*[@id="main-content"]/div/main/article/div[1]/header/ul[1]/li[1]/text()'
        )
        tip = tree.xpath(path_type)

        date_xpath = '//*[@id="enumeration"]/p[2]/span[1]/time/text()'
        date = tree.xpath(date_xpath)

        abbreviations_path = '//*[@id="abbreviations-content"]/dl/dd/p/text()'
        abbreviations = tree.xpath(abbreviations_path)

        funding_path = '//*[@id="Ack1-content"]/p/text()'
        funding = tree.xpath(funding_path)

        key_path = '//*[@id="article-info-content"]/div/div[2]/ul[2]/li/span/text()'
        keywords = tree.xpath(key_path)

        abstract_path = '//*[@id="Abs1-content"]/p/text()'
        abstract = tree.xpath(abstract_path)

        status = 1

    except urllib.error.URLError:
        status = 0
        pass
    except urllib.error.HTTPError:
        status = 0
        pass
    except Exception:
        status = 0
        pass

    return title, tip, date, abstract, abbreviations, funding, keywords, status


def extract_article_data(articles_links, articles_years):
    columns = [
        "title",
        "type",
        "date",
        "abstract",
        "abbreviations",
        "funding",
        "keywords",
        "year",
    ]
    parsed_data = pd.DataFrame(columns=columns)
    unparsed_articles_links = []
    unparsed_articles_year = []

    for article_link, article_year in zip(articles_links, articles_years):
        (
            title,
            tip,
            date,
            abstract,
            abbreviations,
            funding,
            keywords,
            status,
        ) = extract_data(article_link)

        if status == 1:
            parsed_data = parsed_data.append(
                {
                    "title": " ".join(title),
                    "type": " ".join(tip),
                    "date": date,
                    "abstract": " ".join(abstract),
                    "abbreviations": " ".join(abbreviations),
                    "funding": " ".join(funding),
                    "keywords": " ".join(keywords),
                    "year": article_year,
                },
                ignore_index=True,
            )
        else:
            unparsed_articles_links.append(article_link)
            unparsed_articles_year.append(article_year)

    unparsed_articles = pd.DataFrame(
        {
            "article_link": unparsed_articles_links,
            "article_year": unparsed_articles_year,
        }
    )
    parsed_data.to_csv("articles_parsed.csv")

    return parsed_data, unparsed_articles
