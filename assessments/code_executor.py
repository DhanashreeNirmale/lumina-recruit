import os

import requests
from dotenv import load_dotenv


load_dotenv()


class CodeExecutionError(Exception):
    """Raised when code execution fails."""
    pass


class CodeExecutor:

    LANGUAGE_MAP = {
        "python": "python-3.14",
        "python3": "python-3.14",
        "c": "gcc-15",
        "cpp": "g++-15",
        "c++": "g++-15",
        "java": "openjdk-25",
        "csharp": "dotnet-csharp-9",
        "go": "go-1.26",
        "rust": "rust-1.93",
        "javascript": "typescript-deno",
        "typescript": "typescript-deno",
    }

    def __init__(self):
        self.api_key = os.getenv("CODE_EXECUTOR_API_KEY")

        self.url = os.getenv(
            "CODE_EXECUTOR_URL",
            "https://api.onlinecompiler.io/api/run-code-sync/"
        )

        if not self.api_key:
            raise CodeExecutionError(
                "CODE_EXECUTOR_API_KEY is missing from .env"
            )

    def execute(
        self,
        code: str,
        language: str,
        stdin: str = "",
    ) -> dict:

        if not code.strip():
            raise CodeExecutionError(
                "Source code cannot be empty."
            )

        compiler = self.LANGUAGE_MAP.get(
            language.lower().strip()
        )

        if not compiler:
            raise CodeExecutionError(
                f"Unsupported language: {language}"
            )

        payload = {
            "compiler": compiler,
            "code": code,
            "input": stdin or "",
        }

        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                self.url,
                headers=headers,
                json=payload,
                timeout=35,
            )

        except requests.RequestException as exc:
            raise CodeExecutionError(
                f"Connection error: {exc}"
            ) from exc

        if response.status_code != 200:
            raise CodeExecutionError(
                f"API returned {response.status_code}: "
                f"{response.text[:1000]}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise CodeExecutionError(
                "API returned invalid JSON."
            ) from exc

        return {
            "status": data.get("status"),
            "output": data.get("output", ""),
            "error": data.get("error", ""),
            "exit_code": data.get("exit_code"),
            "signal": data.get("signal"),
            "time": data.get("time"),
            "total_time": data.get("total"),
            "memory": data.get("memory"),
        }