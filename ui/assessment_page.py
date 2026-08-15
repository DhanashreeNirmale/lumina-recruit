import json

import streamlit as st

from agents.assessment_agent import (
    AssessmentAgent
)

from database.models import (
    get_candidates,
    get_jobs,
    save_assessment_result,
)

from services.assessment_service import (
    Judge0Service
)


FALLBACK_QUESTION = {

    "id": 1,

    "title": "Two Sum",

    "description": (
        "Given a list of integers and a target, "
        "print the indices of two numbers whose "
        "sum equals the target."
    ),

    "sample_input": (
        "2 7 11 15\n9"
    ),

    "sample_output": (
        "0 1"
    ),

    "test_cases": [

        {
            "input": "2 7 11 15\n9",
            "output": "0 1",
        },

        {
            "input": "3 2 4\n6",
            "output": "1 2",
        },
    ],
}


def show_assessment_page():

    st.title(
        "🧪 Technical Assessment"
    )

    st.caption(
        "AI-generated programming assessment "
        "with self-hosted Judge0 execution."
    )

    candidates = get_candidates()

    jobs = get_jobs()

    if not candidates or not jobs:

        st.info(
            "Create at least one candidate "
            "and one job first."
        )

        return

    candidate_map = {

        f"#{candidate['id']} — {candidate['name']}":
        candidate

        for candidate in candidates
    }

    job_map = {

        f"#{job['id']} — {job['title']}":
        job

        for job in jobs
    }

    selected_candidate_label = st.selectbox(
        "Candidate",
        list(
            candidate_map.keys()
        ),
    )

    selected_job_label = st.selectbox(
        "Job",
        list(
            job_map.keys()
        ),
    )

    language = st.selectbox(
        "Programming Language",
        [
            "Python",
            "Java",
            "C++",
        ],
    )

    # ========================================================
    # QUESTION
    # ========================================================

    question = st.session_state.get(
        "assessment_question",
        FALLBACK_QUESTION
    )

    if st.button(
        "🤖 Generate Question with AI"
    ):

        try:

            result = AssessmentAgent().generate_questions(
                job_map[
                    selected_job_label
                ]["description"],
                count=1
            )

            questions = result.get(
                "questions",
                []
            )

            if questions:

                st.session_state[
                    "assessment_question"
                ] = questions[0]

                question = questions[0]

                st.success(
                    "Question generated successfully."
                )

            else:

                st.warning(
                    "AI returned no question. "
                    "Using fallback question."
                )

        except Exception as exc:

            st.warning(
                "AI question generation failed. "
                f"Using fallback question.\n\n{exc}"
            )

    # ========================================================
    # QUESTION DISPLAY
    # ========================================================

    st.subheader(
        question.get(
            "title",
            "Programming Question"
        )
    )

    st.write(
        question.get(
            "description",
            ""
        )
    )

    if question.get(
        "sample_input"
    ):

        st.write(
            "**Sample Input:**"
        )

        st.code(
            question[
                "sample_input"
            ]
        )

    if question.get(
        "sample_output"
    ):

        st.write(
            "**Expected Output:**"
        )

        st.code(
            question[
                "sample_output"
            ]
        )

    # ========================================================
    # CODE
    # ========================================================

    code = st.text_area(
        "Candidate Code",
        height=350,
        placeholder=(
            "Write your solution here..."
        ),
    )

    # ========================================================
    # JUDGE0
    # ========================================================

    judge = Judge0Service()

    if judge.available():

        st.success(
            "✅ Judge0 is connected."
        )

    else:

        st.warning(
            "⚠️ Judge0 is not reachable at "
            f"{judge.base_url}"
        )

        st.caption(
            "Start your self-hosted Judge0 "
            "service before running code."
        )

    # ========================================================
    # RUN
    # ========================================================

    if st.button(
        "▶ Run Assessment",
        type="primary",
    ):

        if not code.strip():

            st.error(
                "Candidate code cannot be empty."
            )

            return

        tests = question.get(
            "test_cases"
        )

        if not tests:

            tests = [
                {
                    "input": question.get(
                        "sample_input",
                        ""
                    ),

                    "output": question.get(
                        "sample_output",
                        ""
                    ),
                }
            ]

        passed = 0

        results = []

        for index, test in enumerate(
            tests,
            start=1
        ):

            result = judge.run_code(

                code,

                Judge0Service.LANGUAGE_IDS[
                    language
                ],

                test.get(
                    "input",
                    ""
                ),

                test.get(
                    "output",
                    ""
                ),
            )

            results.append(
                result
            )

            if result.get(
                "success"
            ):

                status_id = (
                    result[
                        "data"
                    ]
                    .get(
                        "status",
                        {}
                    )
                    .get(
                        "id"
                    )
                )

                if status_id == 3:

                    passed += 1

        score = round(
            100
            * passed
            / max(
                1,
                len(tests)
            ),
            2
        )

        details = json.dumps(
            {
                "passed": passed,
                "total": len(tests),
                "results": results,
            },
            default=str
        )

        save_assessment_result(

            candidate_map[
                selected_candidate_label
            ]["id"],

            job_map[
                selected_job_label
            ]["id"],

            score,

            details
        )

        st.divider()

        st.metric(
            "Assessment Score",
            f"{score}/100"
        )

        st.write(
            f"Passed {passed} "
            f"out of {len(tests)} test cases."
        )

        # ====================================================
        # RESULTS
        # ====================================================

        for index, result in enumerate(
            results,
            start=1
        ):

            st.write(
                f"### Test Case {index}"
            )

            if result.get(
                "success"
            ):

                data = result[
                    "data"
                ]

                description = (
                    data
                    .get(
                        "status",
                        {}
                    )
                    .get(
                        "description",
                        "Unknown"
                    )
                )

                st.write(
                    f"Status: **{description}**"
                )

                stdout = data.get(
                    "stdout"
                )

                stderr = data.get(
                    "stderr"
                )

                if stdout:

                    st.code(
                        stdout
                    )

                if stderr:

                    st.error(
                        stderr
                    )

            else:

                st.error(
                    result.get(
                        "message",
                        "Assessment execution failed."
                    )
                )