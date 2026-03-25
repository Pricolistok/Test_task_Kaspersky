from fastapi import APIRouter, File, UploadFile
from app.service.queue import add_file_to_queue as add_file_to_queue_service
from app.service.queue import get_status_task as get_status_task_service

router = APIRouter()

@router.post('/public/report/export')
async def add_file_to_queue(file: UploadFile = File(...)):
    return await add_file_to_queue_service(file=file)

@router.post('/public/report/get_status_task')
def get_status_task(task_id: str):
    return get_status_task_service(task_id=task_id)

