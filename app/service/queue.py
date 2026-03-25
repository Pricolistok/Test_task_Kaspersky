from fastapi import UploadFile, HTTPException
from pydantic import UUID4

from app.repository.queue import download_file, add_file_to_queue as add_file_to_queue_repo
from app.repository.queue import get_status_task as get_status_task_repo
from app.repository.utils import validate_file


async def add_file_to_queue(file: UploadFile):
    validate_file(file=file)
    task_id = await download_file(file=file)
    add_file_to_queue_repo(task_id=task_id)
    return {
        'task_id': task_id
    }

def get_status_task(task_id: str):
    try:
        task_id = UUID4(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail='Task_id in error format')
    return get_status_task_repo(task_id=task_id)