
from dataclasses import dataclass
from enum import Enum, auto
from collections import namedtuple

from .tokens import TokenType, Token
from .lexer import LexResult
from .nodes import NodeType, Node
from .info import SourceRange

class DiagnosticType(Enum):
    MissingSemicolon = auto()
    GlobalNotAllowed = auto()
    ImportExpectedString = auto()
    DefinitionExpectedColon = auto()
    TypeNotAllowed = auto()
    ParameterExpectedName = auto()

@dataclass
class Diagnostic():
    type: DiagnosticType
    range: SourceRange

@dataclass(slots=True)
class ParseResult():
    ast: Node
    diagnostics: list[Diagnostic]


def build_ast(lex_result: LexResult):
    tokens = lex_result.tokens

    diagnostics: list[Diagnostic] = []  # https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#diagnostic
    idx = -1
    current: Token = None
    doc_comment: str = ""


    def match(*tt: TokenType):
        return current.type in tt

    def advance():
        nonlocal idx, current, doc_comment
        newlines = 0
        maybe_doc = None
        while True:
            idx += 1
            current = tokens[idx]
            match current.type:
                case TokenType.Newline:
                    newlines += current.lexeme.count("\n")
                case TokenType.LineComment:
                    doc_comment = ""
                case TokenType.DocComment:
                    maybe_doc = current.lexeme
                    newlines = 0
                case TokenType.Identifier:
                    doc_comment = maybe_doc if newlines <= 1 else ""
                    break
                case _:
                    doc_comment = ""
                    break
    advance()

    def consume():
        t = current
        advance()
        return t

    def consume_if(*tt: TokenType):
        if match(*tt):
            return consume()
        return None

    def advance_until(*tt: TokenType):
        while not match(*tt):
            advance()

    def add_diagnostic(type: DiagnosticType, range: SourceRange):
        diagnostics.append(Diagnostic(type, range))


    def expect_semicolon(range: SourceRange):
        sem = consume_if(TokenType.Semicolon)
        if sem:
            range.expand(sem.to_range())
        else:
            add_diagnostic(DiagnosticType.MissingSemicolon, range.to_shrink_to_end())


    def parse_module():
        module_node = Node(NodeType.Module, SourceRange.zero())
        while not match(TokenType.EndOfFile):
            node = switch_global()
            if node.type is NodeType.Error:
                # error already reported and advanced
                advance_until(TokenType.Identifier, TokenType.Import)
            else:
                module_node.data.globals.append(node)
        module_node.range.expand(current.to_range())
        return module_node

    def switch_global():
        match current.type:
            case TokenType.Import:
                return parse_import()
            case TokenType.Identifier:
                return parse_definition()
            case _:
                add_diagnostic(DiagnosticType.GlobalNotAllowed, current.to_range())
                err = Node(NodeType.Error, current.to_range())
                err.data.diagnostic = DiagnosticType.GlobalNotAllowed
                return err


    def parse_import():
        import_tok = consume()
        import_node = Node(NodeType.Import, import_tok.to_range())

        path_tok = consume_if(TokenType.String)
        if path_tok:
            import_node.range.expand(path_tok.to_range())
            import_node.data.path = path_tok.lexeme
        else:
            import_node.data.path = ""
            add_diagnostic(DiagnosticType.ImportExpectedString, import_node.range)

        expect_semicolon(import_node.range)
        return import_node

    def parse_definition():
        # this could be: constant or variable
        doc_str = doc_comment
        name_tok = consume()

        colon = consume_if(TokenType.Colon)
        if not colon:
            add_diagnostic(DiagnosticType.DefinitionExpectedColon, name_tok.to_range())
            err = Node(NodeType.Error, current.to_range())
            err.data.diagnostic = DiagnosticType.DefinitionExpectedColon
            return err

        match current.type:
            case TokenType.Colon:
                advance()
                alias_node = Node(NodeType.Alias, name_tok.to_range().expand(current.to_range()))
                alias_node.data.doc = doc_str
                alias_node.data.name = name_tok.lexeme
                val = parse_alias_value()
                alias_node.range.expand(val.range)
                alias_node.data.value = val
                return alias_node
            case TokenType.Assign:
                advance()
                def_node = Node(NodeType.Definition, name_tok.to_range().expand(current.to_range()))
                def_node.data.doc = doc_str
                def_node.data.name = name_tok.lexeme
                val = parse_value()
                def_node.range.expand(val.range)
                def_node.data.value = val
                return def_node
            case _:
                def_node = Node(NodeType.Definition, name_tok.to_range().expand(colon.to_range()))
                def_node.data.doc = doc_str
                def_node.data.name = name_tok.lexeme
                type_ = parse_type()
                def_node.range.expand(type_.range)
                def_node.data.type = type_
                match current.type:
                    case TokenType.Semicolon:
                        advance()
                    case TokenType.Assign:
                        advance()
                        val = parse_value()
                        def_node.range.expand(val.range)
                        def_node.data.value = val
                        expect_semicolon(def_node.range)
                    case _:
                        expect_semicolon(def_node.range)  # shorter code for missing semicolon
                return def_node

    def parse_type():
        match current.type:
            case TokenType.OpenParenthesis:
                return parse_type_function()
            case TokenType.Identifier:
                ident_tok = consume()
                node = Node(NodeType.NamedType, ident_tok.to_range())
                node.data.name = ident_tok.lexeme
                return node
            case TokenType.Enumeration:
                return parse_enum()
            case TokenType.Structure:
                return parse_struct()
            case _:
                range = current.to_range()
                add_diagnostic(DiagnosticType.TypeNotAllowed, range)
                node = Node(NodeType.Error, range)
                node.data.diagnostic = DiagnosticType.TypeNotAllowed
                return node

    def parse_type_function():
        pass

    def parse_alias_value():
        return Node()

    def parse_value():
        return Node()


    return ParseResult(parse_module(), diagnostics)