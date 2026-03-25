from fastapi import UploadFile
from fastapi.responses import FileResponse
from app.repository.queue import download_file, add_file_to_queue as add_file_to_queue_repo, transform_str_to_uuid
from app.repository.queue import get_file as get_file_repo
from app.repository.queue import get_status_task as get_status_task_repo
from app.repository.utils import validate_file


async def add_file_to_queue(file: UploadFile) -> dict:
    validate_file(file=file)
    task_id = await download_file(file=file)
    add_file_to_queue_repo(task_id=task_id)
    return {
        'task_id': str(task_id)
    }


def get_status_task(task_id: str) -> dict:
    task_id = transform_str_to_uuid(task_id)
    return get_status_task_repo(task_id=task_id)


def get_file(task_id: str) -> FileResponse:
    task_id = transform_str_to_uuid(task_id)
    return get_file_repo(task_id=task_id)
