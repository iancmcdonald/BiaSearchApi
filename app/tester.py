import spacy
from spacy.tokens.doc import Doc
import pickle
from bson.binary import Binary

nlp = spacy.load("en")

d = nlp(u"the cow jumps over the moon")

bin_d = Binary(pickle.dumps(d.to_bytes()))
from_bin = Doc(nlp.vocab).from_bytes(pickle.loads(bin_d))

# from_bin = Doc(nlp.vocab).from_bytes(pickle.loads(bin_d.decode(encoding="utf-8")))

print from_bin
