from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse

from app.service.queue import add_file_to_queue as add_file_to_queue_service
from app.service.queue import get_status_task as get_status_task_service
from app.service.queue import get_file as get_file_service

router = APIRouter()

@router.post('/public/report/export')
async def add_file_to_queue(file: UploadFile = File(...)) -> dict:
    return await add_file_to_queue_service(file=file)

@router.get('/public/report/get_status_task/{task_id}')
def get_status_task(task_id: str) -> dict:
    return get_status_task_service(task_id=task_id)

@router.get('/public/report/get_file/{task_id}')
def get_file(task_id: str) -> FileResponse:
    return get_file_service(task_id=task_id)

