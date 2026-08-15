import requests

from config.settings import JUDGE0_API_URL


class Judge0Service:

    LANGUAGE_IDS = {

        "Python": 71,

        "Java": 62,

        "C++": 54,
    }


    def __init__(self):

        self.base_url = (
            JUDGE0_API_URL
            .rstrip("/")
        )


    def available(self):

        try:

            response = requests.get(
                f"{self.base_url}/languages",
                timeout=5
            )

            return response.ok

        except requests.RequestException:

            return False


    def run_code(
        self,
        source_code,
        language_id,
        stdin="",
        expected_output=""
    ):

        try:

            response = requests.post(

                f"{self.base_url}/submissions",

                params={
                    "wait": "true",
                    "base64_encoded": "false"
                },

                json={

                    "source_code": source_code,

                    "language_id": language_id,

                    "stdin": stdin,

                    "expected_output": expected_output,
                },

                timeout=30
            )

            response.raise_for_status()

            return {
                "success": True,
                "data": response.json()
            }

        except requests.RequestException as exc:

            return {
                "success": False,
                "message": str(exc)
            }