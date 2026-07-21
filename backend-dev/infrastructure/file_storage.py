import filecmp
import os
import shutil
from distutils.dir_util import copy_tree, remove_tree
from fastapi import UploadFile
from decouple import config
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)

class FileStorageManager:
    """Menangani seluruh operasi filesystem (Create, Copy, Remove folder/file).
    Mendukung konfigurasi STORAGE_PATH untuk fleksibilitas Volume Mount (GCS FUSE / Docker Volume).
    """

    def __init__(self):
        # Gunakan direktori saat ini jika STORAGE_PATH tidak di-set
        self.base_path = config('STORAGE_PATH', default='.')

    def save_uploaded_source_code(self, id_modul: str, source_code: UploadFile) -> str:
        """Simpan file .java yang diupload oleh Dosen ke /modules/"""
        modul_dir = os.path.join(self.base_path, "modules", id_modul)
        
        if os.path.exists(modul_dir):
            remove_tree(modul_dir)
        os.makedirs(modul_dir, exist_ok=True)
        
        target_file = os.path.join(modul_dir, source_code.filename)
        with open(target_file, 'wb') as f:
            shutil.copyfileobj(source_code.file, f)

        return target_file

    def read_source_code_text(self, id_modul: str, filename: str) -> str:
        local_path = os.path.join(self.base_path, "modules", id_modul, filename)
        if not os.path.exists(local_path):
            raise FileNotFoundError("Source code file tidak ditemukan di direktori.")
        with open(local_path, 'r', encoding='utf-8') as f:
            return f.read()

    def get_download_file_path(self, id_modul: str, filename: str) -> str:
        local_path = os.path.join(self.base_path, "modules", id_modul, filename)
        if os.path.exists(local_path):
            return local_path
        raise FileNotFoundError("File tidak ada")