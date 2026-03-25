from threading import Thread
from app.repository.wordforms import OUTPUT_DIR, worker as worker_repo
from app.repository.utils import delete_dir
from app.repository.queue import UPLOAD_DIR


def worker() -> None:
    worker_repo()


def start_worker() -> None:
    thread = Thread(target=worker, daemon=True)
    thread.start()


def delete_dirs() -> None:
    delete_dir(OUTPUT_DIR)
    delete_dir(UPLOAD_DIR)
