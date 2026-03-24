from fastapi import APIRouter, File, UploadFile
from app.service.wordforms import analysis_wordforms

router = APIRouter()

@router.post('/public/report/export')
def wordforms(file: UploadFile = File(...)):
    return analysis_wordforms(file=file)