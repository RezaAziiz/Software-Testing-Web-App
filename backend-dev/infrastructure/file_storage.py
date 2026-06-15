import os
import shutil
from distutils.dir_util import copy_tree, remove_tree
from fastapi import UploadFile
from decouple import config
from google.cloud import storage
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

class FileStorageManager:
    """Menangani seluruh operasi filesystem (Create, Copy, Remove folder/file) dan sinkronisasi GCS."""

    def __init__(self):
        self.bucket_name = config('GCS_BUCKET_NAME', default='software-testing-uat-db-init')
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(self.bucket_name)

    def _upload_file_to_gcs(self, local_path: str, blob_path: str) -> None:
        blob = self.bucket.blob(blob_path)
        blob.upload_from_filename(local_path)

    def _upload_directory_to_gcs(self, local_dir: str, blob_root: str) -> None:
        if not os.path.exists(local_dir):
            return
        for root, _, files in os.walk(local_dir):
            for filename in files:
                local_file = os.path.join(root, filename)
                relative_path = os.path.relpath(local_file, local_dir)
                blob_path = os.path.join(blob_root, relative_path).replace('\\', '/')
                self._upload_file_to_gcs(local_file, blob_path)

    def _download_blob_to_file(self, blob_path: str, local_path: str) -> bool:
        blob = self.bucket.blob(blob_path)
        if not blob.exists():
            return False
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        blob.download_to_filename(local_path)
        return True

    def _ensure_local_file(self, local_path: str, blob_path: str) -> bool:
        if os.path.exists(local_path):
            return True
        return self._download_blob_to_file(blob_path, local_path)

    def save_uploaded_source_code(self, id_modul: str, source_code: UploadFile) -> str:
        """Simpan file .java yang diupload oleh Dosen ke /modules/ dan GCS."""
        modul_dir = os.path.join("modules", id_modul)
        
        if os.path.exists(modul_dir):
            remove_tree(modul_dir)
        os.makedirs(modul_dir, exist_ok=True)
        
        target_file = os.path.join(modul_dir, source_code.filename)
        with open(target_file, 'wb') as f:
            shutil.copyfileobj(source_code.file, f)

        blob_path = f"modules/{id_modul}/{source_code.filename}"
        self._upload_file_to_gcs(target_file, blob_path)
        return target_file

    def setup_test_workspace(self, workspace_path: str, source_file_path: str, source_filename: str) -> str:
        """Menyiapkan folder engine-testing untuk eksekusi Gradle Test"""
        os.makedirs("engine-testing", exist_ok=True)
        os.makedirs(workspace_path, exist_ok=True)
        
        copy_tree("jacoco-engine", workspace_path)
        
        src_java_dir = os.path.join(workspace_path, "src", "main", "java")
        os.makedirs(src_java_dir, exist_ok=True)

        if not os.path.exists(source_file_path):
            self._ensure_local_file(source_file_path, source_file_path.replace('\\', '/'))

        shutil.copyfile(source_file_path, os.path.join(src_java_dir, source_filename))
        
        # Kembalikan path tujuan tempat TestCodeGenerator harus menaruh file
        return os.path.join(workspace_path, "src", "test", "java")

    def copy_reports_to_static(self, workspace_path: str, user_id: str, topik_modul_id: str) -> None:
        """Menyalin report HTML Gradle/JaCoCo ke folder static Mahasiswa setelah eksekusi UC-03"""
        static_dir = os.path.join("static", user_id, topik_modul_id)
        
        if os.path.exists(static_dir):
            remove_tree(static_dir)
        
        os.makedirs(os.path.join(static_dir, "report_test"), exist_ok=True)
        os.makedirs(os.path.join(static_dir, "jacoco_report_test"), exist_ok=True)
        
        def safe_copy(src_subpath, dest_dir_name):
            src = os.path.join(workspace_path, src_subpath)
            dst = os.path.join(static_dir, dest_dir_name)
            if os.path.exists(src):
                copy_tree(src, dst)

        try:
            safe_copy(os.path.join("build", "reports", "tests", "test"), "report_test")
            safe_copy(os.path.join("build", "test-results", "test"), "test-results")
            safe_copy(os.path.join("build", "reports", "jacoco", "test"), "jacoco_report_test")
            self._upload_directory_to_gcs(static_dir, f"static/{user_id}/{topik_modul_id}")
        except Exception as e:
            logger.warning(f"Could not copy some test reports: {str(e)}")

    def copy_reports_to_module(self, workspace_path: str, id_modul: str) -> None:
        """Menyalin report saat Dosen pertama kali upload modul (UC-01)"""
        modul_dir = os.path.join("modules", id_modul)
        
        os.makedirs(os.path.join(modul_dir, "report_test"), exist_ok=True)
        os.makedirs(os.path.join(modul_dir, "jacoco_report_test"), exist_ok=True)
        
        def safe_copy(src_subpath, dest_dir_name):
            src = os.path.join(workspace_path, src_subpath)
            dst = os.path.join(modul_dir, dest_dir_name)
            if os.path.exists(src):
                copy_tree(src, dst)

        try:
            safe_copy(os.path.join("build", "reports", "tests", "test"), "report_test")
            safe_copy(os.path.join("build", "test-results", "test"), "test-results")
            safe_copy(os.path.join("build", "reports", "jacoco", "test"), "jacoco_report_test")
            self._upload_directory_to_gcs(modul_dir, f"modules/{id_modul}")
        except Exception as e:
            logger.warning(f"Failed to copy initial module reports: {str(e)}")

    def read_source_code_text(self, id_modul: str, filename: str) -> str:
        local_path = os.path.join("modules", id_modul, filename)
        blob_path = f"modules/{id_modul}/{filename}"
        if not self._ensure_local_file(local_path, blob_path):
            raise FileNotFoundError("Source code file tidak ditemukan di local atau bucket.")
        with open(local_path, 'r', encoding='utf-8') as f:
            return f.read()

    def get_download_file_path(self, id_modul: str, filename: str) -> str:
        local_path = os.path.join("modules", id_modul, filename)
        blob_path = f"modules/{id_modul}/{filename}"
        if self._ensure_local_file(local_path, blob_path):
            return local_path
        raise FileNotFoundError("File tidak ada")

    def cleanup_workspace(self, workspace_path: str) -> None:
        """Menghapus folder sementara engine-testing"""
        try:
            if os.path.exists(workspace_path):
                remove_tree(workspace_path)
        except Exception as e:
            logger.warning(f"Cleanup workspace {workspace_path} failed: {str(e)}")