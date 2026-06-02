from pathlib import Path
from modules_package.modules import path  # pyright: ignore[reportMissingImports]


def test_path():
    """
    Verify that the path helper returns a valid existing directory.
    """

    data_dir = path()

    assert isinstance(
        data_dir, Path
    ), "path() must return a pathlib.Path object"

    assert data_dir.exists(), (
        f"Directory does not exist: {data_dir}"
    )

    assert data_dir.is_dir(), (
        f"Path is not a directory: {data_dir}"
    )