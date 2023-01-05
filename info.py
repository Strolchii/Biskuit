from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SourceCode():
    name: str
    text: str

    def __getitem__(self, index):
        return self.text[index]

    def __len__(self):
        return len(self.text)


@dataclass(slots=True)
class SourceLocation():
    line: int
    column: int

    def __lt__(self, other: SourceLocation):
        if self.line < other.line:
            return True
        if self.line == other.line and self.column < other.column:
            return True
        return False


@dataclass(slots=True)
class SourceRange():
    start: SourceLocation
    end: SourceLocation

    def expand(self, range: SourceRange):
        assert self.start is min(self.start, range.start)
        self.end = max(self.end, range.end)
        return self

    def to_shrink_to_end(self):
        return SourceRange(self.end, self.end)

    def to_shrink_to_start(self):
        return SourceRange(self.start, self.start)

    @classmethod
    def zero(cls):
        return cls(SourceLocation(0,0), SourceLocation(0,0))