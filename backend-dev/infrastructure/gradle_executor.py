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
        """
        try:
            # Gunakan stderr=subprocess.STDOUT agar error gradle tetap tertangkap di output_string
            gradle_cmd = self.gradle_command
            # if not gradle_cmd.startswith("./") and not os.path.isabs(gradle_cmd):
            #     gradle_cmd = f"./{gradle_cmd}"

            command = f"cd {workspace_path} && {gradle_cmd} test"
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            output_string = output.decode("utf-8")
            
            if "BUILD SUCCESSFUL" in output_string:
                return True
            return False
            
        except subprocess.CalledProcessError as e:
            # Test ada yang failed, code tidak error tapi assert ada yang salah
            error_output = e.output.decode("utf-8", errors="ignore") if e.output else "No output"
            logger.warning(f"Gradle test failed in {workspace_path}. Exit code: {e.returncode}. Output:\n{error_output}")
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error executing Gradle in {workspace_path}: {str(e)}")
            raise