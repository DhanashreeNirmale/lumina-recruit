from services.judge0_service import Judge0Service

def run_candidate_code(source_code: str, language: str, stdin: str = "", expected_output: str = "") -> dict:
    """Convenience functional wrapper to execute code on the compiler service."""
    service = Judge0Service()
    return service.run_code(source_code, language, stdin, expected_output)

def check_compiler_status() -> bool:
    """Helper to check compiler status."""
    service = Judge0Service()
    return service.available()
