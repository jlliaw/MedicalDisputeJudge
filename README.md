## 以醫療糾紛判決為例進行示範

### 0. 環境
* python 3.8
```
pip install -r requirements.txt
```

### 1. 如何從司法院的裁判書系統以程式化方式得相關案號
01_getJudgement.py 使用「醫療過失」為關鍵字，把「附民,交簡,交訴,交易,勞安」相關案例排除，主要是參考 https://ir.nctu.edu.tw/bitstream/11536/107626/1/8_2_6.pdf 以及 http://www.tsim.org.tw/article/A103/abstract/402/11%E6%9C%8823%E6%97%A5%E4%B8%8B%E5%8D%88/%E5%90%B3%E4%BF%8A%E7%A9%8E.pdf 兩篇論文的方式，並且僅找109年10月到112年9月間的判決。

### 2. 取得案號後由司法院open api取得判決主文
01_getJudgement.py 包含部分api邏輯, api 取得主文後把檔案在名為hospjudge的資料夾。關於api的使用主要還是參照司法院的open api使用手冊，比較納悶的是, 不知道為什麼只開放夜間12點到早上6點共6小時可以使用這個API，要使用的人注意這個限制!! </br>
* 司法院open api : https://opendata.judicial.gov.tw/ </br>
* 操作手冊: https://opendata.judicial.gov.tw/api/Newses/38/file

### 3. 主文使用CKIP進行斷詞
02_parse_judgement_keyword.py 則是將前步驟找到的判決主文中拉出一審判決進行斷詞，只找一審也是參考前面兩篇論文。值得一提的是CKIP因為是用transformer模型，有GPU的環境是比較有效率的。這個程式執行後會產生judgement_keyword檔案。以步驟1.的篩選條件，可以找到約470篇判決書，只取一審大概會有270篇左右，經過斷詞後約在12萬個詞(CKIP限定名詞情況下)。

### 4. 建立文字雲
使用 https://wordcloud.timdream.org/ 這個網站, 把judgement_keyword所有詞都複製貼進去，就能產生如下圖的文字雲!!
![image info](./pictures/wordcloud.png)


