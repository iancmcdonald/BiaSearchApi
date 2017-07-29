import newspaper
from pymongo import MongoClient


def main():
    client = MongoClient()
    client.drop_database('article_database')

    db = client.article_database

    cnn_collection = db.cnn_collection
    fox_collection = db.fox_collection
    msnbc_collection = db.msnbc_collection
    cbs_collection = db.cbs_collection

    # Newspaper.build is memoized. Papers are only used in the build if they have not been built before.
    # To get around this, e.g. in case you want a full database rebuild, you can set the memoize_articles parameter.
    # Example: cnn_paper = newspaper.build("http://www.cnn.com/", memoize_articles=False)
    # Warning, full database rebuilds definitely take awhile, up to 20 minutes in my experience.

    cnn_paper = newspaper.build("http://www.cnn.com/", memoize_articles=False)
    print("CNN paper size: " + str(cnn_paper.size()))
    fox_paper = newspaper.build("http://www.foxnews.com/", memoize_articles=False)
    print("Fox paper size: " + str(fox_paper.size()))
    msnbc_paper = newspaper.build("http://www.msnbc.com/", memoize_articles=False)
    print("MSNBC paper size: " + str(msnbc_paper.size()))
    cbs_paper = newspaper.build("http://www.cbsnews.com/", memoize_articles=False)
    print("CBS paper size: " + str(cbs_paper.size()))

    papers = [cnn_paper, fox_paper, msnbc_paper, cbs_paper]
    newspaper.news_pool.set(papers, threads_per_source=2)
    newspaper.news_pool.join()

    print("DOWNLOADED ARTICLES")

    collection_dict = {cnn_paper: cnn_collection, fox_paper: fox_collection, msnbc_paper: msnbc_collection,
                       cbs_paper: cbs_collection}
    for paper in papers:
        for article in paper.articles:
            try:
                article.parse()

                article_data = {
                    "title": article.title,
                    "brand": paper.brand,
                    "url": article.url,
                    "image": article.top_image,
                    "text": article.text,
                    "nlp_text": None
                }

                if article.title:
                    collection_dict[paper].insert_one(article_data)

            except Exception:
                print("ERROR!")

    print("UPDATED DATABASES")


if __name__ == '__main__':
    main()
