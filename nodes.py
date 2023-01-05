from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, TypeVar

from .info import SourceRange

Any = object()

autolist = field(default_factory=list)
node = dataclass(slots=True)

@node
class _Error():
    diagnostic: Any = None

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

@node
class _Function():
    header: Node[_FunctionType] = None
    block: Node[_Block] = None

@node
class _Block():
    statements: list[Node] = autolist

@node
class _Return():
    node: Node = None


@node
class _BinOp():
    left: Node = None
    right: Node = None

@node
class _Assignment(_BinOp): pass
@node
class _BinOpAdd(_BinOp): pass
@node
class _BinOpSubtract(_BinOp): pass
@node
class _BinOpMultiply(_BinOp): pass
@node
class _BinOpDivide(_BinOp): pass
@node
class _BinOpModulo(_BinOp): pass

@node
class _BinOpBitAnd(_BinOp): pass
@node
class _BinOpLogicAnd(_BinOp): pass
@node
class _BinOpBitOr(_BinOp): pass
@node
class _BinOpLogicOr(_BinOp): pass
@node
class _BinOpBitXOr(_BinOp): pass

@node
class _BinOpBitShiftLeft(_BinOp): pass
@node
class _BinOpBitRotateLeft(_BinOp): pass
@node
class _BinOpBitShiftRight(_BinOp): pass
@node
class _BinOpBitRotateRight(_BinOp): pass

@node
class _BinOpCompareEquals(_BinOp): pass
@node
class _BinOpCompareNotEquals(_BinOp): pass
@node
class _BinOpCompareLess(_BinOp): pass
@node
class _BinOpCompareLessEquals(_BinOp): pass
@node
class _BinOpCompareGreater(_BinOp): pass
@node
class _BinOpCompareGreaterEquals(_BinOp): pass

@node
class _UnaryOp():
    node: Node = None
@node
class _UnaryOpPlus(_UnaryOp): pass
@node
class _UnaryOpNegate(_UnaryOp): pass
@node
class _UnaryOpPointer(_UnaryOp): pass
@node
class _UnaryOpLogicNot(_UnaryOp): pass
@node
class _UnaryOpBitInvert(_UnaryOp): pass
@node
class _UnaryOpNullCheck(_UnaryOp): pass
@node
class _UnaryOpFollow(_UnaryOp): pass

@node
class _UnaryOpBitInvert(_UnaryOp): pass
@node
class _UnaryOpNullCheck(_UnaryOp): pass


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
    Function = _Function
    Block = _Block
    Return = _Return

    Assigment = _Assignment
    BinOpAdd = _BinOpAdd
    BinOpSubtract = _BinOpSubtract
    BinOpMultiply = _BinOpMultiply
    BinOpDivide = _BinOpDivide
    BinOpModulo = _BinOpModulo
    BinOpBitAnd = _BinOpBitAnd
    BinOpLogicAnd = _BinOpLogicAnd
    BinOpBitOr = _BinOpBitOr
    BinOpLogicOr = _BinOpLogicOr
    BinOpBitXOr = _BinOpBitXOr
    BinOpBitShiftLeft = _BinOpBitShiftLeft
    BinOpBitRotateLeft = _BinOpBitRotateLeft
    BinOpBitShiftRight = _BinOpBitShiftRight
    BinOpBitRotateRight = _BinOpBitRotateRight
    BinOpCompareEquals = _BinOpCompareEquals
    BinOpCompareNotEquals = _BinOpCompareNotEquals
    BinOpCompareLess = _BinOpCompareLess
    BinOpCompareLessEquals = _BinOpCompareLessEquals
    BinOpCompareGreater = _BinOpCompareGreater
    BinOpCompareGreaterEquals = _BinOpCompareGreaterEquals
    UnaryOpPlus = _UnaryOpPlus
    UnaryOpNegate = _UnaryOpNegate
    UnaryOpPointer = _UnaryOpPointer
    UnaryOpLogicNot = _UnaryOpLogicNot
    UnaryOpBitInvert = _UnaryOpBitInvert
    UnaryOpNullCheck = _UnaryOpNullCheck
    UnaryOpFollow = _UnaryOpFollow
    UnaryOpBitInvert = _UnaryOpBitInvert


T = TypeVar("T")

class Node(Generic[T]):
    __slots__ = ("type", "data", "range")
    def __init__(self, type: type[T], range: SourceRange) -> None:
        self.type = type
        self.data = type()
        self.range = range

    def __repr__(self):
        return f"Node(type={self.type.__name__}, data={self.data}, range={self.range})"
