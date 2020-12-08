import os
from datetime import datetime
import sys
from typing import Optional

if sys.platform == 'win32':
    os.system('cls')

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import sqlalchemy

from declaration import Topic, Strategy, topics, strategies, News, news
from helpers import Counter, interpolation
from routers import background, predict
from database import database


app = FastAPI()
app.mount('/js', StaticFiles(directory='dist/js'), name='js')
app.mount('/css', StaticFiles(directory='dist/css'), name='css')
with open('dist/index.html', 'r', encoding='utf-8') as f:
    index_html = f.read()


@app.get('/')
async def main():
    return HTMLResponse(index_html, status_code=200)


@app.get('/admin/topic')
async def redirect():
    return HTMLResponse(index_html, status_code=200)


@app.get('/admin/strategy')
async def redirect():
    return HTMLResponse(index_html, status_code=200)


@app.get('/event')
async def redirect():
    return HTMLResponse(index_html, status_code=200)


@app.on_event('startup')
async def startup():
    print('startup')
    await database.connect()


@app.on_event('shutdown')
async def shutdown():
    print('shutdown')
    await database.disconnect()


@app.get('/api/topics/')
async def get_topic_list(skip: int = 0, limit: int = 10, issue_id: Optional[int] = None):
    if issue_id is None:
        query = topics.select().limit(limit).offset(skip)
        topic_list = await database.fetch_all(query)
        total = await database.fetch_all(sqlalchemy.select([sqlalchemy.func.count()]).select_from(topics))
        return {'data': topic_list, 'total': total[0][0]}
    else:
        issues_list = await database.fetch_all('select distinct(issue) from topic')
        issue = issues_list[issue_id - 1][0]
        query = topics.select().limit(limit).offset(skip).where(whereclause=sqlalchemy.text(f'issue="{issue}"'))
        topic_list = await database.fetch_all(query)
        total = await database.fetch_all(sqlalchemy.select([sqlalchemy.func.count()]).select_from(topics).where(whereclause=sqlalchemy.text(f'issue="{issue}"')))
        return {'data': topic_list, 'total': total[0][0]}


@app.post('/api/topics/')
async def add_topic_list(topic: Topic):
    try:
        query = topics.insert().values(**topic.dict())
        last_record_id = await database.execute(query)
        return {'code': 0, 'data': {'last_record_id': last_record_id, 'message': '新增成功'}}
    except Exception as e:
        return {'code': -1, 'data': {'message': '新增失败：' + str(e)}}


@app.put('/api/topics/{topic_id}')
async def update_topic_list(topic_id: str, topic: Topic):
    try:
        query = topics.update(whereclause=sqlalchemy.text(f'id="{topic_id}"')).values(**topic.dict())
        record_id = await database.execute(query)
        return {'code': 0, 'data': {'record_id': record_id, 'message': '更新成功'}}
    except Exception as e:
        return {'code': -1, 'data': {'message': '更新失败：' + str(e)}}


@app.delete('/api/topics/{topic_id}')
async def delete_topic_list(topic_id: str):
    try:
        query = topics.delete(whereclause=sqlalchemy.text(f'id="{topic_id}"'))
        record_id = await database.execute(query)
        return {'code': 0, 'data': {'record_id': record_id, 'message': '删除成功'}}
    except Exception as e:
        return {'code': -1, 'data': {'message': '删除失败：' + str(e)}}


@app.get('/api/strategies/')
async def get_strategy_list(skip: int = 0, limit: int = 10):
    query = strategies.select().limit(limit).offset(skip)
    strategy_list = await database.fetch_all(query)
    total = await database.fetch_all(sqlalchemy.select([sqlalchemy.func.count()]).select_from(strategies))
    return {'data': strategy_list, 'total': total[0][0]}


@app.post('/api/strategies/')
async def add_strategy_list(strategy: Strategy):
    try:
        query = strategies.insert().values(**strategy.dict())
        last_record_id = await database.execute(query)
        return {'code': 0, 'data': {'last_record_id': last_record_id, 'message': '新增成功'}}
    except Exception as e:
        return {'code': -1, 'data': {'message': '新增失败：' + str(e)}}


@app.put('/api/strategies/{strategy_id}')
async def update_strategy_list(strategy_id: str, strategy: Strategy):
    try:
        query = strategies.update(whereclause=sqlalchemy.text(f'id="{strategy_id}"')).values(**strategy.dict())
        record_id = await database.execute(query)
        return {'code': 0, 'data': {'record_id': record_id, 'message': '更新成功'}}
    except Exception as e:
        return {'code': -1, 'data': {'message': '更新失败：' + str(e)}}


@app.delete('/api/strategies/{strategy_id}')
async def delete_strategy_list(strategy_id: str):
    try:
        query = strategies.delete(whereclause=sqlalchemy.text(f'id="{strategy_id}"'))
        record_id = await database.execute(query)
        return {'code': 0, 'data': {'record_id': record_id, 'message': '删除成功'}}
    except Exception as e:
        return {'code': -1, 'data': {'message': '删除失败：' + str(e)}}


@app.get('/api/issues/')
async def get_issue_list(skip: int = 0, limit: int = 10):
    issues_list = await database.fetch_all('select distinct(issue) from topic')
    issues_list = [{'id': i + 1, 'name': issue[0]} for i, issue in enumerate(issues_list)]
    return {'data': issues_list[skip: skip + limit], 'total': len(issues_list)}


@app.get('/api/news/')
async def get_news_list(skip: int = 0, limit: int = 10, topic_id: Optional[int] = None, start: str = None, end: str = None):
    whereclause = f'topic_id="{topic_id}"'
    if start: whereclause += f'and publish_time >= "{datetime.strptime(start, "%Y%m%d").strftime("%Y-%m-%d")}"'
    if end: whereclause += f'and publish_time <= "{datetime.strptime(end, "%Y%m%d").strftime("%Y-%m-%d")}"'
    query = news.select().limit(limit).offset(skip).where(whereclause=sqlalchemy.text(whereclause))
    news_list = await database.fetch_all(query)
    total = await database.fetch_all(sqlalchemy.select([sqlalchemy.func.count()]).select_from(news).where(whereclause=sqlalchemy.text(whereclause)))
    return {'data': news_list, 'total': total[0][0]}


@app.get('/api/news/{news_id}')
async def get_news_item(news_id: int):
    query = news.select().where(whereclause=sqlalchemy.text(f'id="{news_id}"'))
    news_list = await database.fetch_all(query)
    return {'data': news_list[0]}


@app.put('/api/news/{news_id}')
async def update_news_item(news_id: int, news_item: News):
    query = news.update(whereclause=sqlalchemy.text(f'id="{news_id}"')).values(**news_item.dict())
    record_id = await database.execute(query)
    return {'code': 0, 'data': {'record_id': record_id}}


@app.get('/api/statistic/strategy/{topic_id}')
async def get_statistic_strategy(topic_id: int, start: str = None, end: str = None):
    counter = Counter()
    whereclause = f'topic_id="{topic_id}"'
    if start: whereclause += f'and publish_time >= "{datetime.strptime(start, "%Y%m%d").strftime("%Y-%m-%d")}"'
    if end: whereclause += f'and publish_time <= "{datetime.strptime(end, "%Y%m%d").strftime("%Y-%m-%d")}"'
    query = news.select().where(whereclause=sqlalchemy.text(whereclause))
    news_list = await database.fetch_all(query)
    for n in news_list:
        for strategy_id in n['strategy_id'] + n['predict_strategy_id']:
            counter(int(strategy_id))
    return {'data': counter.order_list(rev=True)}


@app.get('/api/statistic/newstrend/{topic_id}')
async def get_statistic_newstrend(topic_id: int, start: str = None, end: str = None):
    whereclause = f'topic_id="{topic_id}"'
    if start: whereclause += f'and publish_time >= "{datetime.strptime(start, "%Y%m%d").strftime("%Y-%m-%d")}"'
    if end: whereclause += f'and publish_time <= "{datetime.strptime(end, "%Y%m%d").strftime("%Y-%m-%d")}"'
    query = sqlalchemy.select([sqlalchemy.func.count(), sqlalchemy.func.date_format(news.columns.publish_time, '%Y-%m')]).select_from(news) \
        .where(whereclause=sqlalchemy.text(whereclause)) \
        .group_by(sqlalchemy.func.date_format(news.columns.publish_time, '%Y-%m')) \
        .order_by(sqlalchemy.asc(sqlalchemy.func.date_format(news.columns.publish_time, '%Y-%m')))
    news_statistic_by_date = await database.fetch_all(query)
    news_statistic_by_date = [{'date': r['date_format_1'], 'count': r['count_1']} for r in news_statistic_by_date]
    return {'data':  interpolation(news_statistic_by_date)}


app.include_router(
    background.router,
    prefix='/api/background',
)

app.include_router(
    predict.router,
    prefix='/api/predict',
)