import os
import json
import asyncio
import concurrent
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks
import sqlalchemy

from declaration import Strategy, status, news
from database import database, host, user, password, database_
from utils.mysql import DataBase
from helpers import Logger
from vendor.make_data import main as make_data_main
from train import train

logger = Logger()
router = APIRouter()


def non_coroutine_train_task():    
    conn = DataBase(host, user, password, database_)
    try:
        record = conn.select('status', name='train')
        if record and record[0]:
            if record[0]['value']:
                pass
            else:
                conn.update({
                    'table': 'status',
                    'constraints': {
                        'name': 'train',
                    }
                }, value=1, request_submit_time=datetime.now())
                
                output_dir = './temp/'
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                tables = [t[f'Tables_in_{database_}'] for t in conn.execute('SHOW TABLES', res=True)]

                for table in tables:
                    res = conn.select(table)
                    data = [{k: v if not isinstance(v, datetime) else v.strftime('%Y-%m-%d %H:%M:%S') for k, v in d.items()} for d in res]
                    with open(os.path.join(output_dir, f'{table}.json'), 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent='\t')


                logger.info('making data')
                make_data_main('./temp/news.json', './News_Demo/data/')

                logger.info('training')
                train('HAN_0.json')

                logger.info('predicting')
                from analyze.strategy import StrategyPredictor
                sp = StrategyPredictor()
                records = conn.select('status')
                corpus = [{'title': n['title'], 'content': n['content']} for n in records]
                strategy_ids = sp.predict(corpus)
                
                for i, n in enumerate(records):
                    conn.update({
                        'table': 'news',
                        'constraints': {
                            'id': n['id'],
                        }
                    }, predict_strategy_id=[int(id_) for id_ in strategy_ids[i]['strategy_ids']])
                
                logger.info('completed')
                conn.update({
                    'table': 'status',
                    'constraints': {
                        'name': 'train',
                    }
                }, value=0, update_time=datetime.now())
    except Exception as e:
        print(e)
        conn.update({
            'table': 'status',
            'constraints': {
                'name': 'train',
            }
        }, value=0)
        conn.close()


@router.post('/train', status_code=202)
async def train_(background_tasks: BackgroundTasks):
    record = await database.fetch_one(status.select(whereclause=sqlalchemy.text(f'name="train"')))
    if record['value']:
        return {'code': 1, 'data': {'message': '模型正在训练中，请稍后重试'}}
    # background_tasks.add_task(train_task)
    loop = asyncio.get_event_loop()
    with concurrent.futures.ProcessPoolExecutor() as pool:
        await loop.run_in_executor(pool, non_coroutine_train_task)
    return {'code': 0, 'data': {'message': '开始训练模型'}}


@router.get('/train-status')
async def get_train_status():
    try:
        record = await database.fetch_one(status.select(whereclause=sqlalchemy.text(f'name="train"')))
        return {'code': 0, 'data': record}
    except:
        return {'code': -1, 'data': {
            'message': '抱歉，出错了'
        }}