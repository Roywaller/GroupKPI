import jieba
import sqlite3
import re


def remove_stop_words(f):
    d = open("stopwords/cn_stopwords.txt", "r", encoding='utf-8')
    stop_words = {}.fromkeys(d.read().split("\n"))
    for stop_word in stop_words:
        f = f.replace(stop_word, '')
    return f
    d.close()


conn = sqlite3.connect("../KPIEnMicroMsg.db")
cur = conn.cursor()
sql = "SELECT content FROM kpimessage where strftime('%Y', date ) =='2020' and conRemark = '大曾'"
cur.execute(sql)
temp_result = cur.fetchall()
content = ''
for temp in temp_result:
    content = content + str(temp)

new_sentence = re.sub(r'[^\u4e00-\u9fa5]', ' ', content)
f = remove_stop_words(new_sentence)
words = jieba.lcut(f)  # 使用精确模式对文本进行分词
counts = {}  # 通过键值对的形式存储词语及其出现的次数

for word in words:
    if len(word) == 1 or len(word) > 2:  # 单个词语不计算在内
        continue
    else:
        counts[word] = counts.get(word, 0) + 1  # 遍历所有词语，每出现一次其对应的值加 1

items = list(counts.items())  # 将键值对转换成列表
items.sort(key=lambda x: x[1], reverse=True)  # 根据词语出现的次数进行从大到小排序

for i in range(1):
    word, count = items[i]
    mentioned_user = items[i][0]
    count = items[i][1]
    print(mentioned_user, count)
