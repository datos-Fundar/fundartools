from functools import wraps
from typing import Protocol, Iterable
from proto.message import MessageMeta
from proto.marshal.collections.repeated import RepeatedComposite
from google.cloud.aiplatform_v1beta1.types.content import SafetyRating
from .wrappers import SafetySettings, SystemPrompt, GenerationConfigWrapper
from fundar import json
from fundar.structures import lista
import os.path
from google.api_core.exceptions import ServiceUnavailable
from vertexai.generative_models._generative_models import (
    # Importo todo esto desde aca para que este bien tipado
    _GenerativeModel as GenerativeModel,
    GenerationConfig,
    GenerationResponse,
    Candidate,
    Part,
    HarmCategory,
    ChatSession,
    Content,
    GenerationConfigType,
    SafetySettingsType,
    Tool,
    ToolConfig,
    PartsType,
    SafetySetting
)

SafetyRating.to_dict = lambda self: MessageMeta.to_dict(SafetyRating, self) 

class SafetyRatings(RepeatedComposite[SafetyRating]):
    def to_dict(self):
        """
        Transforma un iterable de SafetyRatings en un diccionario.
        """
        return {
            HarmCategory(d.pop('category')): d 
            for x in self 
            for d in [x.to_dict()] # aliasing
        }

class Chat(ChatSession):
    @wraps(ChatSession.__init__)
    def __init__(self, *args, model=None, **kwargs):
        super().__init__(model, *args, **kwargs)
    
    def __str__(self):
        return f'Chat({self._history})'
    
    def __repr__(self):
        return str(self)
    
class FewShotPrompt(Chat):
    @classmethod
    def from_tuples(cls, ts: list[tuple[str, str]]):
        history = list()
        for a,b in ts:
            _a = Content(parts=[Part.from_text(a)], role='user')
            _b = Content(parts=[Part.from_text(b)], role='model')
            history.extend([_a, _b])
        return cls(history=history)
    
    @classmethod
    def from_records(cls, ts: list[dict[str, str]]):
        history = list()
        for x in ts:
            _a = Content(parts=[Part.from_text(x['user'])], role='user')
            _b = Content(parts=[Part.from_text(x['model'])], role='model')
            history.extend([_a, _b])
        return cls(history=history)
    
    @classmethod
    def from_json(cls, path):
        d = json.load(path)
        return cls.from_records(d)


class Builder(Protocol):
    def set_generation_config(self, generation_config: GenerationConfig) -> 'Builder': ...
    def set_safety_settings(self, safety_settings: SafetySettings) -> 'Builder': ...
    def set_tools(self, tools: list[Tool]) -> 'Builder': ...
    def set_tool_config(self, tool_config: ToolConfig) -> 'Builder': ...
    def set_system_instruction(self, system_instruction: SystemPrompt) -> 'Builder': ...
    def set_post_build_fewshot(self, fewshot: FewShotPrompt) -> 'Builder': ...
    def build(self) -> 'Model': ...
    def __or__(self, other) -> 'Builder': ...

class ModelBuilderFactory:
    @staticmethod
    def get_builder(cls):
        class _Builder(Builder):
            __all_fields__ = ['generation_config', 'safety_settings', 'tools', 'tool_config', 'system_instruction']
            generation_config = None
            safety_settings = None
            tools = None
            tool_config = None
            system_instruction = None
            stream: bool

            def __init__(self, model_name):
                self.postbuild = []
                self.model_name = model_name
            
            def set_generation_config(self, generation_config):
                self.generation_config = generation_config
                return self

            def set_safety_settings(self, safety_settings):
                self.safety_settings = safety_settings
                return self
            
            def set_tools(self, tools):
                self.tools = tools
                return self

            def set_tool_config(self, tool_config):
                self.tool_config = tool_config
                return self
            
            def set_system_instruction(self, system_instruction):
                self.system_instruction = system_instruction
                return self
            
            def set_post_build_fewshot(self, fewshot: FewShotPrompt):
                self.postbuild.append(fewshot)
                return self
            
            def build(self):
                result: Builder
                result = cls(
                    self.model_name,
                    generation_config=self.generation_config,
                    safety_settings=self.safety_settings,
                    tools=self.tools,
                    tool_config=self.tool_config,
                    system_instruction=self.system_instruction
                )

                result: Model
                if len(self.postbuild) > 0:
                    for x in self.postbuild:
                        if isinstance(x, FewShotPrompt):
                            result.set_chat(x)
                        else:
                            raise NotImplemented
                
                return result
            
            @property
            def declared_fields(self):
                return {x:y for x in _Builder.__all_fields__
                        for y in [getattr(self, x)]
                        if y is not None}
                # return [(lambda x: f'{attr}={str(x)}')(getattr(self, attr)) 
                #         for attr in _Builder.__all_fields__ 
                #         if getattr(self, attr) is not None]

            def __str__(self):
                declared_fields = ", ".join(f'{k}={v}' for k,v in self.declared_fields.items())
                return f'Builder(model={self.model_name}, {declared_fields})'
            
            def __repr__(self):
                return str(self)
            
            @staticmethod
            def __ERROR_UNSUPPORTED_TYPE_PIPE__(self, other):
                raise TypeError(f"unsupported operand type(s) for |: '{type(self)}' and '{type(other)}'")
            
            def __or__(self, other):
                if isinstance(other, GenerationConfig):
                    self.set_generation_config(other)
                elif isinstance(other, SafetySetting):
                    self.set_safety_settings(other)
                elif isinstance(other, ToolConfig):
                    self.set_tool_config(other)
                elif isinstance(other, GenerationConfigWrapper):
                    self.set_generation_config(other.inner)
                elif isinstance(other, SafetySettings):
                    self.set_safety_settings(other.inner)
                elif isinstance(other, SystemPrompt):
                    self.set_system_instruction(other.inner)
                elif isinstance(other, list):
                    if len(other) == 0:
                        raise NotImplementedError("Ambiguous empty list is not supported")
                    
                    x = other[0]
                    if not isinstance(x, Tool):
                        _Builder.__ERROR_UNSUPPORTED_TYPE_PIPE__(x)
                    
                    self.set_tools(other)

                elif isinstance(other, FewShotPrompt):
                    self.set_post_build_fewshot(other)
                else:
                    _Builder.__ERROR_UNSUPPORTED_TYPE_PIPE__(other)

                return self
        return _Builder

class Model(GenerativeModel):
    @wraps(GenerativeModel.__init__)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat = None
        self.model_path = self._model_name
        self.model_name = os.path.split(self._model_name)[1]

    @classmethod
    def builder(cls, model_name):
        builder = ModelBuilderFactory.get_builder(cls)
        return builder(model_name)

    def __str__(self):
        return f'Model({self.model_name}' + (f', {self.chat})' if self.chat is not None else ')')
    
    def __repr__(self):
        return str(self)

    def set_chat(self, chat: Chat) -> 'Model':
        if not isinstance(chat, Chat):
            raise TypeError(f"unsupported operand type(s) for |: '{type(self)}' and '{type(chat)}'")
        
        if self.chat is None:
            self.chat = chat
            self.chat._model = self
        else:
            self.chat._history.extend(chat._history)
        
        return self
    
    def __or__(self, other: Chat) -> 'Model':
        return self.set_chat(other)
    
    def invoke(self, message, stream: bool = False) -> GenerationResponse | Iterable[GenerationResponse]:
        try:
            if self.chat is None:
                return self.generate_content(message, stream=stream)
            else:
                return self.chat.send_message(message, stream=stream)
        except ServiceUnavailable as su_exc:
            msg = su_exc.message
            msg += '\nIs there internet connection available?'
            raise ServiceUnavailable(msg)