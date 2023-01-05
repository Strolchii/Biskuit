from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, TypeVar

from .info import SourceRange

Any = object()

autolist = field(default_factory=list)
node = dataclass(slots=True)

@node
class _Error():
    diagnostic: Any

@node
class _Module():
    globals: list[Node] = autolist

@node
class _Import():
    path: str = None

@node
class _Alias():
    name: str = None
    value: Node = None
    doc: str = None

@node
class _Definition():
    name: str = None
    type: Node = None
    value: Node = None
    doc: str = None

@node
class _NamedType():
    name: str = None

@node
class _FunctionType():
    parameter: list[Node[NodeType.Parameter]] = autolist
    return_type: Node = None

@node
class _Parameter():
    name: str = None
    type: Node = None
    default_value: Node = None

@node
class _StructureType():
    member: list[Node] = autolist

@node
class _EnumType():
    member: list[Node] = autolist


class NodeType:
    Error = _Error
    Module = _Module
    Import = _Import
    Alias = _Alias
    Definition = _Definition
    NamedType = _NamedType
    FunctionType = _FunctionType
    Parameter = _Parameter
    StructureType = _StructureType
    EnumType = _EnumType


T = TypeVar("T")

class Node(Generic[T]):
    __slots__ = ("type", "data", "range")
    def __init__(self, type: type[T], range: SourceRange) -> None:
        self.type = type
        self.data = type()
        self.range = range

    def __repr__(self):
        return f"Node(type={self.type.__name__}, data={self.data}, range={self.range})"
