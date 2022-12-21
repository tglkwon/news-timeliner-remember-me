import sqlite3
from gensim.models import Word2vec

# crawl to db
con = sqlite3.connect('news_Crawl.db')
cur = con.cursor()

cur.execute('''
    SELECT id, title, corpus, category, dateNews FROM news WHERE content != '';
''')
articles = cur.fetchall()
corpus = articles[2]

model = Word2Vec(sentences = corpus, size = 100, window = 5, min_count = 5, workers = 4, sg = 1)

model.save('word2vec.model')
# model = Word2vec.load('word2vec.model')