import logging
import os
import re
import shlex
import subprocess
import time
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class GradleExecutor:
    """Menangani eksekusi Gradle melalui subprocess."""

    def __init__(self, gradle_command: str):
        self.gradle_command: str = gradle_command

    @staticmethod
    def _timestamp() -> str:
        return datetime.now().strftime("%H:%M:%S.%f")[:-3]

    @staticmethod
    def _dependency_count(workspace: Path) -> int:
        build_file = workspace / "build.gradle"
        if not build_file.exists():
            return 0

        dependency_pattern = re.compile(
            r"^\s*(?:api|implementation|compileOnly|runtimeOnly|testImplementation|"
            r"testCompileOnly|testRuntimeOnly|annotationProcessor|testAnnotationProcessor)\b"
        )
        return sum(
            1
            for line in build_file.read_text(encoding="utf-8", errors="replace").splitlines()
            if dependency_pattern.match(line)
        )

    def _log_workspace_profile(self, workspace_path: str) -> None:
        workspace = Path(workspace_path).resolve()
        main_java = sorted((workspace / "src" / "main" / "java").rglob("*.java"))
        test_java = sorted((workspace / "src" / "test" / "java").rglob("*.java"))
        files = [path for path in workspace.rglob("*") if path.is_file()]
        workspace_size = sum(path.stat().st_size for path in files)

        logger.info(
            "[GRADLE PROFILE] Workspace path=%s exists=%s build_exists=%s .gradle_exists=%s",
            workspace,
            workspace.exists(),
            (workspace / "build").exists(),
            (workspace / ".gradle").exists(),
        )
        logger.info(
            "[GRADLE PROFILE] Project size: src/main/java=%d file(s), "
            "src/test/java=%d file(s), total=%d file(s), dependencies=%d, "
            "workspace_size=%d bytes (%.2f MiB)",
            len(main_java),
            len(test_java),
            len(files),
            self._dependency_count(workspace),
            workspace_size,
            workspace_size / (1024 * 1024),
        )
        for source_file in main_java + test_java:
            stat = source_file.stat()
            logger.info(
                "[GRADLE PROFILE] Source path=%s mtime=%s mtime_ns=%d size=%d bytes",
                source_file.relative_to(workspace),
                datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="milliseconds"),
                stat.st_mtime_ns,
                stat.st_size,
            )

    @staticmethod
    def _latest_profile_report(workspace_path: str) -> Path | None:
        workspace = Path(workspace_path).resolve()
        # Gradle 7.5.1 may write to reports/profile (without build/) when
        # --profile is combined with a reused configuration cache.
        reports = list((workspace / "build" / "reports" / "profile").glob("profile-*.html"))
        reports.extend((workspace / "reports" / "profile").glob("profile-*.html"))
        return max(reports, key=lambda path: path.stat().st_mtime, default=None)

    def run_tests(self, workspace_path: str) -> bool:
        """
        Menjalankan Gradle Test pada path tertentu.
        Return True jika BUILD SUCCESSFUL, False jika gagal.

        Optimasi performa:
        - Reuse Gradle daemon untuk menghindari startup JVM pada setiap request.
        - Gunakan build/configuration cache dari workspace yang persisten.
        - Jalankan offline karena dependency sudah dipanaskan saat image dibangun.
        """
        started_at = time.perf_counter()
        try:
            self._log_workspace_profile(workspace_path)
            command = shlex.split(self.gradle_command, posix=os.name != "nt")

            # Optimasi untuk environment Windows dan Linux
            if os.name == 'nt' and command[0] in ('gradlew', 'gradlew.bat', './gradlew', '.\\gradlew'):
                # Di Windows, subprocess.run tidak mencari executable di 'cwd' jika tidak ada separator path.
                # Paksa menggunakan path absolut ke gradlew.bat di dalam workspace.
                command[0] = os.path.abspath(os.path.join(workspace_path, 'gradlew.bat'))
            elif os.name != 'nt' and command[0] == 'gradlew':
                command[0] = './gradlew'

            command.extend([
                "test",
                "--daemon",
                "--build-cache",
                "--offline",
                "--profile",
                "--info",
                "--configuration-cache",
                "--configuration-cache-problems=warn",
                "--console=plain",
            ])

            # Build Scan mengunggah detail build dan membutuhkan internet, sehingga
            # hanya diaktifkan eksplisit untuk sesi profiling non-production.
            if os.getenv("GRADLE_BUILD_SCAN", "false").lower() == "true":
                command.remove("--offline")
                command.append("--scan")
                logger.warning(
                    "[GRADLE PROFILE] Build Scan enabled; build data may be uploaded to Gradle."
                )

            # Work around Gradle 7.5.1 writing the profile outside build/ when
            # configuration cache is reused. Without this directory Gradle exits
            # with code 1 after reporting BUILD SUCCESSFUL.
            os.makedirs(os.path.join(workspace_path, "reports", "profile"), exist_ok=True)

            logger.info(
                "[%s] [GRADLE PROFILE] Launching Gradle: %s",
                self._timestamp(),
                shlex.join(command),
            )
            output_lines: list[str] = []
            process = subprocess.Popen(
                command,
                cwd=workspace_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            if process.stdout is None:
                raise RuntimeError("Gradle stdout pipe was not created")

            for line in process.stdout:
                line = line.rstrip("\r\n")
                output_lines.append(line)
                logger.info("[%s] [GRADLE] %s", self._timestamp(), line)

            return_code = process.wait()
            output = "\n".join(output_lines)
            elapsed = time.perf_counter() - started_at
            logger.info(
                "[%s] [GRADLE PROFILE] Gradle process finished in %.3fs with exit code %d",
                self._timestamp(),
                elapsed,
                return_code,
            )

            profile_report = self._latest_profile_report(workspace_path)
            logger.info(
                "[GRADLE PROFILE] Gradle profile report: %s",
                profile_report if profile_report else "not generated",
            )

            daemon_started = "Starting a Gradle Daemon" in output
            configuration_cache_reused = any(message in output for message in (
                "Reusing configuration cache.",
                "Configuration cache entry reused.",
            ))
            task_summary = ", ".join(
                line.removeprefix("> Task ").strip()
                for line in output.splitlines()
                if line.startswith("> Task ")
            )
            logger.info(
                "Gradle finished in %.3fs (daemon_reused=%s, configuration_cache_reused=%s, tasks=%s)",
                elapsed,
                not daemon_started,
                configuration_cache_reused,
                task_summary or "not reported",
            )
            if return_code != 0:
                logger.warning(
                    "Gradle test failed in %s after %.3fs. Exit code: %s",
                    workspace_path,
                    elapsed,
                    return_code,
                )
                return False
            return True

        except Exception as e:
            logger.error("Unexpected error executing Gradle in %s: %s", workspace_path, e)
            raise
