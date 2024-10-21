from fundar_llms.dimred.tsne import TSNE as TSNE
from fundar_llms.dimred.umap import UMAP as UMAP

def umap_project_embeddings(umap_transform, embeddings, show_progress, strict: bool, dimensions: int): ...
def tsne_project_embeddings(tsne_transform, embeddings, show_progress): ...
def project_data(transform, embeddings, by: str = None, show_progress: bool = True, strict: bool = True, dimensions: int = 2): ...