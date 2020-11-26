import scraping as sh
import pandas as pd

period_start = 2000
period_end = 2020


def pipeline(start, end):
    articles_list_links, articles_years = sh.get_all_links(write=False, period_start=start, period_end=end)

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

    for article_link, article_year in zip(articles_list_links, articles_years):
        (
            title,
            tip,
            date,
            abstract,
            abbreviations,
            funding,
            keywords,
            status,
        ) = sh.extract_data(article_link)
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

    unparsed = pd.DataFrame(
        {
            "article_link": unparsed_articles_links,
            "article_year": unparsed_articles_year,
        }
    )

    return parsed_data, unparsed


data, _ = pipeline(start=period_start, end=period_end)
