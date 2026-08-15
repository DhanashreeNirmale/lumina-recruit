import json

import pandas as pd
import streamlit as st

from database.models import (
    get_candidates,
    get_jobs,
    update_candidate_score,
)

from matching.matcher import (
    score_candidate
)


def _decode(value):

    if isinstance(
        value,
        list
    ):

        return value

    try:

        parsed = json.loads(
            value or "[]"
        )

        if isinstance(
            parsed,
            list
        ):

            return parsed

    except (
        TypeError,
        json.JSONDecodeError
    ):

        pass

    return []


def show_ranking_page():

    st.title(
        "🏆 Candidate Ranking"
    )

    st.caption(
        "AI-assisted candidate ranking "
        "for the selected job."
    )

    candidates = get_candidates()

    jobs = get_jobs()

    if not candidates:

        st.info(
            "No candidates available."
        )

        return

    if not jobs:

        st.info(
            "No jobs available."
        )

        return

    # ========================================================
    # SELECT JOB
    # ========================================================

    job_map = {

        f"#{job['id']} — {job['title']}":
        job

        for job in jobs
    }

    selected_label = st.selectbox(
        "Rank candidates for",
        list(
            job_map.keys()
        ),
    )

    job = job_map[
        selected_label
    ]

    # ========================================================
    # CALCULATE
    # ========================================================

    if st.button(
        "⚡ Calculate Ranking",
        type="primary",
    ):

        rows = []

        for candidate in candidates:

            candidate_for_score = dict(
                candidate
            )

            candidate_for_score[
                "skills"
            ] = _decode(
                candidate.get(
                    "skills"
                )
            )

            candidate_for_score[
                "education"
            ] = _decode(
                candidate.get(
                    "education"
                )
            )

            score = score_candidate(
                candidate_for_score,
                job
            )

            if score >= 75:

                status = "Shortlisted"

            elif score >= 50:

                status = "Screening"

            else:

                status = "New"

            update_candidate_score(
                candidate["id"],
                score,
                status
            )

            rows.append(
                {
                    "Candidate ID":
                        candidate["id"],

                    "Candidate":
                        candidate["name"],

                    "Email":
                        candidate["email"],

                    "Score":
                        score,

                    "Status":
                        status,

                    "Skills":
                        ", ".join(
                            candidate_for_score[
                                "skills"
                            ]
                        ),

                    "Education":
                        ", ".join(
                            candidate_for_score[
                                "education"
                            ]
                        ),

                    "Notice Period":
                        candidate[
                            "notice_period"
                        ],

                    "Expected Salary (LPA)":
                        candidate[
                            "expected_salary"
                        ],

                    "Location":
                        candidate[
                            "location"
                        ],
                }
            )

        st.session_state[
            "ranking_rows"
        ] = rows

    # ========================================================
    # DISPLAY
    # ========================================================

    rows = st.session_state.get(
        "ranking_rows"
    )

    if not rows:

        st.info(
            "Click 'Calculate Ranking' "
            "to rank the candidates."
        )

        return

    df = pd.DataFrame(
        rows
    )

    df = df.sort_values(
        "Score",
        ascending=False
    ).reset_index(
        drop=True
    )

    # ========================================================
    # TOP CANDIDATE
    # ========================================================

    top = df.iloc[0]

    st.success(
        f"🏆 Top Candidate: "
        f"{top['Candidate']} "
        f"— {top['Score']}/100"
    )

    # ========================================================
    # TABLE
    # ========================================================

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    # ========================================================
    # CSV EXPORT
    # ========================================================

    csv = df.to_csv(
        index=False
    ).encode(
        "utf-8"
    )

    st.download_button(
        "⬇️ Export Candidate Ranking CSV",

        data=csv,

        file_name=(
            "candidate_ranking.csv"
        ),

        mime="text/csv",
    )