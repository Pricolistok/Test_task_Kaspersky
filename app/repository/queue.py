import queue
from datetime import datetime
from uuid import UUID, uuid4
from dataclasses import dataclass
from fastapi import HTTPException

import aiofiles
from fastapi import UploadFile
from fastapi.responses import FileResponse

from app.repository.utils import ensure_directory_exists, UPLOAD_DIR, OUTPUT_DIR


@dataclass
class Job:
    task_id: UUID

@dataclass
class TaskInfo:
    status: str
    last_update: str
    detail: str | None = None

queue_files = queue.Queue(maxsize=25)
task_store : dict[UUID, TaskInfo] = {}


async def download_file(file: UploadFile) -> UUID:
    file_id = uuid4()
    ensure_directory_exists(UPLOAD_DIR)
    file_path = UPLOAD_DIR / f'data_in_{file_id}.txt'
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read(4096)
        while content:
            await out_file.write(content)
            content = await file.read(4096)
    return file_id


def add_file_to_queue(task_id: UUID) -> None:
    node = Job(task_id=task_id)
    task_store[task_id] = TaskInfo(
        status='queued',
        last_update=datetime.now().isoformat(),
        detail='Task added to queue'
    )
    try:
        queue_files.put_nowait(node)
    except queue.Full:
        task_store.pop(task_id, None)
        raise HTTPException(
            status_code=503,
            detail='Server is busy. Try again later.'
        )


def get_status_task(task_id: UUID) -> dict:
    if task_id in task_store:
        return {
            'status': task_store[task_id].status,
            'detail': task_store[task_id].detail,
            'last_update': task_store[task_id].last_update
        }
    raise HTTPException(status_code=404, detail='Task_id not found')


def update_job(job: Job, status: str, detail: str | None = None) -> None:
    task_store[job.task_id].status = status
    task_store[job.task_id].last_update = datetime.now().isoformat()
    task_store[job.task_id].detail = detail


def get_file(task_id: UUID) -> FileResponse:
    if task_id not in task_store:
        raise HTTPException(status_code=404, detail='Task not found')
    if task_store[task_id].status != 'done':
        raise HTTPException(status_code=400, detail='The work is not completed, please try again later.')
    file_path = OUTPUT_DIR / f'{task_id}.xlsx'
    if not OUTPUT_DIR.exists() or not file_path.exists():
        raise HTTPException(status_code=404, detail='File not found')
    return FileResponse(
        path=file_path,
        filename=f'{task_id}.xlsx'
    )


def transform_str_to_uuid(uuid_check: str) -> UUID:
    try:
        result_uuid = UUID(uuid_check)
    except ValueError:
        raise HTTPException(status_code=400, detail='Task_id in error format')
    return result_uuid
