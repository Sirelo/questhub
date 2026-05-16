from __future__ import annotations

import uuid
from pathlib import Path

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


def save_image(file: FileStorage, folder: str) -> str:
    filename = secure_filename(file.filename or "")
    if "." not in filename:
        raise ValueError("У файла нет расширения.")

    extension = filename.rsplit(".", 1)[1].lower()
    if extension not in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        raise ValueError("Недопустимый формат файла.")

    unique_name = f"{uuid.uuid4().hex}.{extension}"
    destination_dir = Path(current_app.config["UPLOAD_ROOT"]) / folder
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination_path = destination_dir / unique_name

    file.save(destination_path)

    return unique_name
