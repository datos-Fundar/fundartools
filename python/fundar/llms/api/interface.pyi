from _typeshed import Incomplete
from fundar_llms import Base64 as Base64, Context as Context
from fundar_llms.utils import DataclassDictUtilsMixin as DataclassDictUtilsMixin
from typing import Any, Protocol

response_dataclass: Incomplete

class BaseResponse(DataclassDictUtilsMixin):
    model: str
    prompt: str
    system: str
    response: str
    total_duration: int
    load_duration: int | None
    done: bool | None
    done_reason: str | None
    context: Context | None
    num_ctx: int | None
    num_predict: int | None
    temperature: float | None
    top_k: float | None
    top_p: float | None
    extra: Any | None

class PlainPromptInterface(Protocol):
    def generate(self, model: str, prompt: str, raw: bool | None = None, image: Base64 | None = None, suffix: str | None = None, format: str | None = None, system: str | None = None, context: Context | None = None, stream: bool | None = None, num_ctx: int | None = None, num_predict: int | None = None, temperature: float | None = None, top_k: int | None = None, top_p: float | None = None, *args, **kwargs) -> Any: ...
