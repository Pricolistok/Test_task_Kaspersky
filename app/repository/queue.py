import os
import queue
import uuid
from dataclasses import dataclass
from fastapi import HTTPException
from pathlib import Path

import aiofiles
from fastapi import UploadFile
from pydantic.v1 import UUID4

from app.repository.utils import ensure_directory_exists


@dataclass
class Job:
    task_id: UUID4

@dataclass
class TaskInfo:
    status: bool
    detail: str



UPLOAD_DIR = Path('data_in')
queue_files = queue.Queue()
task_store : dict[UUID4, TaskInfo] = {}


async def download_file(file: UploadFile):
    file_id = uuid.uuid4()
    ensure_directory_exists(UPLOAD_DIR)
    file_path = os.path.join(UPLOAD_DIR, f'data_in_{file_id}.txt')
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read(4096)
        while content:
            await out_file.write(content)
            content = await file.read(4096)
    return file_id


def add_file_to_queue(task_id: UUID4):
    node = Job(task_id=task_id)
    task_store[task_id] = TaskInfo(status=False, detail='In queue')
    queue_files.put(node)


def get_status_task(task_id: UUID4):
    if task_id in task_store:
        return {
            'status': task_store[task_id].status,
            'detail': task_store[task_id].detail
        }
    raise HTTPException(status_code=404, detail='Task_id not found')
