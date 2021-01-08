from collections import defaultdict
from typing import List, Optional

from fastapi import APIRouter, File, UploadFile, Form
from pydantic import BaseModel
import sqlalchemy

from analyze.strategy import StrategyPredictor
from database import database
from declaration import strategies, topics
from helpers import Logger
logger = Logger('predict')


class Counter:
    def __init__(self):
        self.dict = defaultdict(int)

    def __call__(self, item):
        self.dict[item] += 1
    
    def __getitem__(self, index):
        return self.dict[index]

    def get_max_items(self, n=5):
        return sorted([(key, value) for key, value in self.dict.items()], key=lambda item: item[1], reverse=True)[:n]


class PredictInput(BaseModel):
    news: List
    # topic: Optional[str] = None
    max_num: Optional[int] = 5


router = APIRouter()


@router.post('/')
async def predict(data: PredictInput):
    predictor = StrategyPredictor()
    counter = Counter()
    predictions = [[int(str_id) for str_id in prediction['strategy_ids']] for prediction in predictor.predict(data.news)]

    for prediction in predictions:
        for id_ in prediction:
            counter(id_)

    max_items = counter.get_max_items(data.max_num)
    sumup = sum([item[1] for item in max_items])
    max_items = [{'id': id_, 'value': round(value / sumup, 4)} for id_, value in max_items]

    return {
        'sumup': max_items,
    }


@router.post('/uploadfile/')
async def upload_file(file: UploadFile = File(...), max_num: int = Form(5)):
    content = await file.read()
    import pandas as pd
    import io
    data = pd.read_csv(io.BytesIO(content), na_filter=False)
    predictor = StrategyPredictor()
    counter = Counter()

    logger.info('predicting...')
    predictions = [[int(str_id) for str_id in prediction['strategy_ids']] for prediction in predictor.predict([{
        'title': row.get('title', '') or row['content'][:20],
        'content': row['content'],
    } for _, row in data.iterrows()])]

    logger.info('counting...')
    for prediction in predictions:
        for id_ in prediction:
            counter(id_)
    max_items = counter.get_max_items(max_num)
    sumup = sum([item[1] for item in max_items])
    max_items = [{'id': id_, 'value': round(value / sumup, 4)} for id_, value in max_items]
    return {'sumup': max_items}

