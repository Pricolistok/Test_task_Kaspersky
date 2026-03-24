from app.repository.wordforms import analyze_wordforms_in_file
from app.repository.wordforms import create_excel_table, validate_file
from fastapi import UploadFile

def analysis_wordforms(file: UploadFile) -> dict[str, str]:
    validate_file(file)
    stats, cnt_rows = analyze_wordforms_in_file(file=file)
    file_name = create_excel_table(stats=stats, cnt_rows=cnt_rows)
    return {
        'filename': file_name,
    }


