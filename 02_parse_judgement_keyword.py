import json
import os
import sys
import time
from datetime import datetime, timedelta
from os import walk
from pathlib import Path, PurePath

from ckip_transformers import __version__
from ckip_transformers.nlp import (CkipNerChunker, CkipPosTagger,
                                   CkipWordSegmenter)


def get_all_judgement(listpath):
    f = []
    for (dirpath, dirnames, filenames) in walk(listpath):
        f.extend( dirpath + "/" + f for f in filenames)

    return f

##
def word_sep(id, article_content):
    retlist = None
    text = None
    keywords = None
    zipped = None
    zipped2 = None

    try:
        text = [article_content]
        #text.append(article_content)
        ws = ws_driver(text)
        pos = pos_driver(ws)
        #ner = ner_driver(text)

        keywords = set() #避免重複
        zipped = zip(ws, pos)
        for z in zipped:
            zipped2 = zip(z[0], z[1])
            for w, p in zipped2: #字, 詞性
                if len(w) > 1 and p.startswith('N'): #名詞系又長度超過1個
                    keywords.add(w)
        
        retlist = list(keywords)
    except:
        with open('can_not_proc_id', 'a') as failf:
            failf.write(f'{id}\n')


    return retlist

# Show version
print(__version__)

# Initialize CKIP drivers
print("Initializing drivers ... WS")
ws_driver = CkipWordSegmenter(model="albert-base", device=0) #device=0 by using GPU -1 is not
print("Initializing drivers ... POS")
pos_driver = CkipPosTagger(model="albert-base", device=0)
print("Initializing drivers ... NER")
ner_driver = CkipNerChunker(model="albert-base", device=0)
print("Initializing drivers ... all done")
print()

files = get_all_judgement('./hospjudge')
outpath = "judgement_keyword"

if os.path.exists(outpath) : os.remove(outpath)

for i, inputf in enumerate(files):
    #process file      
    filename = Path(inputf).name
    print(f"{i+1}/{len(files)} : {filename}")          

    #非事實審級排除排除高院/最高院- 劉邦揚, 我國地方法院刑事醫療糾紛判決的實證分析：2000年至2010, 科技法學評論8卷2期頁257（2011）
    if filename[2] != 'D':
        continue

    with open(inputf) as f:
        object = json.load(f)
        isbreak = False 

        
        #break condition, 確認檔案內容是否符合斷詞條件
        #沒有主文資料 ["JFULLX"]["JFULLCONTENT"]排除
        if ("JFULLX" not in object):
            isbreak = True      
        else:
            if "JFULLCONTENT" not in object["JFULLX"]:
                isbreak = True
        
        if not isbreak:              
            keywords_Noun = None                
            id = None
            articles = None

            id = object['JID']     
            articles = object['JFULLX']["JFULLCONTENT"]

            #print(articles)
            #replace
            rep_str = ["\r\n", "　", " "]
            for s in rep_str:            
                articles = articles.replace(s, "")
            
            #replace
            rep_str = ["\r\n", "　", " "]
            for s in rep_str:            
                articles = articles.replace(s, "")

            keywords_Noun = word_sep(id, articles)

            if keywords_Noun == None:
                continue

            #輸出->案號 詞
            with open(outpath, 'a', encoding='utf-8') as out:                  
                for k in keywords_Noun:
                    out.write(f'{k}\n')