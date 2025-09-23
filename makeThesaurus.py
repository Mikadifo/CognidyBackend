import nltk
from dotenv import load_dotenv
import os

nltk.download('wordnet')

from nltk.corpus import wordnet as wn

#creation of theasaurus database
def make_thesaurus(wn):
      thesaurus = {}
      for synset in wn.all_synsets():
         for lemma in synset.lemmas():
               word = lemma.name().lower()
               synonyms = set()
               for syn in wn.synsets(word):
                  for l in syn.lemmas():
                     synonyms.add(l.name().lower())
               if word in thesaurus:
                  thesaurus[word].update(synonyms)
               else:
                  thesaurus[word] = synonyms
      # Convert sets to lists for easier storage in MongoDB
      for word in thesaurus:
         thesaurus[word] = list(thesaurus[word])
      return thesaurus