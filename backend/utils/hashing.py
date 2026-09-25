import hashlib


def calculate_file_hash(
    file_path: str
) -> str | None:

    sha256 = hashlib.sha256()

    try:

        with open(
            file_path,
            "rb"
        ) as file:

            while chunk := file.read(
                1024 * 1024
            ):

                sha256.update(chunk)

        return sha256.hexdigest()

    except (
        OSError,
        PermissionError
    ):

        return None