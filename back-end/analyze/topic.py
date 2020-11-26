from News_Demo.demo_cls import Demo as DemoCls
from News_Demo.demo_abs import Demo as DemoAbs


class NewsProcessor:
    def __init__(self):
        self.demo_cls = DemoCls()
        self.demo_abs = DemoAbs()
    
    def cluster(self, data: list) -> (list, list):
        """
        INPUT
        data: [{'title': 'news_title', 'content': 'news_text'}, ...]

        OUTPUT
        results: [{'label': 0}, ...]
        clusters: [{'title': 'abstract', 'key_words': [('word', 0.134), ...], 'key_sentences': [('word', 0.134), ...]}]
        """
        return self.demo_cls.predict(data)
    
    def abstract(self, data: list) -> (list, list):
        """
        INPUT
        data: [{'title': 'news_title', 'content': 'news_text'}, ...]

        OUTPUT
        key_words: [(word, weight), ...]
        key_sentences: [(sentence, weight), ...]
        """
        return self.demo_abs.predict(data)