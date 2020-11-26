from pyquery import PyQuery
import urllib
import lxml.html as html
import csv
import numpy as np


def get_journal_links(journal_code, year, volume_start, volume_end, max_issues):
    links, years = [], []

    for volume in range(volume_start, volume_end + 1):
        for issue in range(1, max_issues + 1):
            link = "https://link.springer.com/journal/" + str(journal_code) + "/volumes-and-issues/" + str(volume) + "-" + str(issue)
            links.append(link)
            years.append(year)

            # links.append(link + "/page/2")
            # years.append(year)
            #
            # links.append(link + "/page/3")
            # years.append(year)

        year = year + 1

    return links, years


def get_article_links(journal_link):
    data = urllib.request.urlopen(journal_link).read()
    pq = PyQuery(data)
    articles = pq('h3.c-card__title>a').map(lambda _, x: x.attrib['href'])
    return articles


def get_all_links(period_start, period_end, addresses, years):
    period = np.arange(period_start, period_end)
    articles_list_links, articles_years = [], []

    for link, year in zip(addresses, years):
        if year in period:
            try:
                articles_links = get_article_links(link)
                for a_l in articles_links:
                    article_link = a_l
                    articles_list_links.append(article_link)
                    articles_years.append(year)
            except:
                continue


    return articles_list_links, articles_years


def extract_data(article_link):

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

        title_xpath = '//*[@id="main-content"]/main/article/div[1]/header/h1/text()'

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

