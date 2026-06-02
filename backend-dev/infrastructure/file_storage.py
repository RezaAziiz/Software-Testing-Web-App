import os
import shutil
from distutils.dir_util import copy_tree, remove_tree
from fastapi import UploadFile
import logging

logger = logging.getLogger(__name__)

class FileStorageManager:
    """Menangani seluruh operasi filesystem (Create, Copy, Remove folder/file)."""
    
    def save_uploaded_source_code(self, id_modul: str, source_code: UploadFile) -> str:
        """Simpan file .java yang diupload oleh Dosen ke /modules/"""
        modul_dir = os.path.join("modules", id_modul)
        
        if os.path.exists(modul_dir):
            remove_tree(modul_dir)
        os.makedirs(modul_dir, exist_ok=True)
        
        target_file = os.path.join(modul_dir, source_code.filename)
        with open(target_file, 'wb') as f:
            shutil.copyfileobj(source_code.file, f)
            
        return target_file

    def setup_test_workspace(self, workspace_path: str, source_file_path: str, source_filename: str) -> str:
        """Menyiapkan folder engine-testing untuk eksekusi Gradle Test"""
        os.makedirs("engine-testing", exist_ok=True)
        os.makedirs(workspace_path, exist_ok=True)
        
        copy_tree("jacoco-engine", workspace_path)
        
        src_java_dir = os.path.join(workspace_path, "src", "main", "java")
        os.makedirs(src_java_dir, exist_ok=True)
        
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
        
        # Fungsi pembantu untuk copy secara aman
        def safe_copy(src_subpath, dest_dir_name):
            src = os.path.join(workspace_path, src_subpath)
            dst = os.path.join(static_dir, dest_dir_name)
            if os.path.exists(src):
                copy_tree(src, dst)

        try:
            safe_copy(os.path.join("build", "reports", "tests", "test"), "report_test")
            safe_copy(os.path.join("build", "test-results", "test"), "test-results")
            safe_copy(os.path.join("build", "reports", "jacoco", "test"), "jacoco_report_test")
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
        except Exception as e:
            logger.warning(f"Failed to copy initial module reports: {str(e)}")

    def cleanup_workspace(self, workspace_path: str) -> None:
        """Menghapus folder sementara engine-testing"""
        try:
            if os.path.exists(workspace_path):
                remove_tree(workspace_path)
        except Exception as e:
            logger.warning(f"Cleanup workspace {workspace_path} failed: {str(e)}")