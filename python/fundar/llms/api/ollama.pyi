from _typeshed import Incomplete
from fundar_llms.api.interface import Base64 as Base64, PlainPromptInterface as PlainPromptInterface
from fundar_llms.utils import get_available_vram as get_available_vram
from ollama import Client as _OllamaClient
from typing import Any

OLLAMA_DEFAULT_OPTIONS: Incomplete

class OllamaClient(PlainPromptInterface, _OllamaClient):
    def list_models(self, max_vram: Incomplete | None = None): ...
    def generate(self, model: str, prompt: str, raw: bool | None = None, image: Base64 | None = None, suffix: str | None = None, format: str | None = None, system: str | None = None, context: Any | None = None, stream: bool | None = None, num_ctx: int | None = None, num_predict: int | None = None, temperature: float | None = None, top_k: int | None = None, top_p: float | None = None, *args, **kwargs) -> Any: ...
