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
    """Menangani seluruh operasi filesystem (Create, Copy, Remove folder/file) dan sinkronisasi GCS.
    Mode ditentukan oleh env var USE_GCS:
    - USE_GCS=true  → init Google Cloud Storage, upload/download ke bucket (Cloud)
    - USE_GCS=false → pakai local filesystem saja (Local Development)
    """

    def __init__(self):
        self.use_gcs = config('USE_GCS', default='false').lower() == 'true'
        
        if self.use_gcs:
            from google.cloud import storage
            import requests
            
            self.bucket_name = config('GCS_BUCKET_NAME', default='software-testing-uat-db-init')
            self.storage_client = storage.Client()
            self.bucket = self.storage_client.bucket(self.bucket_name)
            
            # Optimasi Pool Koneksi GCS agar mendukung upload paralel skala besar
            pool_size = 64
            adapter = requests.adapters.HTTPAdapter(
                pool_connections=pool_size,
                pool_maxsize=pool_size,
                max_retries=3
            )
            # Pasang adapter ke session HTTP client GCS (baik http maupun https)
            self.storage_client._http.mount("https://", adapter)
            self.storage_client._http.mount("http://", adapter)
            if hasattr(self.storage_client._http, '_auth_request') and self.storage_client._http._auth_request:
                self.storage_client._http._auth_request.session.mount("https://", adapter)
                self.storage_client._http._auth_request.session.mount("http://", adapter)
        else:
            self.storage_client = None
            self.bucket = None

    def _upload_file_to_gcs(self, local_path: str, blob_path: str) -> None:
        if not self.use_gcs:
            return
        blob = self.bucket.blob(blob_path)
        blob.upload_from_filename(local_path)

    def _upload_directory_to_gcs(self, local_dir: str, blob_root: str) -> None:
        if not self.use_gcs:
            return
        if not os.path.exists(local_dir):
            return
        
        # Cari semua berkas yang akan diunggah
        upload_tasks = []
        for root, _, files in os.walk(local_dir):
            for filename in files:
                local_file = os.path.join(root, filename)
                relative_path = os.path.relpath(local_file, local_dir)
                blob_path = os.path.join(blob_root, relative_path).replace('\\', '/')
                upload_tasks.append((local_file, blob_path))

        # Unggah secara paralel menggunakan ThreadPoolExecutor
        if upload_tasks:
            # Gunakan 16 worker threads karena upload file ke GCS adalah I/O bound
            with ThreadPoolExecutor(max_workers=16) as executor:
                for local_file, blob_path in upload_tasks:
                    executor.submit(self._upload_file_to_gcs, local_file, blob_path)

    def _download_blob_to_file(self, blob_path: str, local_path: str) -> bool:
        if not self.use_gcs:
            return False
        blob = self.bucket.blob(blob_path)
        if not blob.exists():
            return False
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        blob.download_to_filename(local_path)
        return True

    def _ensure_local_file(self, local_path: str, blob_path: str) -> bool:
        """Pastikan file ada di local. Kalau tidak ada dan GCS aktif, coba download dari bucket."""
        if os.path.exists(local_path):
            return True
        return self._download_blob_to_file(blob_path, local_path)

    def save_uploaded_source_code(self, id_modul: str, source_code: UploadFile) -> str:
        """Simpan file .java yang diupload oleh Dosen ke /modules/ (dan GCS jika aktif)."""
        modul_dir = os.path.join("modules", id_modul)
        
        if os.path.exists(modul_dir):
            remove_tree(modul_dir)
        os.makedirs(modul_dir, exist_ok=True)
        
        target_file = os.path.join(modul_dir, source_code.filename)
        with open(target_file, 'wb') as f:
            shutil.copyfileobj(source_code.file, f)

        # Upload ke GCS jika aktif
        blob_path = f"modules/{id_modul}/{source_code.filename}"
        self._upload_file_to_gcs(target_file, blob_path)
        return target_file

    def setup_test_workspace(self, workspace_path: str, source_file_path: str, source_filename: str) -> str:
        """Menyiapkan folder engine-testing untuk eksekusi Gradle Test"""
        os.makedirs("engine-testing", exist_ok=True)
        os.makedirs(workspace_path, exist_ok=True)
        
        # Optimasi performa copy: Hanya salin berkas-berkas penting Gradle & wrapper
        # Jangan salin folder .gradle, build, lib, dll.
        essential_items = [
            "build.gradle",
            "settings.gradle",
            "gradle.properties",
            "gradlew",
            "gradlew.bat"
        ]
        for item in essential_items:
            src_path = os.path.join("jacoco-engine", item)
            dest_path = os.path.join(workspace_path, item)
            if os.path.exists(src_path):
                shutil.copy2(src_path, dest_path)

        src_gradle_dir = os.path.join("jacoco-engine", "gradle")
        dest_gradle_dir = os.path.join(workspace_path, "gradle")
        if os.path.exists(src_gradle_dir):
            copy_tree(src_gradle_dir, dest_gradle_dir)

        
        src_java_dir = os.path.join(workspace_path, "src", "main", "java")
        os.makedirs(src_java_dir, exist_ok=True)

        if not os.path.exists(source_file_path):
            self._ensure_local_file(source_file_path, source_file_path.replace('\\', '/'))

        destination_source = os.path.join(src_java_dir, source_filename)
        destination_existed = os.path.exists(destination_source)
        content_unchanged = (
            destination_existed
            and filecmp.cmp(source_file_path, destination_source, shallow=False)
        )
        mtime_before = (
            os.stat(destination_source).st_mtime_ns if destination_existed else None
        )
        shutil.copyfile(source_file_path, destination_source)
        mtime_after = os.stat(destination_source).st_mtime_ns
        logger.info(
            "[SOURCE PROFILE] Main source path=%s existed=%s content_unchanged=%s "
            "rewritten=True mtime_before_ns=%s mtime_after_ns=%s",
            destination_source,
            destination_existed,
            content_unchanged,
            mtime_before,
            mtime_after,
        )
        
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
            safe_copy(os.path.join("build", "reports", "profile"), "gradle_profile")
            safe_copy(os.path.join("reports", "profile"), "gradle_profile")
            
            # Jalankan upload GCS di background thread agar tidak memblokir respon API mahasiswa
            import threading
            upload_thread = threading.Thread(
                target=self._upload_directory_to_gcs,
                args=(static_dir, f"static/{user_id}/{topik_modul_id}")
            )
            upload_thread.daemon = True
            upload_thread.start()
            
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
            safe_copy(os.path.join("build", "reports", "profile"), "gradle_profile")
            safe_copy(os.path.join("reports", "profile"), "gradle_profile")
            # Jalankan upload GCS di background thread agar tidak memblokir respon API dosen
            import threading
            upload_thread = threading.Thread(
                target=self._upload_directory_to_gcs,
                args=(modul_dir, f"modules/{id_modul}")
            )
            upload_thread.daemon = True
            upload_thread.start()
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
        # SKIP CLEANUP (Baik di Local maupun Cloud Run)
        # Jangan hapus workspace agar cache gradle (folder build/) dan hasil kompilasi
        # tetap ada untuk mempercepat run berikutnya (incremental compilation).
        logger.info(f"Skipping workspace cleanup for {workspace_path} to reuse build caches (Workspace Cache Persistence)")
        return

        try:
            if os.path.exists(workspace_path):
                remove_tree(workspace_path)
        except Exception as e:
            logger.warning(f"Cleanup workspace {workspace_path} failed: {str(e)}")