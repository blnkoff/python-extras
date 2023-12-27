import re
from typing import MutableMapping, Mapping, Any

__all__ = [
    'snake_case',
    'camel_case',
    'pascal_case',
    'find_by_key',
    'constant_case',
    'kebab_case'
]


def find_by_key(__dict: MutableMapping | Mapping, user_key: Any) -> Any | None:
    if user_key in __dict:
        return __dict[user_key]

    for key, value in __dict.items():
        if isinstance(value, dict):
            return find_by_key(value, user_key)
        elif isinstance(value, list) or isinstance(value, tuple) and isinstance(value[0], dict):
            return find_by_key(value[0], user_key)

    return None


def snake_case(s: str) -> str:
    """
    Convert a string to snake_case.
    """
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s)
    s = re.sub(r'\W+', '_', s).lower()
    s = re.sub(r'_+', '_', s)
    return s


def camel_case(s: str) -> str:
    """
    Convert a string to camelCase.
    """
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s)
    s = re.sub(r'\W+', '_', s)
    words = s.split('_')
    capitalized_words = [word.capitalize() for word in words]
    return capitalized_words[0].lower() + ''.join(capitalized_words[1:])


def pascal_case(s: str) -> str:
    """
    Convert a string to PascalCase.
    """
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s)
    s = re.sub(r'\W+', '_', s)
    words = s.split('_')
    capitalized_words = [word.capitalize() for word in words]
    return ''.join(capitalized_words)


def constant_case(s: str) -> str:
    """
    Convert a string to CONSTANT_CASE.
    """
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s)
    s = re.sub(r'\W+', '_', s)
    return s.upper()


def kebab_case(s: str) -> str:
    """
    Convert a string to kebab-case
    """
    s = re.sub(r"(\s|_|-)+", " ", s)
    s = re.sub(r"[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+",
               lambda mo: ' ' + mo.group(0).lower(), s)
    s = '-'.join(s.split())
    return s
