
from dataclasses import dataclass

from .nodes import Node


@dataclass(slots=True)
class TypeCheckResult():
    pass


def check_type(ast: Node):
    return TypeCheckResult()