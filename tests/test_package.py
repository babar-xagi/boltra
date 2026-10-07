"""Verify pure Python distribution contents and installed-package behavior."""

from __future__ import annotations

import subprocess
import sys
import tarfile
from pathlib import Path
from zipfile import ZipFile

import pytest

from boltra import __version__

pytestmark = pytest.mark.packaging
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def distributions(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build both release formats once for the packaging tests."""
    destination = tmp_path_factory.mktemp("distributions")
    result = subprocess.run(
        ["uv", "build", "--out-dir", str(destination)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return destination


def test_wheel_is_pure_python_and_has_templates(distributions: Path) -> None:
    """Every platform uses the same wheel, including all generator resources."""
    wheel = next(distributions.glob("*.whl"))
    assert wheel.name == f"boltra-{__version__}-py3-none-any.whl"
    with ZipFile(wheel) as archive:
        names = archive.namelist()
        assert "boltra/py.typed" in names
        assert "boltra/cli/cli.py" in names
        assert "boltra/dev/windows.py" in names
        for asset in ["main.py", "settings.py", "pyproject.toml", "env.example"]:
            assert f"boltra/project/templates/{asset}.tmpl" in names
        assert not any(name.endswith((".pyd", ".so", ".dll", ".rs")) for name in names)
        metadata = archive.read(f"boltra-{__version__}.dist-info/WHEEL").decode()
        assert "Root-Is-Purelib: true" in metadata
        entrypoints = archive.read(
            f"boltra-{__version__}.dist-info/entry_points.txt"
        ).decode()
        assert "boltra = boltra.cli.cli:run" in entrypoints


def test_source_distribution_is_clean(distributions: Path) -> None:
    """Source archives exclude old native source and local development caches."""
    with tarfile.open(next(distributions.glob("*.tar.gz"))) as archive:
        names = archive.getnames()
    assert any(name.endswith("/README.md") for name in names)
    for name in names:
        assert not (
            {".uv", ".venv", "target", "crates", ".cargo"} & set(Path(name).parts)
        )
        assert not name.endswith(("Cargo.toml", "Cargo.lock", ".pyd", ".rs"))


def test_installed_wheel_cli_and_templates(distributions: Path, tmp_path: Path) -> None:
    """A fresh environment can use the CLI and scaffold without app dependencies."""
    environment = tmp_path / "isolated"
    subprocess.run(
        ["uv", "venv", "--python", sys.executable, str(environment)],
        check=True,
        capture_output=True,
    )
    bin_dir = environment / ("Scripts" if sys.platform == "win32" else "bin")
    python = bin_dir / ("python.exe" if sys.platform == "win32" else "python")
    subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--python",
            str(python),
            "--no-deps",
            "--no-index",
            str(next(distributions.glob("*.whl"))),
        ],
        check=True,
        capture_output=True,
    )
    # Isolated mode and a different working directory rule out source-tree imports.
    result = subprocess.run(
        [str(python), "-I", "-m", "boltra", "--version"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == __version__
    cli = bin_dir / ("boltra.exe" if sys.platform == "win32" else "boltra")
    result = subprocess.run(
        [str(cli), "new", "sample"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Created project 'sample'" in result.stdout
    for filename in ["main.py", "settings.py", "pyproject.toml", ".env.example"]:
        assert (tmp_path / "sample" / filename).is_file()
    # The removed native helpers are not imported by the public package.
    subprocess.run(
        [
            str(python),
            "-I",
            "-c",
            "import boltra, importlib.util; "
            "assert importlib.util.find_spec('boltra._native') is None",
        ],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
