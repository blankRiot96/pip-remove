from src.pip_remove.orphans import get_orphans_of_package, get_orphans

from .conftest import VENV_PYTHON_PATH, TEMP_DIR


def test_all_orphans():
    assert set(get_orphans_of_package("flask", VENV_PYTHON_PATH)) == {
        "blinker",
        "click",
        "itsdangerous",
        "Jinja2",
        "MarkupSafe",
        "Werkzeug",
    }


def test_unused_orphans():
    assert get_orphans("flask", VENV_PYTHON_PATH, TEMP_DIR)[1] == {
        "blinker",
        "itsdangerous",
        "Jinja2",
        "MarkupSafe",
        "Werkzeug",
    }
