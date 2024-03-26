import numpy as np
from fundar.utils import Singleton

class _Reranker(metaclass=Singleton):
    def __init__(self):
        from sentence_transformers import CrossEncoder
        self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', device='cuda')

class Reranker:
    """
    Abstraction for the Cross-Encoder Reranker. It always initializes it and provides
    static functions to rerank items.
    """
    cross_encoder = _Reranker.get_instance().cross_encoder

    @staticmethod
    def rerank_from(universe, query, scores=False):
        pairs = [[query, doc] for doc in universe]
        scores_ = Reranker.cross_encoder.predict(pairs)
        if scores:
            return [(universe[o], scores_[o]) for o in np.argsort(scores_)[::-1]]
        return [universe[o] for o in np.argsort(scores_)[::-1]]
    
    def __init__(self, universe):
        self._universe = universe
    
    @classmethod
    def universe(cls, V):
        return cls(V)
    
    def rerank(self, query, scores=False):
        return Reranker.rerank_from(self._universe, query, scores)
