
from dataclasses import dataclass
from enum import Enum, auto

from .info import SourceLocation, SourceRange


class TokenType(Enum):
    Undefined = auto()

    EndOfFile = auto()
    Newline = auto()
    LineComment = auto()
    DocComment = auto()

    Identifier = auto()
    Integer = auto()
    Float = auto()
    String = auto()

    OpenParenthesis = auto()  # (
    CloseParenthesis = auto()  # )
    OpenBracket = auto()  # [
    CloseBracket = auto()  # ]
    OpenBrace = auto()  # {
    CloseBrace = auto()  # }

    Comma = auto()  # ,
    Semicolon = auto()  # ;
    Dot = auto()  # .
    Colon = auto()  # :

    Assign = auto()  # =
    CompareEquals = auto()  # ==

    Minus = auto()  # -
    AssignSubtract = auto()  # -=
    ReturnArrow = auto()  # ->
    NotInitialized = auto()  # ---

    Plus = auto()  # +
    AssignAdd = auto()  # +=
    Asterisk = auto()  # *
    AssignMultiply = auto()  # *=
    Divide = auto()  # /
    AssignDivide = auto()  # /=
    Modulo = auto()  # %
    AssignModulo = auto()  # %=

    BitAnd = auto()  # &
    LogicAnd = auto()  # && and
    AssignBitAnd = auto()  # &=
    AssignLogicAnd = auto()  # &&=
    BitOr = auto()  # |
    LogicOr = auto()  # || or
    AssignBitOr = auto()  # |=
    AssignLogicOr = auto()  # ||=
    BitXOr = auto()  # ^
    AssignBitXOr = auto()  # ^=

    LogicNot = auto()  # ! not
    CompareNotEquals = auto()  # !=

    CompareLess = auto()  # <
    BitShiftLeft = auto()  # <<
    BitRotateLeft = auto()  # <<<
    CompareLessEquals = auto()  # <=
    AssignBitShiftLeft = auto()  # <<=
    AssignBitRotateLeft = auto()  # <<<=

    CompareGreater = auto()  # >
    BitShiftRight = auto()  # >>
    BitRotateRight = auto()  # >>>
    CompareGreaterEquals = auto()  # >=
    AssignBitShiftRight = auto()  # >>=
    AssignBitRotateRight = auto()  # >>>=

    BitInvert = auto()  # ~
    Question = auto()  # ?
    Follow = auto()  # @

    Import = auto()  # #import
    Library = auto()  # #library

    If = auto()  # if
    Else = auto()  # else
    While = auto()  # while
    For = auto()  # for
    True_ = auto()  # true
    False_ = auto()  # false

    Structure = auto()  # struct
    Enumeration = auto()  # enum


class TokenTag(Enum):
    IncompleteFormatNumber = auto()
    IncompleteFloatNumber = auto()
    IncompleteString = auto()
    IncompleteDocComment = auto()
    IncompleteCompilerAction = auto()
    IncompleteNotInitialized = auto()
    HexFormat = auto()
    BinFormat = auto()


@dataclass(slots=True)
class Token():
    type: TokenType
    lexeme: str
    start: SourceLocation
    tag: TokenTag = None

    def __len__(self):
        return len(self.lexeme)

    def to_range(self):
        if self.type is TokenType.DocComment and self.lexeme.count("\n"):
            return SourceRange(self.start, SourceLocation(
                self.start.line + self.lexeme.count("\n"),
                len(self.lexeme.split("\n")[-1])
            ))
        return SourceRange(self.start, SourceLocation(
            self.start.line,
            self.start.column + len(self)
        ))