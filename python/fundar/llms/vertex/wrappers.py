from google.cloud.aiplatform_v1beta1.types.content import SafetyRating
from typing import get_args
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
    Image,
    HarmBlockThreshold,
    SafetySetting
)

class Wrapper:
    def __init__(self, inner):
        self.inner = inner
    
    def to_dict(self):
        if isinstance(self.inner, dict):
            return self.inner
        elif 'to_dict' in dir(self.inner):
            return self.inner.to_dict()
        else:
            raise NotImplemented(f'Inner type {type(self.inner)} does not implement to_dict.')
    
class SystemPrompt(Wrapper):
    @staticmethod
    def typecheck(obj) -> bool:
        base_types = (str, Image, Part)

        if isinstance(obj, base_types):
            return True

        if isinstance(obj, list):
            return all(isinstance(item, base_types) for item in obj)

        return False
    
    def __init__(self, inner):
        if not SystemPrompt.typecheck(inner):
            raise TypeError(f"Unsupported type for SystemPrompt: {type(inner)}")
        super().__init__(inner)
    
    def __str__(self):
        return f'SystemPrompt({str(self.inner).strip()})'
    
    def __repr__(self):
        return str(self)
    
    @classmethod
    def from_file(cls, path: str) -> 'SystemPrompt':
        with open(path, 'r') as f:
            return cls(f.readlines())
    
class SafetySettings(Wrapper):
    @staticmethod
    def typecheck(obj) -> bool:
        settings_types = get_args(SafetySettingsType)

        # Check for List[SafetySetting]
        if isinstance(obj, list) and all(isinstance(item, SafetySetting) for item in obj):
            return True

        if isinstance(obj, dict) and all(
            isinstance(key, HarmCategory) and isinstance(value, HarmBlockThreshold)
            for key, value in obj.items()):
            return True

        return False
    
    @classmethod
    def equal_threshold(cls, threshold: int) -> 'SafetySettings':
        """

        
        Values:
            HARM_BLOCK_THRESHOLD_UNSPECIFIED (0):
                Unspecified harm block threshold.
            BLOCK_LOW_AND_ABOVE (1):
                Block low threshold and above (i.e. block
                more).
            BLOCK_MEDIUM_AND_ABOVE (2):
                Block medium threshold and above.
            BLOCK_ONLY_HIGH (3):
                Block only high threshold (i.e. block less).
            BLOCK_NONE (4):
                Block none.
        """
        return cls({k: HarmBlockThreshold(threshold) for k in HarmCategory})
    
    def __init__(self, inner):
        if not SafetySettings.typecheck(inner):
            raise TypeError(f"Unsupported type for SafetySettings: {type(inner)}")
        super().__init__(inner)
    
    def __str__(self):
        return f'SafetySettings({str(self.inner).to_dict() if not isinstance(self.inner, dict) else self.inner})'
    
    def __repr__(self):
        return str(self)

class GenerationConfigWrapper(Wrapper):
    @staticmethod
    def typecheck(obj) -> bool:
        if isinstance(obj, GenerationConfig):
            return True
        
        if isinstance(obj, dict) and all(isinstance(key, str) for key in obj.keys()):
            return True
        
        return False
    
    def __init__(self, inner):
        if not GenerationConfigWrapper.typecheck(inner):
            raise TypeError(f"Unsupported type for GenerationConfig: {type(inner)}")
        super().__init__(inner)
    
    def __str__(self):
        return f'GenerationConfigWrapper({str(self.inner).to_dict()})'
    
    def __repr__(self):
        return str(self)