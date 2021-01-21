# coding: utf-8
from flask import Blueprint, request, jsonify
import sqlite3
import datetime
from dateutil.relativedelta import relativedelta

module_api = Blueprint('info_api', __name__)
# 指定时区
BJT = datetime.timezone(datetime.timedelta(hours=+8), 'BJT')


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@module_api.route('/api')
def api_index():
    day = request.args.get('day')
    conn = sqlite3.connect('../RingFitRank.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    now = datetime.datetime.now(BJT)
    ranking_timestamp = now - datetime.timedelta(hours=4)
    max_day = ranking_timestamp.strftime("%Y-%m-%d")

    if day is None:
        day = max_day

    stop_day = (datetime.datetime.strptime(day, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    params = (day,)

    cur.execute("SELECT id,dense_RANK() OVER(ORDER BY kcal DESC) AS ranking,weiboname,kcal,created_at "
                "FROM (SELECT *, dense_RANK() OVER(PARTITION BY weiboname ORDER BY kcal DESC, id) AS rnk FROM RingFit WHERE   date(datetime(created_at,'-4 hours'))==?) tmp "
                "WHERE rnk = 1 ORDER BY kcal DESC, created_at ASC;", params)

    exercise_data_list = cur.fetchall()

    return jsonify({
        'start_day': day,
        'stop_day': stop_day,
        'exercise_data_list': exercise_data_list
    }), 200


@module_api.route('/api/monthly')
def api_monthly():
    month = request.args.get('month')
    conn = sqlite3.connect('../RingFitRank.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    now = datetime.datetime.now(BJT)
    ranking_timestamp = now - datetime.timedelta(hours=4)
    start_day = ranking_timestamp.strftime("%Y-%m") + "-01"

    if month is not None:
        start_day = month + "-01"

    stop_day = (datetime.datetime.strptime(start_day, "%Y-%m-%d") + relativedelta(months=1) - datetime.timedelta(
        days=1)).strftime("%Y-%m-%d")
    params = (start_day,)

    print(params)

    cur.execute(
        "SELECT id,dense_RANK() OVER(ORDER BY SUM(kcal) DESC) AS ranking,weiboname,SUM(kcal) AS monthly_kcal,COUNT(weiboname) AS days "
        "FROM (SELECT *, dense_RANK() OVER(PARTITION BY [weiboname],[tweeted_date] ORDER BY kcal DESC, id) AS rnk "
        "FROM (SELECT *, strftime('%Y-%m-%d',datetime(created_at,'-4 hours')) AS tweeted_date FROM RingFit) WHERE strftime('%Y-%m',datetime(created_at,'-4 hours')) == strftime('%Y-%m',?)) tmp "
        "WHERE rnk = 1 GROUP BY weiboname ORDER BY monthly_kcal DESC, created_at ASC ;", params)

    exercise_data_list = cur.fetchall()

    return jsonify({
        'start_day': start_day,
        'stop_day': stop_day,
        'exercise_data_list': exercise_data_list
    }), 200


@module_api.route('/api/user')
def api_user():
    user = request.args.get('user')
    conn = sqlite3.connect('../RingFitRank.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    if user is None: user = ""
    params = (user,)

    cur.execute(
        "WITH NonOverlapTable AS (SELECT *, dense_RANK() OVER(PARTITION BY weiboname, date(datetime(created_at,'-4 hours')) ORDER BY kcal DESC, id) AS rnk FROM RingFit)"
        ",DailyRankedTable AS (SELECT *,dense_RANK() OVER(PARTITION BY date(datetime(created_at,'-4 hours')) ORDER BY kcal DESC) AS daily_rank FROM NonOverlapTable WHERE rnk = 1)"
        "SELECT id,daily_rank,kcal,created_at, strftime('%w', datetime(created_at,'-4 hours')) AS weeknumber FROM DailyRankedTable WHERE rnk = 1 AND weiboname==? ORDER BY created_at DESC;",
        params)

    exercise_data_list = cur.fetchall()

    return jsonify({
        'user_exercise_data_list': exercise_data_list
    }), 200
