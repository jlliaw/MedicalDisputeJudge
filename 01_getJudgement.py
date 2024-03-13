# 司法院裁判書系統檢索(https://judgment.judicial.gov.tw/FJUD/default.aspx)
# 取得案號 
# 由案號去司法院openapi取得對應判決

import datetime
import json
import os
from os import walk
from pathlib import Path, PurePath
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup

#get parameter __VIEWSTATE / __VIEWSTATEGENERATOR / __VIEWSTATEENCRYPTED / __EVENTVALIDATION through GET method
#by using url : https://judgment.judicial.gov.tw/FJUD/Default_AD.aspx
root_url = 'https://judgment.judicial.gov.tw'
purl = f"{root_url}/FJUD/Default_AD.aspx"
soup = None

pcookies = None
dic_cookies = {}

aspx_VIEWSTATE = ''
aspx_VIEWSTATEGENERATOR = ''
aspx_VIEWSTATEENCRYPTED = ''
aspx_EVENTVALIDATION = ''

with requests.get(purl) as r:
    if r.status_code == 200:        
        pcookies = r.cookies #cookies

        for ck in r.cookies: #cookies kvp
            dic_cookies[ck.name] = ck.value
        
        soup = BeautifulSoup(r.text, 'html.parser')            
        aspx_VIEWSTATE = '' if soup.select_one("#__VIEWSTATE") == None else soup.select_one("#__VIEWSTATE")["value"]
        aspx_VIEWSTATEGENERATOR = '' if soup.select_one("#__VIEWSTATEGENERATOR") == None else soup.select_one("#__VIEWSTATEGENERATOR")["value"]
        aspx_VIEWSTATEENCRYPTED = '' if soup.select_one("#__VIEWSTATEENCRYPTED") == None else soup.select_one("#__VIEWSTATEENCRYPTED")["value"]
        aspx_EVENTVALIDATION = '' if soup.select_one("#__EVENTVALIDATION") == None else soup.select_one("#__EVENTVALIDATION")["value"]


#get data by using POST method

payload = {}

''''''
payload["__VIEWSTATE"] = aspx_VIEWSTATE
payload["__VIEWSTATEGENERATOR"] = aspx_VIEWSTATEGENERATOR
payload["__VIEWSTATEENCRYPTED"] = aspx_VIEWSTATEENCRYPTED
payload["__EVENTVALIDATION"] = aspx_EVENTVALIDATION

payload["dy1"] = "109"
payload["dm1"] = "09"
payload["dd1"] = "30"

payload["dy2"] = "112"
payload["dm2"] = "10"
payload["dd2"] = "01"

payload["jud_kw"] = "醫療過失-附民-交簡-交訴-交易-勞安"
payload["judtype"] = "JUDBOOK"
payload["whosub"] = "1"
payload["ctl00$cp_content$btnQry"] = "送出查詢"


with requests.post(purl, data = payload) as r:
    if  r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")


hidQID_value = soup.find(attrs = {"id": "hidQID"}).attrs["value"] #hidQID value for qryresultlst.aspx

#get page links
purl = f"{root_url}/FJUD/qryresultlst.aspx?q={hidQID_value}"

with requests.get(purl) as r:
    if  r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")

#api auth
api_auth={}
api_auth["user"] = "your_user_name"
api_auth["password"] = "your_password"
res = requests.post(url="https://data.judicial.gov.tw/jdg/api/Auth", data=api_auth)
jobject = json.loads(res.text)
token = jobject["Token"]

#option tag的內容->取得分頁
page_options = soup.find(attrs = {"id": "ddlPage"}).find_all('option')
for o in page_options:
    #處理每一分頁
    #o['value'] / o.text
    purl = f"{root_url}{o['value']}"

    with requests.get(purl) as r:
        if  r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
   
    for p in soup.find_all(attrs = {'id':'hlTitle'}):
        caseno = p['onclick']        
        rep_str = ["cookieId", "(", ")", "'"]
        for s in rep_str:            
            caseno = caseno.replace(s, "")

        caseno_decode = unquote(caseno.split(',')[0])
        print(caseno_decode + " : " + p.text)        

        #使用案號從open api取得資料並存成json file
        jid = caseno_decode
        payload = {
            "token":token,
            "j":jid
        }
        res = requests.post(url="https://data.judicial.gov.tw/jdg/api/JDoc", data=payload)
        judgecontent = json.loads(res.text)

        with open(f"./hospjudge/{jid}.json", 'w', encoding='utf-8') as f:
            json.dump(judgecontent, f, ensure_ascii=False, indent=4)
