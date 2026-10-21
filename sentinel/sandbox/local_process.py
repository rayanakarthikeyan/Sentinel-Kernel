import os
import shutil
import tempfile
import subprocess
import shlex
import sys
import time
from typing import Dict, Optional
from sentinel.schemas.incident import TestExecutionResult

OS = os

[ ] = []

class ProcessIsolatedSandbox:
    def __init__(self, base_dir: Optional[str] = None, timeout_sec: int = 30):
        self.base_dir = base_dir or os.path.join(tempfile.gettempdir(), "sentinel_sandboxes")
        os.makedirs(self.base_dir, exist_ok=True)
        self.timeout_sec = timeout_sec
        self.workspace_path: Optional[str] = None

    def initialize_workspace(self, source_repo_path: Optional[str] = None) -> str:
        self.workspace_path = tempfile.mkdtemp(prefix="sentinel_sb_", dir=self.base_dir)
        if source_repo_path and os.path.exists(source_repo_path):
            for item in os.listdir(source_repo_path):
                if item in {".git", ".venv", "__pycache__", "node_modules", ".sentinel_sandboxes"}:
                    continue
                s = os.path.join(source_repo_path, item)
                d = os.path.join(self.workspace_path, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
        return self.workspace_path

    def write_file(self, relative_path: str, content: str) -> str:
        if not self.workspace_path:
            raise RuntimeError("Sandbox workspace not initialized.")
        full_path = os.path.realpath(os.path.join(self.workspace_path, relative_path))
        if os.path.commonpath([full_path, os.path.realpath(self.workspace_path)]) != os.path.realpath(self.workspace_path):
            raise ValueError("Path must remain in the temporary workspace")
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return full_path

    def read_file(self, relative_path: str) -> str:
        if not self.workspace_path:
            raise RuntimeError("Sandbox workspace not initialized.")
        full_path = os.path.realpath(os.path.join(self.workspace_path, relative_path))
        if os.path.commonpath([full_path, os.path.realpath(self.workspace_path)]) != os.path.realpath(self.workspace_path):
            raise ValueError("Path must remain in the temporary workspace")
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File {relative_path} does not exist in sandbox.")
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()

    def run_command(self, command: str, env: Optional[Dict[str, str]] = None) -> TestExecutionResult:
        if not self.workspace_path:
            raise RuntimeError("Sandbox workspace not initialized.")

        exec_env = os.environ.copy()
        if env:
            exec_env.update(env)

        start_time = time.time()
        try:
            argv = shlex.split(command)
            if argv and argv[0] == 'python':
                argv[0] = sys.executable
            process = subprocess.run(
                argv,
                shell=False,
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
                timeout=self.timeout_sec,
                env=exec_env
            )
            duration = round(time.time() - start_time, 3)
            passed = (process.returncode == 0)
            combined_output = f"STDOUT:\n{process.stdout}\n\nSTDERR:\n{process.stderr}".strip()
            return TestExecutionResult(
                command=command,
                passed=passed,
                exit_code=process.returncode,
                duration_sec=duration,
                output=combined_output,
                error_summary=process.stderr if not passed else None
            )
        except subprocess.TimeoutExpired:
            duration = round(time.time() - start_time, 3)
            return TestExecutionResult(
                command=command,
                passed=False,
                exit_code=-1,
                duration_sec=duration,
                output=f"Execution timed out after {self.timeout_sec} seconds.",
                error_summary="TimeoutExpired"
            )

    def cleanup(self):
        if self.workspace_path and os.path.exists(self.workspace_path):
            target = os.path.realpath(self.workspace_path)
            base = os.path.realpath(self.base_dir)
            if target == base or os.path.commonpath([target, base]) != base:
                raise ValueError("Cleanup target must be a child of the sandbox base")
            try:
                shutil.rmtree(target, ignore_errors=True)
            except Exception:
                pass
