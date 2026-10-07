"""App scaffolding, source preservation, and failure recovery contracts."""

from __future__ import annotations

import codecs
from pathlib import Path

import pytest

from boltra.apps import AppError, add_app
from boltra.apps.registration import register_router
from boltra.apps.validation import validate_app_name
from boltra.cli import execute, parse_argv
from boltra.project import create_project


@pytest.fixture
def project(tmp_path: Path) -> Path:
    """Use the real four-file project so tests cover the public workflow."""
    return create_project("school", cwd=tmp_path)


def test_add_registers_and_preserves_user_code(project: Path) -> None:
    main = project / "main.py"
    original = main.read_text(encoding="utf-8")
    settings_source = (project / "settings.py").read_bytes()
    main.write_text(original + "\n# Keep my custom endpoint.\n", encoding="utf-8")
    directory = add_app("students", cwd=project)
    assert directory == project / "apps" / "students"
    assert (directory / "__init__.py").is_file()
    assert 'prefix="/students"' in (directory / "router.py").read_text()
    source = main.read_text(encoding="utf-8")
    assert (
        "from apps.students.router import router as _boltra_students_router" in source
    )
    assert "app.include_router(_boltra_students_router)" in source
    assert "# Keep my custom endpoint." in source
    assert (project / "settings.py").read_bytes() == settings_source


def test_add_from_subdirectory_and_multiple_apps(project: Path) -> None:
    nested = project / "backend"
    nested.mkdir()
    for name in ("students", "courses", "teachers"):
        add_app(name, cwd=nested)
    source = (project / "main.py").read_text()
    for name in ("students", "courses", "teachers"):
        assert source.count(f"app.include_router(_boltra_{name}_router)") == 1


@pytest.mark.parametrize(
    "name",
    [
        "",
        "Students",
        "1bad",
        "bad-name",
        "../bad",
        "student\n",
        "école",
        "class",
        "con",
        "com1",
        "lpt9",
        "match",
        "__init__",
    ],
)
def test_invalid_names_do_not_mutate(project: Path, name: str) -> None:
    original = (project / "main.py").read_bytes()
    with pytest.raises(AppError):
        add_app(name, cwd=project)
    assert not (project / "apps").exists()
    assert (project / "main.py").read_bytes() == original
    assert parse_argv(["add", "app", name]).action == "error"


def test_valid_importable_name() -> None:
    assert validate_app_name("student_records2") == "student_records2"


def test_duplicate_preserves_all_files(project: Path) -> None:
    directory = add_app("students", cwd=project)
    custom = directory / "custom.txt"
    custom.write_text("keep me")
    original = (project / "main.py").read_bytes()
    with pytest.raises(AppError, match=r"already imported|already exists"):
        add_app("students", cwd=project)
    assert custom.read_text() == "keep me"
    assert (project / "main.py").read_bytes() == original


@pytest.mark.parametrize(
    "conflict", ["apps.py", "apps", "apps/__init__.py", "apps/students"]
)
def test_conflicting_paths_are_preserved(project: Path, conflict: str) -> None:
    path = project / conflict
    path.parent.mkdir(parents=True, exist_ok=True)
    if conflict.endswith("__init__.py"):
        path.mkdir()
    else:
        path.write_text("unrelated")
    with pytest.raises(AppError):
        add_app("students", cwd=project)
    assert path.exists()


def test_existing_package_initializer_is_preserved(project: Path) -> None:
    apps = project / "apps"
    apps.mkdir()
    initializer = apps / "__init__.py"
    initializer.write_text("# user-owned package\n")
    add_app("students", cwd=project)
    assert initializer.read_text() == "# user-owned package\n"


def test_packaged_module_and_custom_attribute(project: Path) -> None:
    backend = project / "backend"
    backend.mkdir()
    (backend / "__init__.py").touch()
    main = backend / "api.py"
    main.write_text("import fastapi as api\napplication: api.FastAPI = api.FastAPI()\n")
    config = project / "pyproject.toml"
    config.write_text(config.read_text().replace("main:app", "backend.api:application"))
    add_app("students", cwd=project)
    assert "application.include_router(_boltra_students_router)" in main.read_text()


@pytest.mark.parametrize(
    "source",
    [
        "app = make_app()\n",
        "from fastapi import FastAPI\napp = FastAPI()\napp = other\n",
        "def create():\n    return None\n",
        "invalid Python!\n",
        "from fastapi import FastAPI\napp = FastAPI(); app.run()\n",
    ],
)
def test_unsupported_app_source_fails_before_writes(project: Path, source: str) -> None:
    main = project / "main.py"
    main.write_text(source)
    with pytest.raises(AppError):
        add_app("students", cwd=project)
    assert not (project / "apps").exists()
    assert main.read_text() == source


def test_source_is_never_executed(project: Path) -> None:
    main = project / "main.py"
    main.write_text(main.read_text() + "\nraise RuntimeError('do not execute')\n")
    add_app("students", cwd=project)


def test_bom_crlf_comments_and_main_guard_preserved() -> None:
    original = codecs.BOM_UTF8 + (
        b'"""My application."""\r\n'
        b"from __future__ import annotations\r\n"
        b"from fastapi import FastAPI as API\r\n"
        b"# custom constructor comment\r\n"
        b"app = API(\r\n    title='School',\r\n)\r\n"
        b"if __name__ == '__main__':\r\n    run_server()"
    )
    result = register_router(original, "students", "app")
    assert result.startswith(codecs.BOM_UTF8)
    assert b"\n" not in result.replace(b"\r\n", b"")
    assert b"# custom constructor comment\r\n" in result
    assert result.index(b"include_router") < result.index(b"if __name__")
    assert result.index(b"from __future__") < result.index(b"from apps.students")


def test_unicode_string_separator_is_not_a_source_line() -> None:
    original = (
        'from fastapi import FastAPI\nlabel = "first\u2028second"\napp = FastAPI()\n'
    )
    result = register_router(original.encode(), "students", "app").decode()
    assert 'label = "first\u2028second"\n' in result
    assert result.index("app = FastAPI()") < result.index("app.include_router")


@pytest.mark.parametrize(
    "extra",
    [
        "from apps.students.router import router\n",
        "_boltra_students_router = None\n",
        "import other as _boltra_students_router\n",
    ],
)
def test_registration_conflicts(extra: str) -> None:
    source = "from fastapi import FastAPI\napp = FastAPI()\n" + extra
    with pytest.raises(ValueError, match="already"):
        register_router(source.encode(), "students", "app")


def test_nested_attribute_is_not_supported(project: Path) -> None:
    config = project / "pyproject.toml"
    config.write_text(config.read_text().replace("main:app", "main:container.app"))
    with pytest.raises(AppError, match="top-level"):
        add_app("students", cwd=project)


@pytest.mark.parametrize("existing_apps", [False, True])
def test_atomic_replace_failure_rolls_back(
    project: Path, monkeypatch: pytest.MonkeyPatch, existing_apps: bool
) -> None:
    import boltra.apps.generator as generator

    original = (project / "main.py").read_bytes()
    apps = project / "apps"
    if existing_apps:
        apps.mkdir()
        (apps / "keep.txt").write_text("keep")

    def fail_replace(*args: object) -> None:
        raise PermissionError("source locked")

    monkeypatch.setattr(generator.os, "replace", fail_replace)
    with pytest.raises(AppError, match="source locked"):
        add_app("students", cwd=project)
    assert (project / "main.py").read_bytes() == original
    assert not (apps / "students").exists()
    assert not (apps / "__init__.py").exists()
    assert not list(project.glob("tmp*"))
    if existing_apps:
        assert (apps / "keep.txt").read_text() == "keep"
    else:
        assert not apps.exists()


def test_partial_write_failure_rolls_back(
    project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_open = Path.open
    original_main = (project / "main.py").read_bytes()

    def fail_router(path: Path, *args: object, **kwargs: object) -> object:
        if path.name == "router.py" and args == ("x",):
            raise OSError("disk full")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fail_router)
    with pytest.raises(AppError, match="disk full"):
        add_app("students", cwd=project)
    assert not (project / "apps").exists()
    assert (project / "main.py").read_bytes() == original_main


def test_editor_change_is_preserved(
    project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    main = project / "main.py"
    original_read = Path.read_bytes
    reads = 0

    def concurrent_read(path: Path) -> bytes:
        nonlocal reads
        if path == main:
            reads += 1
            if reads == 2:
                main.write_text("# edited concurrently\n")
        return original_read(path)

    monkeypatch.setattr(Path, "read_bytes", concurrent_read)
    with pytest.raises(AppError, match="source changed"):
        add_app("students", cwd=project)
    assert main.read_text() == "# edited concurrently\n"
    assert not (project / "apps").exists()


def test_missing_project_and_source(tmp_path: Path, project: Path) -> None:
    with pytest.raises(AppError, match="not in a Boltra project"):
        add_app("students", cwd=tmp_path)
    (project / "main.py").unlink()
    with pytest.raises(AppError):
        add_app("students", cwd=project)


def test_linked_apps_are_rejected(project: Path, tmp_path: Path) -> None:
    external = tmp_path / "external"
    external.mkdir()
    try:
        (project / "apps").symlink_to(external, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation is unavailable")
    with pytest.raises(AppError, match=r"inside|linked"):
        add_app("students", cwd=project)
    assert not list(external.iterdir())


def test_cli_add_success_and_duplicate(
    project: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert execute(["add", "app", "students"], cwd=project) == 0
    assert "Registered endpoint: /students/" in capsys.readouterr().out
    assert execute(["add", "app", "students"], cwd=project) == 1
    output = capsys.readouterr()
    assert not output.out
    assert output.err.count("error:") == 1


@pytest.mark.parametrize(
    "args", [["add"], ["add", "app"], ["add", "unknown"], ["add", "app", "x", "extra"]]
)
def test_add_usage_errors(args: list[str], capsys: pytest.CaptureFixture[str]) -> None:
    assert execute(args) == 2
    assert capsys.readouterr().err.count("error:") == 1


@pytest.mark.parametrize("args", [["add", "--help"], ["add", "app", "--help"]])
def test_add_help_once(args: list[str], capsys: pytest.CaptureFixture[str]) -> None:
    assert execute(args) == 0
    output = capsys.readouterr()
    assert output.out.count("usage:") == 1
    assert not output.err
