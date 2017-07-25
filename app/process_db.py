from itertools import tee, zip_longest
import pickle
import spacy
from bson.binary import Binary
from pymongo import MongoClient

nlp = spacy.load("en")

"""
TODO: Only update collections with new articles, rather than re-processing the articles which already
have an "nlp_text" property. The current reason this is not done is that spaCy has a serialization bug
related to concurrency issues in nlp.pipe(). So with each database processing, some small number of articles
may be serialized incorrectly. Reprocessing the database with each update improves robustness in the sense
that the same article will probably not be serialized incorrectly twice. The next version of spaCy promises
to fix this issue, so it should be a temporary problem.
"""


def get_sim_stream(collection):
    static_stream, dynamic_stream = tee(collection.find())

    similarity_stream = zip(static_stream,
                            (nlp.pipe((article["text"] for article in dynamic_stream),
                                      batch_size=50, n_threads=4)))
    return similarity_stream


def main():
    client = MongoClient()
    db = client.article_database

    collections = [db.fox_collection, db.cbs_collection, db.msnbc_collection, db.cnn_collection]

    for c in collections:
        for entry, processed_text in get_sim_stream(c):
            c.update_one({"_id": entry["_id"]},
                         {"$set": {"nlp_text": Binary(pickle.dumps(processed_text.to_bytes()))}}, upsert=False)


if __name__ == '__main__':
    main()
