import os
import json
import asyncio
import random
from datetime import datetime

import databases
import sqlalchemy

from declaration import topics, strategies, news, status, metadata


async def dump_from_db_to_json(database='science', output_dir='./temp/'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    from database import host, user, port, password
    DATABASE_URL = f'mysql://{user}{f":{password}" if password else ""}@{host}{f":{port}" if port else ""}/{database}'
    database_ = databases.Database(DATABASE_URL)
    await database_.connect()

    try:
        tables = [t[f'Tables_in_{database}'] for t in await database_.fetch_all('SHOW TABLES')]

        for table in tables:
            res = await database_.fetch_all(f'SELECT * FROM {table}')
            data = [{k: v if not isinstance(v, datetime) else v.strftime('%Y-%m-%d %H:%M:%S') for k, v in d.items()} for d in res]
            with open(os.path.join(output_dir, f'{table}.json'), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent='\t')
    finally:
        await database_.disconnect()


async def _init_status():    
    DATABASE_URL = f'mysql://root@localhost/science3'
    database = databases.Database(DATABASE_URL)

    await database.connect()
    try:
        await database.execute('drop table status')
    finally:
        engine = sqlalchemy.create_engine(DATABASE_URL)
        metadata.create_all(engine)
        
        await database.execute(status.insert(), {
            'name': 'train',
            'value': 0,
            'request_submit_time': datetime.now(),
            'update_time': datetime.now(),
        })

        await database.disconnect()


async def _write_all_json_to_database():
    DATABASE_URL = f'mysql://root@localhost/science3'
    database = databases.Database(DATABASE_URL)

    engine = sqlalchemy.create_engine(DATABASE_URL)
    metadata.create_all(engine)

    await database.connect()
    with open('data/topic.json', 'r', encoding='utf-8') as f:
        topic_data = json.load(f)
        await database.execute_many(topics.insert(), topic_data)
    
    topicname2id = {}
    for t in topic_data:
        if t['topic'] not in topicname2id:
            topicname2id[t['topic']] = [t['id']]
        else:
            topicname2id[t['topic']].append(t['id'])

    with open('data/strategy.json', 'r', encoding='utf-8') as f:
        strategy_data = json.load(f)
        await database.execute_many(strategies.insert(), strategy_data)

    temp = set()
    with open('data/news.json', 'r', encoding='utf-8') as f:
        line = f.readline().strip()
        while line:
            data = json.loads(line)

            for topic_id in topicname2id[data['topic']]:
                await database.execute(news.insert(), {
                    'topic_id': topic_id,
                    'publish_time': datetime.strptime(data['publish_time'], '%Y-%m-%d %H:%M:%S'),
                    'title': data['title'],
                    'url': data['url'],
                    'site': data['site'],
                    'source': data['source'],
                    'content': data['content'],
                    'strategy_id': json.loads(data['strategy_id']),
                    'predict_strategy_id': [],
                })
                for sid in json.loads(data['strategy_id']):
                    temp.add(sid)

            line = f.readline().strip()
    await database.disconnect()


async def _update_keywords_keysentences():
    from analyze.topic import NewsProcessor
    np = NewsProcessor()

    DATABASE_URL = f'mysql://root@localhost/science3'
    database_ = databases.Database(DATABASE_URL)
    await database_.connect()
    
    all_topics = await database_.fetch_all(topics.select())
    for t in all_topics:
        news_list = await database_.fetch_all(news.select().where(whereclause=sqlalchemy.text(f'topic_id="{t["id"]}"')))
        print(f'{t["id"]}: {t["topic"]}')
        keywords, keysentences = np.abstract(random.sample(news_list, k=min(len(news_list), 100)))
        await database_.execute(topics.update(whereclause=sqlalchemy.text(f'id="{t["id"]}"')).values(
            keywords=keywords,
            keysentences=keysentences,
        ))

    await database_.disconnect()


async def _update_model():
    from helpers import Logger
    from vendor.make_data import main as make_data_main
    from train import train

    logger = Logger()

    logger.info('dump_from_db_to_json')
    await dump_from_db_to_json('science3', './temp/')
    
    logger.info('making data')
    make_data_main('./temp/news.json', './News_Demo/data/')

    logger.info('training')
    train('HAN_0.json')


async def _update_predict_strategy():
    DATABASE_URL = f'mysql://root@localhost/science3'
    database = databases.Database(DATABASE_URL)
    
    await database.connect()

    from analyze.strategy import StrategyPredictor
    sp = StrategyPredictor()
    
    records = await database.fetch_all(news.select())
    corpus = [{'title': n['title'], 'content': n['content']} for n in records]
    strategy_ids = sp.predict(corpus)
    for i, n in enumerate(records):
        await database.execute(news.update(whereclause=sqlalchemy.text(f'id={n["id"]}')).values(
            predict_strategy_id=[int(id_) for id_ in strategy_ids[i]['strategy_ids']]
        ))
    await database.disconnect()