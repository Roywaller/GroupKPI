# coding: utf-8
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_paginate import Pagination, get_page_parameter
from flask_cors import CORS
import datetime
import pandas as pd
from info_api import module_api  # 附加模块
import sqlite3
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import jieba
import os
import re
import numpy as np
from PIL import Image

app = Flask(__name__)
app.debug = True
app.config["JSON_AS_ASCII"] = False
bootstrap = Bootstrap(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# 指定时区
BJT = datetime.timezone(datetime.timedelta(hours=+8), 'BJT')

# 从其他模块(.py)调用
app.register_blueprint(module_api)


@app.route('/')
def index():
    year = request.args.get('year')
    conn = sqlite3.connect('../KPIEnMicroMsg.db')
    cur = conn.cursor()

    now = datetime.datetime.now(BJT)
    ranking_timestamp = now - datetime.timedelta(days=365)
    max_year = ranking_timestamp.strftime("%Y")

    if year is None:
        year = max_year

    stop_year = (datetime.datetime.strptime(year, "%Y")).strftime("%Y")
    sql = "SELECT imgflag, conRemark, count( * ) AS counts,dense_RANK( ) OVER ( ORDER BY count( * ) DESC ) AS ranking " \
          " FROM kpimessage WHERE strftime('%%Y',date) == '%s' GROUP BY conRemark ORDER BY counts DESC" % (
                  '%s' % year)
    cursor = cur.execute(sql)

    exercise_data_list = cursor.fetchall()

    page = request.args.get(get_page_parameter(), type=int, default=1)
    res = exercise_data_list[(page - 1) * 100: page * 100]
    pagination = Pagination(page=page, total=len(exercise_data_list), per_page=100, css_framework='bootstrap4')

    return render_template('index.html', results=res, start_year=year,
                           stop_year=stop_year, max_year=max_year, pagination=pagination)


@app.route('/hapi')
def hapi():
    year = request.args.get('year')
    conn = sqlite3.connect('../KPIEnMicroMsg.db')
    cur = conn.cursor()

    now = datetime.datetime.now(BJT)
    ranking_timestamp = now - datetime.timedelta(days=365)
    max_year = ranking_timestamp.strftime("%Y")

    if year is None:
        year = max_year

    stop_year = (datetime.datetime.strptime(year, "%Y")).strftime("%Y")
    sql = "SELECT imgflag, conRemark, count( * ) AS counts, dense_RANK( ) OVER ( ORDER BY count( * ) DESC ) AS " \
          "ranking FROM kpimessage WHERE strftime('%%Y',date)== '%s' AND content LIKE '%s' GROUP BY conRemark ORDER " \
          "BY counts DESC" % (
              '%s' % year, '%哈哈哈%')
    cursor = cur.execute(sql)

    exercise_data_list = cursor.fetchall()

    page = request.args.get(get_page_parameter(), type=int, default=1)
    res = exercise_data_list[(page - 1) * 100: page * 100]
    pagination = Pagination(page=page, total=len(exercise_data_list), per_page=100, css_framework='bootstrap4')

    return render_template('hapi.html', results=res, start_year=year,
                           stop_year=stop_year, max_year=max_year, pagination=pagination)


@app.route('/userdata')
def userdata():
    user = request.args.get('user')
    type = request.args.get('type')

    # # 词云开始
    # def remove_stop_words(f):
    #     d = open("stopwords/cn_stopwords.txt", "r", encoding='utf-8')
    #     stop_words = {}.fromkeys(d.read().split("\n"))
    #     for stop_word in stop_words:
    #         f = f.replace(stop_word, '')
    #     return f
    #     d.close()
    #
    # # 生成词云
    # def create_word_cloud(f):
    #     # 设置本地的simhei字体文件位置
    #     FONT_PATH = os.environ.get("FONT_PATH", os.path.join(os.path.dirname(__file__), "simhei.ttf"))
    #     f = remove_stop_words(f)
    #     cut_text = " ".join(jieba.cut(f, cut_all=False, HMM=True))
    #     image = np.array(Image.open('mask.png'))
    #     wc = WordCloud(
    #         background_color="white",
    #         mask=image,
    #         font_path=FONT_PATH,
    #         max_words=200,
    #         max_font_size=150,
    #         prefer_horizontal=1,
    #         scale=4
    #     )
    #     wordcloud = wc.generate(cut_text)
    #     # 写词云图片
    #     wordcloud.to_file("static/wordcloud/" + user + ".jpg")
    #     # 显示词云文件
    #     plt.imshow(wordcloud)
    #     plt.axis("off")
    #
    # def get_content_from_weixin():
    #     # 创建数据库连接
    #     # 这里需要把 找到的weixin.db 放到根目录，具体方法之前文稿讲过
    #     conn = sqlite3.connect("../KPIEnMicroMsg.db")
    #     # 获取游标
    #     cur = conn.cursor()
    #     # 创建数据表
    #     # 查询当前数据库中的所有数据表
    #     sql = "SELECT name FROM sqlite_master WHERE type = 'table' and name like 'kpi%'"
    #     cur.execute(sql)
    #     tables = cur.fetchall()
    #     content = ''
    #     for table in tables:
    #         sql = "SELECT content FROM " + table[
    #             0] + " where strftime('%Y', date ) =='2020' and conRemark = '" + user + "' "
    #         cur.execute(sql)
    #         temp_result = cur.fetchall()
    #         for temp in temp_result:
    #             content = content + str(temp)
    #     # 提交事务
    #     conn.commit()
    #     # 关闭游标
    #     cur.close()
    #     # 关闭数据库连接
    #     conn.close()
    #     return content
    #
    # content = get_content_from_weixin()
    # # 去掉HTML标签里的内容
    # new_sentence = re.sub(r'[^\u4e00-\u9fa5]', ' ', content)
    # # 将聊天记录生成词云
    # create_word_cloud(new_sentence)
    # # 词云结束
    conn = sqlite3.connect('../KPIEnMicroMsg.db')
    cur = conn.cursor()
    now = datetime.datetime.now(BJT)
    ranking_timestamp = now - datetime.timedelta(days=365)
    max_year = ranking_timestamp.strftime("%Y")
    year = request.args.get('year')

    if user is None:
        year = max_year

    stop_year = (datetime.datetime.strptime(year, "%Y")).strftime("%Y")
    if user is None: user = ""

    if type == "hapi":
        title = '哈哈哈'
        sql = "SELECT strftime( '%%Y-%%m-%%d', date ) AS day, count( date ) AS count, imgflag FROM kpimessage WHERE conRemark = " \
              "'%s' AND strftime('%%Y',date)== '%s' AND content LIKE '%s' GROUP BY day" % ('%s' % user, year, '%哈哈哈%')
    elif type == "buca":
        title = '划水'
        sql = "SELECT strftime('%%Y-%%m-%%d', date ) AS day, count( date ) AS count, imgflag FROM kpimessage WHERE conRemark " \
              "='%s' AND strftime('%%Y', date ) =='%s' GROUP BY day" % ('%s' % user, year)

    cursor = cur.execute(sql)
    exercise_data_list = cursor.fetchall()
    res1 = pd.DataFrame(list(exercise_data_list), columns=['day', 'count', 'imgflag'])
    chartcal = str(res1['day'].values.tolist())
    chartcre = res1['count'].values.tolist()
    img = res1['imgflag'].values[1]
    result = ''

    page = request.args.get(get_page_parameter(), type=int, default=1)
    res = exercise_data_list[(page - 1) * 100: page * 100]
    pagination = Pagination(page=page, total=len(exercise_data_list), per_page=100, css_framework='bootstrap4')

    return render_template('userdata.html', stop_year=stop_year, results=res, pagination=pagination, user=user,
                           chartcal=chartcal,
                           chartcre=chartcre, img=img, title=title)


@app.route('/user')
def user():
    year = request.args.get('year')
    conn = sqlite3.connect('../KPIEnMicroMsg.db')
    cur = conn.cursor()

    now = datetime.datetime.now(BJT)
    ranking_timestamp = now - datetime.timedelta(days=365)
    max_year = ranking_timestamp.strftime("%Y")

    if year is None:
        year = max_year

    stop_year = (datetime.datetime.strptime(year, "%Y")).strftime("%Y")
    sql = "select imgflag,conRemark from kpimessage where strftime('%%Y',date)== '%s' GROUP BY conRemark ORDER BY conRemark desc" % (
            '%s' % year)
    cursor = cur.execute(sql)

    exercise_data_list = cursor.fetchall()

    page = request.args.get(get_page_parameter(), type=int, default=1)
    res = exercise_data_list[(page - 1) * 100: page * 100]
    pagination = Pagination(page=page, total=len(exercise_data_list), per_page=100, css_framework='bootstrap4')

    return render_template('user.html', results=res, start_year=year,
                           stop_year=stop_year, max_year=max_year, pagination=pagination)


@app.route('/personal')
def personal():
    user = request.args.get('user')
    year = request.args.get('year')
    conn = sqlite3.connect('../KPIEnMicroMsg.db')
    cur = conn.cursor()

    now = datetime.datetime.now(BJT)
    ranking_timestamp = now - datetime.timedelta(days=365)
    max_year = ranking_timestamp.strftime("%Y")

    if year is None:
        year = max_year

    stop_year = (datetime.datetime.strptime(year, "%Y")).strftime("%Y")
    sql = "SELECT count (content) as postimes, SUM(LENGTH( content ) - 1) as textcount FROM kpimessage WHERE " \
          "conRemark == '%s' and  strftime( '%%Y', date ) == '%s' AND LENGTH( content ) < 100 " % ('%s' % user, year)
    cursor = cur.execute(sql)
    bucacount = cursor.fetchall()
    res1 = pd.DataFrame(list(bucacount), columns=['postimes', 'textcount'])
    postimes = str(res1['postimes'].values[0])
    textcount = str(res1['textcount'].values[0])
    sql = "SELECT strftime( '%%H', date ) AS huatime, count( date ) AS count FROM kpimessage WHERE conRemark = '%s' " \
          "AND strftime( '%%Y', date ) == '%s' GROUP BY huatime ORDER BY count DESC LIMIT 1 " % ('%s' % user, year)
    cursor = cur.execute(sql)
    huatime = cursor.fetchall()
    res1 = pd.DataFrame(list(huatime), columns=['huatime', 'count'])
    huatime = str(res1['huatime'].values[0])
    huacount = str(res1['count'].values[0])

    def remove_stop_words(f):
        d = open("stopwords/cn_stopwords.txt", "r", encoding='utf-8')
        stop_words = {}.fromkeys(d.read().split("\n"))
        for stop_word in stop_words:
            f = f.replace(stop_word, '')
        return f
        d.close()

    sql = "SELECT content FROM kpimessage where conRemark = '%s' and strftime('%%Y', date ) =='%s'" % (
        '%s' % user, year)
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
    for i in items:
        sql = "select content from kpimessage where conRemark = '%s' and strftime('%%Y', date ) =='%s' and content like '%%%s%%' AND LENGTH( content ) < 20 limit 4" % (
            '%s' % user, year, i[0])  # 获取关键词会出现空的情况所以出错
        cur.execute(sql)
        mentionedr = cur.fetchall()
        mentioned = i
        if len(mentionedr) == 0:
            i[+1]
            continue
        else:
            sql = "select content from kpimessage where conRemark = '%s' and strftime('%%Y', date ) =='%s' and content like '%%%s%%' AND LENGTH( content ) < 40 limit 4" % (
                '%s' % user, year, i[0])  # 获取关键词会出现空的情况所以出错
            cur.execute(sql)
            mentionedr = cur.fetchall()
            while len(mentionedr) < 4:
                mentionedr.append(' ')
            break


    sql = "WITH day AS ( SELECT strftime( '%%Y-%%m-%%d', date ) AS day FROM kpimessage WHERE conRemark = '%s' AND strftime( '%%Y', date ) == '%s' GROUP BY day ) SELECT count( * ) FROM day" % (
        '%s' % user, year)
    cur.execute(sql)
    Ndays = cur.fetchall()
    Ndays = pd.DataFrame(list(Ndays), columns=['Ndays'])
    Ndays = str(Ndays['Ndays'].values[0])

    sql = "SELECT strftime( '%%m月%%d日', date ) AS haday, count( date ) AS count FROM kpimessage WHERE conRemark = '%s' AND strftime( '%%Y', date ) == '%s' AND content LIKE '%%%s%%' GROUP BY haday ORDER BY count desc LIMIT 1" % (
        '%s' % user, year, '哈哈哈')
    cur.execute(sql)
    special_day = cur.fetchall()
    special_day = pd.DataFrame(list(special_day), columns=['haday', 'count'])
    special_date = str(special_day['haday'].values[0])

    sql = "SELECT strftime( '%%H点%%M分', date ) AS haday, content FROM kpimessage WHERE conRemark = '%s' AND strftime( '%%Y年%%m月%%d日', date ) == '%s年%s' AND content LIKE '%%%s%%' order by haday desc LIMIT 1" % (
        '%s' % user, stop_year, special_date, '哈哈哈')
    cur.execute(sql)
    latestend = cur.fetchall()
    latestend = pd.DataFrame(list(latestend), columns=['time', 'content'])

    sql = "WITH user AS( SELECT conRemark FROM kpimessage WHERE strftime( '%%Y', date ) =='%s' and conRemark != '%s' GROUP BY conRemark ) select count(*) as count from user" % (
        '%s' % stop_year, user)
    cur.execute(sql)
    partner = cur.fetchall()

    sqll = "SELECT conRemark FROM kpimessage WHERE strftime( '%%Y', date ) =='%s' and conRemark != '%s' GROUP BY conRemark" % (
        '%s' % stop_year, user)
    cur.execute(sqll)
    partnername = cur.fetchall()
    partnername = pd.DataFrame(list(partnername), columns=['name'])
    partnername = partnername['name'].values.tolist()
    content = ''
    for i in partnername:
        content = content + '<span style="white-space:nowrap;">' + str(i) + '</span> '

    conn.commit()
    # 关闭游标
    cur.close()
    # 关闭数据库连接
    conn.close()

    return render_template('personal.html', start_year=year, stop_year=stop_year, max_year=max_year, user=user,
                           postimes=postimes, textcount=textcount, huatime=huatime, huacount=huacount,
                           mentioned=mentioned, mentionedr=mentionedr, Ndays=Ndays, special_day=special_day,
                           latestend=latestend, partner=partner[0], partnername=content)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('not_found.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('internal_server_error.html'), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=11111)
