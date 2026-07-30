import os
import shutil
import logging
from fastapi import UploadFile
from decouple import config

logger = logging.getLogger(__name__)


class FileStorageManager:
    """Menangani seluruh operasi filesystem dengan GCS fallback.
    
    Strategi Write-Through + Read-Fallback:
    - WRITE: Simpan lokal + upload ke GCS
    - READ: Cek lokal → tidak ada? → download dari GCS → simpan lokal → baca
    """

    def __init__(self):
        self.base_path = config('STORAGE_PATH', default='.')
        self.use_gcs = config('USE_GCS', default='false').lower() == 'true'
        self.bucket_name = config('GCS_BUCKET_NAME', default='')
        self._bucket = None

        if self.use_gcs and self.bucket_name:
            try:
                from google.cloud import storage
                client = storage.Client()
                self._bucket = client.bucket(self.bucket_name)
                logger.info(f"GCS initialized: bucket={self.bucket_name}")
            except Exception as e:
                logger.warning(f"GCS init failed, falling back to local only: {e}")
                self.use_gcs = False

    # ──────────────────────────────────────────────
    # GCS helper (private)
    # ──────────────────────────────────────────────
    def _upload_to_gcs(self, gcs_path: str, local_path: str) -> bool:
        """Upload file lokal ke GCS. Return True jika berhasil."""
        if not self._bucket:
            return False
        try:
            blob = self._bucket.blob(gcs_path)
            blob.upload_from_filename(local_path)
            logger.info(f"GCS upload OK: {gcs_path}")
            return True
        except Exception as e:
            logger.warning(f"GCS upload failed ({gcs_path}): {e}")
            return False

    def _upload_string_to_gcs(self, gcs_path: str, content: str, content_type: str = "text/html") -> bool:
        """Upload string content langsung ke GCS tanpa file lokal."""
        if not self._bucket:
            return False
        try:
            blob = self._bucket.blob(gcs_path)
            blob.upload_from_string(content, content_type=content_type)
            logger.info(f"GCS upload string OK: {gcs_path}")
            return True
        except Exception as e:
            logger.warning(f"GCS upload string failed ({gcs_path}): {e}")
            return False

    def _download_from_gcs(self, gcs_path: str, local_path: str) -> bool:
        """Download file dari GCS ke lokal. Return True jika berhasil."""
        if not self._bucket:
            return False
        try:
            blob = self._bucket.blob(gcs_path)
            if not blob.exists():
                return False
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            blob.download_to_filename(local_path)
            logger.info(f"GCS download OK: {gcs_path} → {local_path}")
            return True
        except Exception as e:
            logger.warning(f"GCS download failed ({gcs_path}): {e}")
            return False

    # ──────────────────────────────────────────────
    # Source Code (modules/)
    # ──────────────────────────────────────────────
    def save_uploaded_source_code(self, id_modul: str, source_code: UploadFile) -> str:
        """Simpan file .java yang diupload oleh Dosen ke /modules/ + GCS"""
        modul_dir = os.path.join(self.base_path, "modules", id_modul)

        if os.path.exists(modul_dir):
            shutil.rmtree(modul_dir)
        os.makedirs(modul_dir, exist_ok=True)

        target_file = os.path.join(modul_dir, source_code.filename)
        with open(target_file, 'wb') as f:
            shutil.copyfileobj(source_code.file, f)

        # Write-through ke GCS
        if self.use_gcs:
            gcs_path = f"modules/{id_modul}/{source_code.filename}"
            self._upload_to_gcs(gcs_path, target_file)

        return target_file

    def read_source_code_text(self, id_modul: str, filename: str) -> str:
        """Baca source code. Lokal first → GCS fallback."""
        local_path = os.path.join(self.base_path, "modules", id_modul, filename)

        # Coba baca lokal
        if os.path.exists(local_path):
            with open(local_path, 'r', encoding='utf-8') as f:
                return f.read()

        # Fallback ke GCS
        if self.use_gcs:
            gcs_path = f"modules/{id_modul}/{filename}"
            if self._download_from_gcs(gcs_path, local_path):
                with open(local_path, 'r', encoding='utf-8') as f:
                    return f.read()

        raise FileNotFoundError("Source code file tidak ditemukan di direktori.")

    def get_download_file_path(self, id_modul: str, filename: str) -> str:
        """Dapatkan path file untuk download. Lokal first → GCS fallback."""
        local_path = os.path.join(self.base_path, "modules", id_modul, filename)

        if os.path.exists(local_path):
            return local_path

        # Fallback ke GCS
        if self.use_gcs:
            gcs_path = f"modules/{id_modul}/{filename}"
            if self._download_from_gcs(gcs_path, local_path):
                return local_path

        raise FileNotFoundError("File tidak ada")

    # ──────────────────────────────────────────────
    # Static files (static/) — JaCoCo reports dll
    # ──────────────────────────────────────────────
    def save_static_content(self, relative_path: str, content: str, content_type: str = "text/html") -> str:
        """Simpan string content ke static/ lokal + GCS.
        relative_path contoh: 'student_id/topik_id/jacoco_report_test/html/default/IsVokal.java.html'
        """
        local_path = os.path.join(self.base_path, "static", relative_path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        with open(local_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Write-through ke GCS
        if self.use_gcs:
            gcs_path = f"static/{relative_path}"
            self._upload_string_to_gcs(gcs_path, content, content_type)

        return local_path

    def ensure_static_file(self, relative_path: str) -> str:
        """Pastikan static file ada di lokal. Download dari GCS jika perlu.
        Return local path jika ditemukan, raise jika tidak.
        """
        local_path = os.path.join(self.base_path, "static", relative_path)

        if os.path.exists(local_path):
            return local_path

        # Fallback ke GCS
        if self.use_gcs:
            gcs_path = f"static/{relative_path}"
            if self._download_from_gcs(gcs_path, local_path):
                return local_path

        raise FileNotFoundError(f"Static file tidak ditemukan: {relative_path}")