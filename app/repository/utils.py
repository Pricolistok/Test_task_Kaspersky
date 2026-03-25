import os.path
import shutil
from pathlib import Path

from fastapi import HTTPException, UploadFile


def validate_filename(filename: str | None) -> None:
    if filename is None:
        raise HTTPException(status_code=400, detail='Invalid filename')
    if filename == '' or not filename.lower().endswith('.txt'):
        raise HTTPException(status_code=400, detail='File format is not supported')


def validate_not_empty(file: UploadFile) -> None:
    if file.file.read(1) == b"":
        file.file.seek(0)
        raise HTTPException(status_code=400, detail='File is empty')
    file.file.seek(0)

def validate_content_type(content_type: str | None) -> None:
    if content_type != 'text/plain':
        raise HTTPException(status_code=400, detail='Invalid content type file')


def validate_encoding(file: UploadFile) -> None:
    try:
        file.file.read(2048).decode('utf-8')
    except UnicodeError:
        raise HTTPException(400, "File must be UTF-8 encoded")
    finally:
        file.file.seek(0)


def validate_file(file: UploadFile) -> None:
    validate_filename(file.filename)
    validate_content_type(file.content_type)
    validate_not_empty(file)
    validate_encoding(file)


def ensure_directory_exists(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def delete_dir(dir_path: Path) -> None:
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)