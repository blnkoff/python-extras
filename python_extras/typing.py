from collections import UserDict
from typing import Any, Literal, Type, TypedDict, get_args, Optional, Callable, Self, Union
from .tools import *

__all__ = [
    'in_literal',
    'is_typed_dict',
    'SnakedDict',
    'CameledDict'
]


def in_literal(value: Any, expected_type: Literal) -> bool:
    values = get_args(expected_type)
    return value in values


def is_typed_dict(value: Any, typed_dict: Type[TypedDict]) -> bool:
    typed_dict_keys = typed_dict.__annotations__.keys()

    try:
        value_keys = value.keys()
    except AttributeError:
        return False

    return typed_dict_keys == value_keys


class _MultiCaseDict(UserDict):
    def __init__(self, __dict: dict | Self, case_handler: Callable[[str], str]):
        user_cased_dict = __dict if __dict else {}

        cased_dict = dict()
        key_map = dict()
        key_occuring = set()

        for user_key, value in user_cased_dict.items():
            if not (cased_key := case_handler(user_key)) in key_occuring:
                key_occuring.add(cased_key)
                key_map[cased_key] = user_key
                cased_dict[cased_key] = value

        self._case_handler = case_handler
        super().__init__(cased_dict)

    def __setitem__(self, key, value):
        case_handler = self._case_handler
        cased_key = case_handler(key)
        super().__setitem__(cased_key, value)

    @classmethod
    def recursive_case(
            cls,
            __dict: dict,
            case_handler: Callable[[str], str]
    ) -> Self:
        user_dict = __dict
        new_dict = {}
        for key, value in user_dict.items():
            if isinstance(value, Union[dict, _MultiCaseDict]):
                new_dict[key] = _MultiCaseDict(value, case_handler)
            elif isinstance(value, list):
                new_dict[key] = [
                    _MultiCaseDict(item, case_handler) if isinstance(item, Union[dict, _MultiCaseDict]) else item for
                    item in value]
            else:
                new_dict[key] = value

        return cls(new_dict, case_handler)

    def pascal_case(self) -> dict:
        pascal_cased_dict = {}
        pascal_cased_dict.update(_MultiCaseDict.recursive_case(self.data, pascal_case))
        return pascal_cased_dict

    def camel_case(self) -> dict:
        camel_cased_dict = {}
        camel_cased_dict.update(_MultiCaseDict.recursive_case(self.data, camel_case))
        return camel_cased_dict

    def constant_case(self) -> dict:
        constant_cased_dict = {}
        constant_cased_dict.update(_MultiCaseDict.recursive_case(self.data, constant_case))
        return constant_cased_dict

    def kebab_case(self) -> dict:
        kebab_cased_dict = {}
        kebab_cased_dict.update(_MultiCaseDict.recursive_case(self.data, kebab_case))
        return kebab_cased_dict

    def snake_case(self) -> dict:
        snake_cased_dict = {}
        snake_cased_dict.update(_MultiCaseDict.recursive_case(self.data, snake_case))
        return snake_cased_dict


class SnakedDict(_MultiCaseDict):
    def __init__(self, __dict: Optional[dict] = None):
        snaked_dict = _MultiCaseDict.recursive_case(__dict, snake_case)
        super().__init__(snaked_dict, snake_case)


class CameledDict(_MultiCaseDict):
    def __init__(self, __dict: Optional[dict] = None):
        cameled_dict = _MultiCaseDict.recursive_case(__dict, camel_case)
        super().__init__(cameled_dict, camel_case)
