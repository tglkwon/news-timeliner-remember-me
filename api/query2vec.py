import pandas as pd
import re
import pickle
from konlpy.tag import Okt, Kkma, Komoran, Hannanum, Mecab
# import sentencepiece as spm
import gensim
import sqlite3
import sys

if len(sys.argv) < 2:
    print('no argv. this file needs "query: str"')
query = sys.argv[2]

okt = Okt()
kkma = Kkma()
komoran = Komoran()
han = Hannanum()
mecab = Mecab()

if gensim.__version__[0] < '4':
    print('gensim version is old. upgrade gensim ver 4.0 or over.')

path = './'

# crawl to db
path_db = path + 'news.db'
con = sqlite3.connect(path_db)
cur = con.cursor()
cur.execute('SELECT id, title, dateNews, category FROM news;')
articles = cur.fetchall()
articles = pd.DataFrame(articles)
articles.columns = ['id', 'title', 'dateNews', 'category']
articles.dateNews = articles.dateNews.apply(lambda x: str(x)[:6])

path_stopwords = path + 'stopwords.pickle'
with open(path_stopwords, 'rb') as f:
    stopwords = pickle.load(f)


def query2vec(query: str) -> list:
    # 전처리 1
    query = re.sub('[^A-Za-zㄱ-ㅎㅏ-ㅣ가-힣 ]', ' ', query)
    query = re.sub(r'\s{2,}', ' ', query)
    # tokenizer
    query = mecab.morphs(query)
    # 전처리 2
    query = [word for word in query if len(word) > 1 and word not in stopwords]
    
    path_embedding = path + 'doc2vec.model'
    # fasttext = gensim.models.fasttext.FastText.load(path_embedding)
    doc2vec = gensim.models.doc2vec.Doc2Vec.load(path_embedding)
    similars = doc2vec.dv.most_similar(0, topn=25000)
    article_id = [id for id, similarity in similars if similarity > 0.5]
    article_similarity = [similarity for id, similarity in similars if similarity > 0.5]

    articles_res = articles.iloc[article_id]
    articles_res['similarity'] = article_similarity
    return articles_res
    # return articles_res, articles_res.groupby(by=articles_res.dateNews).count()
    
print(query2vec('참사'))