from pathlib import Path


def path() -> Path:
    """
    Return the project's data directory.

    The directory is created automatically if it does not
    already exist.

    Returns
    -------
    Path
        Absolute path to the project's data directory.
    """

    project_root = Path(__file__).resolve().parent

    data_dir = project_root / "data"

    data_dir.mkdir(exist_ok=True)

    return data_dir