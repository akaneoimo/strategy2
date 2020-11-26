import random
from News_Demo.demo_str import Demo

class StrategyPredictor:
    def __init__(self):
        self.demo = Demo("HAN_0.json")
    
    def predict(self, data: list) -> list:
        """
        INPUT
        data: [{'title': 'news_title', 'content': 'news_text'}, ...]

        OUTPUT: [{'strategy_ids': ['0', '4', '5']}, ...]
        """
        return self.demo.predict(data)
        # return self._random_predict(data)

    def __fake_predict(self, data):
        return [{'strategy_ids': ['1']} for _ in data]

    def _random_predict(self, data, candidate_strategy_ids=[1]):
        """
        INPUT
        data: [{'title': 'news_title', 'content': 'news_text'}, ...]

        OUTPUT: [{'strategy_ids': ['0', '4', '5']}, ...]
        """
        return[{'strategy_ids': random.sample(candidate_strategy_ids, k=min(len(candidate_strategy_ids), random.randint(1, 5)))} for _ in data]