import py_compile
from pathlib import Path


def test_numbered_root_lessons_compile() -> None:
    root = Path(__file__).parents[1]
    lessons = sorted(root.glob("[0-9][0-9]_*.py"))
    assert [path.name[:2] for path in lessons] == ["01", "02", "03", "04", "05"]
    for lesson in lessons:
        py_compile.compile(str(lesson), doraise=True)
