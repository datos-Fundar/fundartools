from fundar.utils import Singleton

class SentenceTransformerEmbeddingsImport(metaclass=Singleton):
    def __init__(self):
        from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings as _SentenceTransformerEmbeddings
        self.embedding_function = _SentenceTransformerEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2', model_kwargs={'device': 'cuda'})

SentenceTransformerEmbeddings = SentenceTransformerEmbeddingsImport.get_instance().embedding_function
