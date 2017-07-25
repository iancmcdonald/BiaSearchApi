import sys
import spacy
from goose import Goose
from pymongo import MongoClient

# user_article_url = "http://www.cnn.com/2017/07/09/politics/trump-russia-meeting-campaign/index.html"
# user_article_url = "http://www.foxnews.com/politics/2017/07/09/congress-returns-to-obamacare-and-other-key-issues-with-fast-approaching-deadlines.html"
# user_article_url = "http://www.foxnews.com/politics/2017/07/09/trump-appears-to-back-off-joint-cyber-security-unit-with-russia-after-criticism.html"

user_article_url = sys.argv[1]

nlp = spacy.load("en")

g = Goose()
user_article = g.extract(url=user_article_url)
user_article_text = user_article.cleaned_text

print "============== GOOSE ============="
source_text = nlp(user_article_text)


client = MongoClient()
db = client.article_database

collections = [db.fox_collection, db.cbs_collection, db.msnbc_collection, db.cnn_collection]

def get_match(collection):
    match_sim = 0.0
    match_article = None
    for article in collection.find():
        curr_text = article["text"]
        nlp_text = nlp(curr_text)
        curr_sim = source_text.similarity(nlp_text)
        if curr_sim > match_sim:
            match_sim = curr_sim
            match_article = article
    return match_article

for c in collections:
 match = get_match(c)
 print "==================== BEGIN MATCH COLLECTION ========================="
 print "\n"
 print match["url"]
 print match["image"]
 print "\n"
 print "==================== END MATCH COLLECTION ========================="
 print "\n"
