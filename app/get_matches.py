import sys
from itertools import tee, zip_longest
import spacy
import newspaper
from pymongo import MongoClient

# user_article_url = "http://www.cnn.com/2017/07/09/politics/trump-russia-meeting-campaign/index.html"
# user_article_url = "http://www.foxnews.com/politics/2017/07/09/congress-returns-to-obamacare-and-other-key-issues-with-fast-approaching-deadlines.html"
# user_article_url = "http://www.foxnews.com/politics/2017/07/09/trump-appears-to-back-off-joint-cyber-security-unit-with-russia-after-criticism.html"

user_article_url = sys.argv[1]

nlp = spacy.load("en")

art = newspaper.Article(user_article_url)
art.download()
art.parse()
user_article_text = art.text

in_text = nlp(user_article_text)

client = MongoClient()
db = client.article_database

collections = [db.fox_collection, db.cbs_collection, db.msnbc_collection, db.cnn_collection]


def get_match(collection):
    static_stream, dynamic_stream = tee(collection.find())

    similarity_stream = zip(static_stream,
                                    (in_text.similarity(processed_doc) for processed_doc in
                                     nlp.pipe((article["text"] for article in dynamic_stream),
                                              batch_size=50, n_threads=4)))

    return max(similarity_stream, key=lambda x: x[1])[0]


for c in collections:
    match = get_match(c)
    print(match["url"])
    print(match["image"])
