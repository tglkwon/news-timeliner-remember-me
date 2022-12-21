import pandas as pd
import re
import sqlite3
import pickle
from tqdm import tdqm
from konlpy.tag import Mecab

mecab = Mecab()

with open('stopwords.pickle', 'rb') as fi:
    stopwords = pickle.load(fi)

# crawl to db
con = sqlite3.connect('news_Crawl.db')
cur = con.cursor()

cur.execute('''
    SELECT id, title, content, category, dateNews FROM news WHERE content != '';
''')
articles = cur.fetchall()

articles = pd.DataFrame(articles)

articles[4] = articles[4].apply(lambda x: str(x)[:6])
articles[5] = articles[2].apply(lambda x: re.sub('[^0-9A-Za-zㄱ-ㅎㅏ-ㅣ가-힣 ]', ' ', x))
articles[5] = articles[5].apply(lambda x: re.sub(r'\s{2,}', ' ', x))

# 형태소 분석기
articles[5] = articles[5].apply(lambda x: mecab.morphs(x))
articles[5] = articles[5].apply(lambda x: x if len(x) > 1 else '')
articles[5] = articles[5].apply(lambda x: x if x not in stopwords else '')
articles[5] = articles[5].apply(lambda x: ' '.join(x))


# corpus save
for article in tqdm(articles):
    date = article[4]
    doc = article[5]
    cur.execute('''
        INSERT INTO news WHERE
        (corpus, dateNews)
        VALUES (:corpus, :dateNews);
    ''', (doc, date))

con.commit()

cur.execute('SELECT id, corpus, dateNews')
print(cur.fetchone())