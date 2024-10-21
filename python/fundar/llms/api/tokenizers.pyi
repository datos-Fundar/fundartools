from _typeshed import Incomplete
from fundar_llms.utils import modelname as modelname

tokenizer_model_dataclass: Incomplete
auto_tokenizer_: Incomplete

class TokenizerModel:
    name: str
    needs_auth: bool
    def auto_tokenizer_from_pretrained(self): ...

DEFAULT_TOKENIZER_MAP: Incomplete

def get_tokenizer(model_name: str, tokenizer_map: dict[str, TokenizerModel] | None = None, default: TokenizerModel | None = None) -> TokenizerModel: ...
