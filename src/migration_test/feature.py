from abc import ABCMeta, abstractmethod
from enum import Enum, auto
from pathlib import Path
from typing import Dict, Mapping, Hashable, Any, Sequence, Type
from re import match
from importlib import import_module
from datetime import datetime, date

def import_custom_class(module, cls) -> Type[object]:
    return object


class NotEncodableException(Exception):
    ...

class MissingClass(Exception):
    ...

class CodecType(Enum):

    json = auto()
    yaml = auto()

class CodecMeta(ABCMeta):
    ...

class CodecAbc(metaclass=CodecMeta):

    @property
    @classmethod
    @abstractmethod
    def _codec_type(self) -> CodecType:
        ...

    @property
    @classmethod
    @abstractmethod
    def _ext(self) -> str:
        ...

    @abstractmethod
    def encode(self, o: object) -> Dict[Hashable, Dict[Hashable, Any]]:
        return self._encode(o)
    
    def encode(self, o: object) -> Dict[Hashable, Dict[Hashable, Any]]:

        if isinstance(o, Dict):
            return {
                k: self.encode(v)
                for k, v in o.items()
            }
        elif isinstance(o, Sequence):
            return [self.encode(it) for it in o]

        elif isinstance(o, (bool, int, float)):
            return o
        
        elif isinstance(o, None):
            return self._none_handler(o)
        
        elif isinstance(o, Hashable):
            return str(o)

        else:
            try:
                _module = self.__module__
                _class = self.__class__.__name__
                _dict = self.__dict__
                return {f"<{_module._class}>": self.encode(_dict)}
            except Exception as e:
                raise NotEncodableException(f"Cannot encode object of type {type(o)}")


    @abstractmethod
    @classmethod
    def decode(cls, o) -> object:
        return cls._decode(o)

    @classmethod
    def _decode(cls, o) -> object:
        if isinstance(o, Mapping):
            return {
                cls._class_check(k): cls.decode(v)
                for k, v in o.items()
            }
        elif isinstance(o, Sequence):
            return [cls.decode(it) for it in o]

        elif isinstance(o, (bool, int, float)):
            return o
        
        elif isinstance(o, str):
            return cls.try_parse(o)

        return None

    @staticmethod
    def _class_check(key: Hashable) -> bool:
        pm = match(r"^\<?=((.*)\.)(.*)\>$", key)
        if x := pm.groups():
            m, _, n = x
            try:
                _cls = import_custom_class(m, n)
            except Exception:
                m = "builtins" or m
                raise MissingClass("Cannot find class {n} from module {m}")
        else:
            return str(key)

        return _cls

    @abstractmethod
    def to_str(self, o: object) -> str:
        ...

    @abstractmethod
    def to_file(self, o: object) -> Path:
        ...

    @abstractmethod
    def _none_handler(o):
        return None

    @abstractmethod
    @staticmethod
    def try_parse_str(o) -> Any:
        ...



class JsonCodec(CodecAbc):

    _codec_type = CodecType.json
    _ext = ".json"

    def encode(self, o: object):
        return super().encode(o)

    def decode(self, o: str):
        return super().decode(o)