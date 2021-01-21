import sqlite3
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import jieba
import os
import re
import numpy as np
from PIL import Image


# 去掉停用词
def remove_stop_words(f):
    d = open("stopwords/cn_stopwords.txt", "r", encoding='utf-8')
    stop_words = {}.fromkeys(d.read().split("\n"))
    for stop_word in stop_words:
        f = f.replace(stop_word, '')
    return f
    d.close()


# 生成词云
def create_word_cloud(f):
    jieba.add_word('妈的', tag='u')
    # 设置本地的simhei字体文件位置
    FONT_PATH = os.environ.get("FONT_PATH", os.path.join(os.path.dirname(__file__), "simhei.ttf"))
    f = remove_stop_words(f)
    cut_text = " ".join(jieba.cut(f, cut_all=False, HMM=True))
    # f = remove_stop_words(cut_text)
    image = np.array(Image.open('mask.png'))
    wc = WordCloud(
        background_color="white",
        mask=image,
        font_path=FONT_PATH,
        max_words=200,
        max_font_size=150,
        prefer_horizontal=1,
        scale=4
    )
    wordcloud = wc.generate(cut_text)
    # 写词云图片
    wordcloud.to_file("wordcloud.jpg")
    # 显示词云文件
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.show()


def get_content_from_weixin():
    # 创建数据库连接
    # 这里需要把 找到的weixin.db 放到根目录，具体方法之前文稿讲过
    conn = sqlite3.connect("../KPIEnMicroMsg.db")
    # 获取游标
    cur = conn.cursor()
    # 创建数据表
    # 查询当前数据库中的所有数据表
    sql = "SELECT name FROM sqlite_master WHERE type = 'table' and name like 'kpi%'"
    cur.execute(sql)
    tables = cur.fetchall()
    content = ''
    for table in tables:
        sql = "SELECT content FROM " + table[0] + " where strftime('%Y', date ) =='2020' and conRemark = '萌粗粗'"
        cur.execute(sql)
        temp_result = cur.fetchall()
        for temp in temp_result:
            content = content + str(temp)
    # 提交事务
    conn.commit()
    # 关闭游标
    cur.close()
    # 关闭数据库连接
    conn.close()
    return content


content = get_content_from_weixin()
# 去掉HTML标签里的内容
new_sentence = re.sub(r'[^\u4e00-\u9fa5]', ' ', content)
# 将聊天记录生成词云
create_word_cloud(new_sentence)
