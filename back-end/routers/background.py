import os
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks
import sqlalchemy

from declaration import Strategy, status, news
from database import database, database_
from helpers import Logger
from vendor.make_data import main as make_data_main
from train import train
from operation import dump_from_db_to_json

logger = Logger()
router = APIRouter()


async def train_task():
    logger.info('dumping data from mysql to json')
    try:
        record = await database.fetch_one(status.select(whereclause=sqlalchemy.text(f'name="train"')))
        if record['value']:
            pass
        else:
            await database.execute(status.update(whereclause=sqlalchemy.text(f'name="train"')).values(
                value=1,
                request_submit_time=datetime.now(),
            ))
            await dump_from_db_to_json(
                database=database_,
                output_dir='./temp/',
            )

        logger.info('making data')
        make_data_main('./temp/news.json', './News_Demo/data/')

        logger.info('training')
        train('HAN_0.json')

        logger.info('predicting')
        from analyze.strategy import StrategyPredictor
        sp = StrategyPredictor()
        records = await database.fetch_all(news.select())
        corpus = [{'title': n['title'], 'content': n['content']} for n in records]
        strategy_ids = sp.predict(corpus)
        for i, n in enumerate(records):
            await database.execute(news.update(whereclause=sqlalchemy.text(f'id={n["id"]}')).values(
                predict_strategy_id=[int(id_) for id_ in strategy_ids[i]['strategy_ids']]
            ))
        
        logger.info('completed')
        await database.execute(status.update(whereclause=sqlalchemy.text(f'name="train"')).values(
            value=0,
            update_time=datetime.now(),
        ))
    except Exception as e:
        print(e)
        await database.execute(status.update(whereclause=sqlalchemy.text(f'name="train"')).values(
            value=0,
        ))
        

@router.post('/train', status_code=202)
async def train_(background_tasks: BackgroundTasks):
    record = await database.fetch_one(status.select(whereclause=sqlalchemy.text(f'name="train"')))
    if record['value']:
        return {'code': 1, 'data': {'message': '模型正在训练中，请稍后重试'}}
    background_tasks.add_task(train_task)
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