from app.repository.wordforms import analysis_wordforms as analysis_wordforms_repo
from app.repository.wordforms import create_table, checker_format_file
from fastapi import UploadFile, HTTPException

def analysis_wordforms(file: UploadFile):
    if not checker_format_file(file):
        raise HTTPException(status_code=400, detail='File format is not supported')
    stats = analysis_wordforms_repo(file=file)
    create_table(stats=stats)


