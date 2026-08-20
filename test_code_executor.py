from assessments.code_executor import (
    CodeExecutor,
    CodeExecutionError,
)


def main():
    try:
        executor = CodeExecutor()

        print("Testing code execution...")

        result = executor.execute(
            code='print("Hello from our assessment system")',
            language="python",
        )

        print("\n========== RESULT ==========")
        print("Status:", result["status"])
        print("Output:", result["output"])
        print("Error:", result["error"])
        print("Exit code:", result["exit_code"])
        print("Time:", result["time"])
        print("Memory:", result["memory"])
        print("============================")

    except CodeExecutionError as exc:
        print("\nCODE EXECUTION ERROR:")
        print(exc)

    except Exception as exc:
        print("\nUNEXPECTED ERROR:")
        print(exc)


if __name__ == "__main__":
    main()