from abc import ABC as AbstractBaseClass

class DataclassDictUtilsMixin(AbstractBaseClass):
    @classmethod
    def from_dict(cls, data): ...
    def to_dict(self, compact: bool = False): ...