from collections import UserDict
from typing import Any, Literal, Type, TypedDict, get_args, Optional, Callable, Self, Union, Mapping, MutableMapping
from python_extras.tools import *

__all__ = [
    'in_literal',
    'is_typed_dict',
    'SnakedDict',
    'CameledDict',
    'is_decimal',
    'validate_number',
    'translate_response'
]

_Mapping = Union[Mapping, MutableMapping]


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


def is_decimal(input_string: str) -> bool:
    exceptions = (ValueError, AttributeError, IndexError, TypeError)
    try:
        float(input_string)
        is_float = True
    except exceptions:
        is_float = False

    try:
        is_integer = input_string.isdecimal()
    except exceptions:
        is_integer = False

    return is_float or is_integer


def validate_number(input_string: str) -> float | int | str:
    if is_decimal(input_string):
        try:
            int_value = int(input_string)
        except ValueError:
            int_value = None

        float_value = float(input_string)
        value = int_value if int_value == float_value else float_value
        return value
    else:
        return input_string


class _MultiCaseDict(UserDict):
    def __init__(self, __dict: _Mapping | Self, case_handler: Callable[[str], str], translate_numbers: bool = False):
        user_cased_dict = __dict if __dict else {}

        cased_dict = dict()
        key_map = dict()
        key_occuring = set()

        for user_key, value in user_cased_dict.items():
            if not (cased_key := case_handler(user_key)) in key_occuring:
                if translate_numbers:
                    value = validate_number(value)

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
            __dict: _Mapping,
            case_handler: Callable[[str], str],
            translate_numbers: bool = False
    ) -> Self:
        user_dict = __dict
        new_dict = {}
        for key, value in user_dict.items():
            if isinstance(value, _Mapping | _MultiCaseDict):
                for nested_key, nested_value in value.items():
                    if isinstance(nested_value, _Mapping | _MultiCaseDict):
                        value[nested_key] = cls.recursive_case(nested_value, case_handler)

                new_dict[key] = cls(value, case_handler, translate_numbers=translate_numbers)
            elif isinstance(value, list):
                new_dict[key] = [
                    cls.recursive_case(item, case_handler)
                    if isinstance(item, _Mapping)
                    else item for item in value
                ]
            else:
                new_dict[key] = value

        return cls(new_dict, case_handler, translate_numbers=translate_numbers)

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
    def __init__(self, __dict: Optional[dict] = None, translate_numbers: bool = False):
        snaked_dict = _MultiCaseDict.recursive_case(__dict, snake_case, translate_numbers=translate_numbers)
        super().__init__(snaked_dict, snake_case, translate_numbers=translate_numbers)


class CameledDict(_MultiCaseDict):
    def __init__(self, __dict: Optional[dict] = None, translate_numbers: bool = False):
        cameled_dict = _MultiCaseDict.recursive_case(__dict, camel_case, translate_numbers=translate_numbers)
        super().__init__(cameled_dict, camel_case, translate_numbers=translate_numbers)


def translate_response(response: dict | list, translate_numbers: bool = False) -> dict | list:
    if isinstance(response, list):
        if len(response) and isinstance(response[0], dict):
            for idx, item in enumerate(response):
                response[idx] = SnakedDict(item, translate_numbers=translate_numbers)
    elif isinstance(response, dict):
        response = SnakedDict(response, translate_numbers=translate_numbers)

    return response
