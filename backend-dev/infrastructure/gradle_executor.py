import os
import subprocess
import logging

logger = logging.getLogger(__name__)

class GradleExecutor:
    """Menangani eksekusi perintah Gradle via shell subprocess."""
    
    def __init__(self, gradle_command: str):
        self.gradle_command = gradle_command

    def run_tests(self, workspace_path: str) -> bool:
        """
        Menjalankan Gradle Test pada path tertentu.
        Return True jika BUILD SUCCESSFUL, False jika gagal.
        
        Optimasi performa:
        - --daemon    : Reuse JVM yang sudah berjalan (skip cold start ~3-5 detik)
        - --build-cache: Cache hasil kompilasi (skip re-compile jika source tidak berubah)
        - -q          : Quiet mode, kurangi output logging Gradle (sedikit lebih cepat I/O)
        """
        try:
            gradle_cmd = self.gradle_command

            command = f"cd {workspace_path} && {gradle_cmd} test --daemon --build-cache -q"
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            output_string = output.decode("utf-8")
            
            if "BUILD SUCCESSFUL" in output_string:
                return True
            # Quiet mode mungkin tidak mencetak "BUILD SUCCESSFUL",
            # tapi jika exit code 0 (tidak exception), build berhasil
            return True
            
        except subprocess.CalledProcessError as e:
            # Test ada yang failed, code tidak error tapi assert ada yang salah
            error_output = e.output.decode("utf-8", errors="ignore") if e.output else "No output"
            logger.warning(f"Gradle test failed in {workspace_path}. Exit code: {e.returncode}. Output:\n{error_output}")
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error executing Gradle in {workspace_path}: {str(e)}")
            raise
