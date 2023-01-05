
from dataclasses import dataclass
from collections import defaultdict

from .info import SourceCode, SourceLocation
from .tokens import Token, TokenType, TokenTag


@dataclass(slots=True)
class LexResult():
    tokens: list[Token]


class CharSets:
    Newline = set(("\n",))
    Space = set(" \r\t")
    Number = set("0123456789")
    NumberFormat = set("bx")
    HexNumber = Number | set("abcdefABCDEF")
    BinNumber = set("01")
    IdentifierStart = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_")
    Identifier = IdentifierStart | Number
    DocCommentEnd = set(("*",))
    StringEnd = set(('"',)) | Newline


class LexemeMaps:
    Keyword = {
        "if": TokenType.If,
        "else": TokenType.Else,
        "while": TokenType.While,
        "for": TokenType.For,
        "true": TokenType.True_,
        "false": TokenType.False_,
        "and": TokenType.LogicAnd,
        "or": TokenType.LogicOr,
        "not": TokenType.LogicNot,
        "struct": TokenType.Structure,
        "enum": TokenType.Enumeration,
    }
    Compiler = {
        "#import": TokenType.Import,
        "#library": TokenType.Library,
    }
    Literal = {
        "(": TokenType.OpenParenthesis,
        ")": TokenType.CloseParenthesis,
        "[": TokenType.OpenBracket,
        "]": TokenType.CloseBracket,
        "{": TokenType.OpenBrace,
        "}": TokenType.CloseBrace,
        ",": TokenType.Comma,
        ";": TokenType.Semicolon,
        ".": TokenType.Dot,
        ":": TokenType.Colon,
        "~": TokenType.BitInvert,
        "?": TokenType.Question,
        "@": TokenType.Follow,
    }


def tokenize(code: SourceCode):
    tokens = []

    idx: int = 0
    current: str = code[idx : idx+1]
    line: int = 0
    column: int = 0
    location: SourceLocation

    counter: defaultdict[TokenType, int] = defaultdict(int)

    def make_location():
        nonlocal location
        location = SourceLocation(line, column)

    def make_token(tt: TokenType, lexeme: list[str] | str, tag: TokenTag = None):
        if isinstance(lexeme, list):
            lexeme = "".join(lexeme)
        tokens.append(Token(tt, lexeme, location, tag))
        counter[tt] += 1

    def advance():
        nonlocal idx, current, line, column
        idx += 1
        column += 1
        if current == "\n":
            line += 1
            column = 0
        current = code[idx : idx+1]

    def consume():
        c = current
        advance()
        return c

    def collect_all(while_in: set[str], into: list[str] = None, max_count: int = -1):
        into = [] if into is None else into
        while current in while_in and max_count:
            max_count -= 1
            into.append(consume())
        return into

    def collect_number(while_in: set[str], into: list[str] = None):
        into = [] if into is None else into
        while current in while_in:
            collect_all(while_in, into)
            if current == "_":
                into.append(consume())
        return into

    def collect_until(until: set[str], include: bool, into: list[str] = None, max_count: int = -1):
        into = [] if into is None else into
        while current and current not in until and max_count:
            max_count -= 1
            into.append(consume())
        if include and current and max_count:
            into.append(consume())
        return into

    while True:
        make_location()
        match current:

            case "":
                make_token(TokenType.EndOfFile, current)
                break

            case c if c in CharSets.Space:
                advance()

            case c if c in CharSets.Newline:
                lexeme = "".join(collect_all(CharSets.Space | CharSets.Newline))
                lexeme.rstrip("".join(CharSets.Space))  # remove trailing spaces until \n
                make_token(TokenType.Newline, lexeme)

            case c if c in CharSets.IdentifierStart:
                lexeme = "".join(collect_all(CharSets.Identifier))
                tt = LexemeMaps.Keyword.get(lexeme, TokenType.Identifier)
                make_token(tt, lexeme)

            case c if c in CharSets.Number:
                number = collect_number(CharSets.Number)

                if number == ["0",] and current in CharSets.NumberFormat:
                    charset, tag = CharSets.BinNumber, TokenTag.BinFormat if current == "b" else CharSets.HexNumber, TokenTag.HexFormat
                    number.append(consume())
                    collect_number(charset, number)
                    if len(number) <= 2:  # only "0x" or "0b"
                        make_token(TokenType.Undefined, number, TokenTag.IncompleteFormatNumber)
                    else:
                        make_token(TokenType.Integer, number, tag)
                    continue

                if current == ".":
                    number.append(consume())
                    float_part = collect_number(CharSets.Number)
                    number.extend(float_part)
                    if float_part:
                        make_token(TokenType.Float, number)
                    else:
                        make_token(TokenType.Undefined, number, TokenTag.IncompleteFloatNumber)
                else:
                    make_token(TokenType.Integer, number)

            case "#":
                lexeme = [consume(),]
                collect_all(CharSets.Identifier, lexeme)
                tt = LexemeMaps.Compiler.get("".join(lexeme), TokenType.Undefined)
                tag = None
                if tt is TokenType.Undefined:
                    tag = TokenTag.IncompleteCompilerAction
                make_token(tt, lexeme, tag)

            case '"':
                lexeme = [consume(),]
                collect_until(CharSets.StringEnd, False, lexeme)
                if current == '"':
                    lexeme.append(consume())
                    make_token(TokenType.String, lexeme)
                else:
                    make_token(TokenType.Undefined, lexeme, TokenTag.IncompleteString)
                    if lexeme[-1] == ";":
                        make_location()
                        make_token(TokenType.Semicolon, ";")

            case "/":
                # / // /* /=
                advance()
                match current:
                    case "/":
                        # //
                        lexeme = ["/", consume(),]
                        collect_until(CharSets.Newline, False, lexeme)
                        make_token(TokenType.LineComment, lexeme)
                    case "*":
                        # /*
                        lexeme = ["/", consume(),]
                        while True:
                            collect_until(CharSets.DocCommentEnd, True, lexeme)
                            if current == "/":
                                lexeme.append(consume())
                                make_token(TokenType.DocComment, lexeme)
                                break
                    case "=":
                        # /=
                        advance()
                        make_token(TokenType.AssignDivide, "/=")
                    case _:
                        # /
                        make_token(TokenType.Divide, "/")

            case "-":
                advance()
                match current:
                    case "=":
                        advance()
                        make_token(TokenType.AssignSubtract, "-=")
                    case ">":
                        advance()
                        make_token(TokenType.ReturnArrow, "->")
                    case "-":
                        advance()
                        if current == "-":
                            advance()
                            make_token(TokenType.NotInitialized, "---")
                        else:
                            make_token(TokenType.Undefined, "--", TokenTag.IncompleteNotInitialized)
                    case _:
                        make_token(TokenType.Minus, "-")

            case "+":
                advance()
                if current == "=":
                    advance()
                    make_token(TokenType.AssignAdd, "+=")
                else:
                    make_token(TokenType.Plus, "+")

            case "*":
                advance()
                if current == "=":
                    advance()
                    make_token(TokenType.AssignMultiply, "*=")
                else:
                    make_token(TokenType.Asterisk, "*")

            case "%":
                advance()
                if current == "=":
                    advance()
                    make_token(TokenType.AssignModulo, "%=")
                else:
                    make_token(TokenType.Modulo, "%")

            case "&":
                advance()
                match current:
                    case "=":
                        advance()
                        make_token(TokenType.AssignBitAnd, "&=")
                    case "&":
                        advance()
                        if current == "=":
                            advance()
                            make_token(TokenType.AssignLogicAnd, "&&=")
                        else:
                            make_token(TokenType.LogicAnd, "&&")
                    case _:
                        make_token(TokenType.BitAnd, "&")

            case "|":
                advance()
                match current:
                    case "=":
                        advance()
                        make_token(TokenType.AssignBitOr, "|=")
                    case "|":
                        advance()
                        if current == "=":
                            advance()
                            make_token(TokenType.AssignLogicOr, "||=")
                        else:
                            make_token(TokenType.LogicOr, "||")
                    case _:
                        make_token(TokenType.BitOr, "|")

            case "^":
                advance()
                if current == "=":
                    advance()
                    make_token(TokenType.AssignBitXOr, "^=")
                else:
                    make_token(TokenType.BitXOr, "^")

            case "!":
                advance()
                if current == "=":
                    advance()
                    make_token(TokenType.CompareNotEquals, "!=")
                else:
                    make_token(TokenType.LogicNot, "!")

            case "=":
                advance()
                if current == "=":
                    advance()
                    make_token(TokenType.CompareEquals, "==")
                else:
                    make_token(TokenType.Assign, "=")

            case "<":
                # < <= << <<= <<< <<<=
                advance()
                match current:
                    case "=":
                        # <=
                        advance()
                        make_token(TokenType.CompareLessEquals, "<=")
                    case "<":
                        # << <<= <<< <<<=
                        advance()
                        match current:
                            case "=":
                                advance()
                                make_token(TokenType.AssignBitShiftLeft, "<<=")
                            case "<":
                                advance()
                                if current == "=":
                                    advance()
                                    make_token(TokenType.AssignBitRotateLeft, "<<<=")
                                else:
                                    make_token(TokenType.BitRotateLeft, "<<<")
                            case _:
                                make_token(TokenType.BitShiftLeft, "<<")
                    case _:
                        # <
                        make_token(TokenType.CompareLess, "<")

            case ">":
                # > >= >> >>= >>> >>>=
                advance()
                match current:
                    case "=":
                        # >=
                        advance()
                        make_token(TokenType.CompareGreaterEquals, ">=")
                    case ">":
                        # >> >>= >>> >>>=
                        advance()
                        match current:
                            case "=":
                                advance()
                                make_token(TokenType.AssignBitShiftRight, ">>=")
                            case ">":
                                advance()
                                if current == "=":
                                    advance()
                                    make_token(TokenType.AssignBitRotateRight, ">>>=")
                                else:
                                    make_token(TokenType.BitRotateRight, ">>>")
                            case _:
                                make_token(TokenType.BitShiftRight, ">>")
                    case _:
                        # >
                        make_token(TokenType.CompareGreater, ">")

            case _:
                tt = LexemeMaps.Literal.get(current, TokenType.Undefined)
                make_token(tt, consume())

    return LexResult(tokens)