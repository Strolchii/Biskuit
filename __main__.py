
from .info import SourceCode
from .lexer import tokenize
from .parser import build_ast  # type: ignore shadowedImport(stdlib.parser)
from .walker import check_type


def main(filepath: str):
    code = SourceCode(filepath, None)
    with open(filepath, "rt", encoding="utf-8") as f:
        code.text = f.read()

    lex_result = tokenize(code)
    #if __debug__:
    #    for t in lex_result.tokens:
    #        print(t)
    #    print()

    parse_result = build_ast(lex_result)
    print(parse_result)

    #type_result = check_type(parse_result.ast)

main("biskuit/test.bs")