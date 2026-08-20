from assessments.judge0 import Judge0Service, Judge0Error


def main():
    try:
        print("Connecting to Judge0...")

        judge = Judge0Service()

        about = judge.check_connection()

        print("SUCCESS: Judge0 connected!")
        print("Judge0:", about)

        print("\nSubmitting test code...")

        result = judge.run_code(
            source_code='print("Hello from Judge0")',
            language_id=71,
        )

        print("\n========== RESULT ==========")
        print("Status:", result.get("status"))
        print("Output:", result.get("stdout"))
        print("Error:", result.get("stderr"))
        print("Compile error:", result.get("compile_output"))
        print("Time:", result.get("time"))
        print("Memory:", result.get("memory"))
        print("============================")

    except Judge0Error as e:
        print("\nJUDGE0 ERROR:")
        print(e)

    except Exception as e:
        print("\nUNEXPECTED ERROR:")
        print(e)


if __name__ == "__main__":
    main()