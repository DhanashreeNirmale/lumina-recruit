# database/recruiter.py

import json

from database.models import (
    save_candidate,
    save_job,
    save_application,
    save_interview,
    get_candidates,
    get_jobs,
    get_applications,
    get_interviews,
)

from matching.matcher import match_candidate
from matching.ranker import rank_candidates


class RecruiterService:
    """
    High-level service layer for the AI recruiter.

    Responsibilities:
    - Candidate management
    - Job management
    - Candidate-job matching
    - Application creation
    - Candidate ranking
    - Interview scheduling
    - Recruiter dashboard data

    This class sits between the UI/agents and the database layer.
    """

    # =====================================================
    # CANDIDATE MANAGEMENT
    # =====================================================

    def create_candidate(self, candidate):
        """
        Save an extracted candidate profile.

        Parameters
        ----------
        candidate : dict
            Candidate information extracted from the resume.

        Returns
        -------
        int
            Database ID of the newly created candidate.
        """

        if not candidate:
            raise ValueError(
                "Candidate information cannot be empty."
            )

        if not candidate.get("name"):
            candidate["name"] = "Unknown Candidate"

        if not candidate.get("skills"):
            candidate["skills"] = []

        return save_candidate(candidate)

    # =====================================================
    # JOB MANAGEMENT
    # =====================================================

    def create_job(self, job, description=""):
        """
        Save a job requirement.

        Parameters
        ----------
        job : dict
            Structured job information.

        description : str
            Original job description.

        Returns
        -------
        int
            Database ID of the newly created job.
        """

        if not job:
            raise ValueError(
                "Job information cannot be empty."
            )

        if not job.get("title"):
            raise ValueError(
                "Job title is required."
            )

        if not job.get("required_skills"):
            job["required_skills"] = []

        return save_job(
            job,
            description
        )

    # =====================================================
    # MATCHING
    # =====================================================

    def match_candidate_to_job(
        self,
        candidate,
        job
    ):
        """
        Match one candidate against one job.

        Returns the transparent scoring breakdown.
        """

        if not candidate:
            raise ValueError(
                "Candidate information is required."
            )

        if not job:
            raise ValueError(
                "Job information is required."
            )

        return match_candidate(
            candidate,
            job
        )

    # =====================================================
    # APPLICATION
    # =====================================================

    def create_application(
        self,
        candidate_id,
        job_id,
        candidate,
        job
    ):
        """
        Match candidate and job and save the application.

        This is the main recruiter workflow:

            Candidate
                ↓
            Job
                ↓
            Matching Engine
                ↓
            Score
                ↓
            Application Database
        """

        if not candidate_id:
            raise ValueError(
                "Candidate ID is required."
            )

        if not job_id:
            raise ValueError(
                "Job ID is required."
            )

        result = self.match_candidate_to_job(
            candidate,
            job
        )

        application_id = save_application(
            candidate_id,
            job_id,
            result
        )

        return {
            "application_id": application_id,
            "candidate_id": candidate_id,
            "job_id": job_id,
            "result": result,
        }

    # =====================================================
    # RANKING
    # =====================================================

    def rank_candidates_for_job(
        self,
        candidates,
        job
    ):
        """
        Match multiple candidates against one job
        and rank them by overall score.

        Parameters
        ----------
        candidates : list[dict]
            Candidate profiles.

        job : dict
            Job requirements.

        Returns
        -------
        list[dict]
            Ranked candidates.
        """

        if not candidates:
            return []

        if not job:
            raise ValueError(
                "Job information is required."
            )

        results = []

        for candidate in candidates:

            try:

                match_result = self.match_candidate_to_job(
                    candidate,
                    job
                )

                results.append(
                    {
                        "candidate_id": candidate.get(
                            "id"
                        ),
                        "candidate_name": candidate.get(
                            "name",
                            "Unknown Candidate"
                        ),
                        "email": candidate.get(
                            "email",
                            ""
                        ),
                        "skills": candidate.get(
                            "skills",
                            []
                        ),
                        "experience": candidate.get(
                            "experience",
                            0
                        ),
                        **match_result,
                    }
                )

            except Exception as exc:

                results.append(
                    {
                        "candidate_id": candidate.get(
                            "id"
                        ),
                        "candidate_name": candidate.get(
                            "name",
                            "Unknown Candidate"
                        ),
                        "error": str(exc),
                        "overall_score": 0,
                        "recommendation": "Error",
                    }
                )

        return rank_candidates(results)

    # =====================================================
    # SHORTLISTING
    # =====================================================

    def get_shortlisted_candidates(
        self,
        candidates,
        job,
        minimum_score=80
    ):
        """
        Return candidates whose matching score
        is greater than or equal to minimum_score.
        """

        ranked = self.rank_candidates_for_job(
            candidates,
            job
        )

        return [
            candidate
            for candidate in ranked
            if candidate.get(
                "overall_score",
                0
            ) >= minimum_score
        ]

    # =====================================================
    # INTERVIEW MANAGEMENT
    # =====================================================

    def schedule_candidate_interview(
        self,
        candidate_id,
        job_id,
        interview_date,
        interview_time,
        interview_type="Technical",
        notes=""
    ):
        """
        Schedule an interview for a candidate.
        """

        if not candidate_id:
            raise ValueError(
                "Candidate ID is required."
            )

        if not job_id:
            raise ValueError(
                "Job ID is required."
            )

        if not interview_date:
            raise ValueError(
                "Interview date is required."
            )

        if not interview_time:
            raise ValueError(
                "Interview time is required."
            )

        return save_interview(
            candidate_id=candidate_id,
            job_id=job_id,
            interview_date=str(
                interview_date
            ),
            interview_time=str(
                interview_time
            ),
            interview_type=interview_type,
            notes=notes,
        )

    # =====================================================
    # DATA RETRIEVAL
    # =====================================================

    def list_candidates(self):
        """
        Return all candidates.
        """

        return get_candidates()

    def list_jobs(self):
        """
        Return all jobs.
        """

        return get_jobs()

    def list_applications(self):
        """
        Return all applications.
        """

        return get_applications()

    def list_interviews(self):
        """
        Return all scheduled interviews.
        """

        return get_interviews()

    # =====================================================
    # DASHBOARD STATISTICS
    # =====================================================

    def get_dashboard_statistics(self):
        """
        Generate recruiter dashboard statistics.
        """

        candidates = self.list_candidates()
        jobs = self.list_jobs()
        applications = self.list_applications()
        interviews = self.list_interviews()

        shortlisted = 0
        selected = 0
        screening = 0
        rejected = 0

        for application in applications:

            recommendation = (
                application.get(
                    "recommendation",
                    ""
                )
            )

            status = application.get(
                "status",
                ""
            )

            if recommendation == "Shortlisted":
                shortlisted += 1

            if status == "Selected":
                selected += 1

            if status == "Screening":
                screening += 1

            if status == "Not Shortlisted":
                rejected += 1

        return {
            "total_candidates": len(
                candidates
            ),
            "total_jobs": len(
                jobs
            ),
            "total_applications": len(
                applications
            ),
            "total_interviews": len(
                interviews
            ),
            "shortlisted": shortlisted,
            "selected": selected,
            "screening": screening,
            "rejected": rejected,
        }

    # =====================================================
    # TOP CANDIDATES
    # =====================================================

    def get_top_candidates(
        self,
        limit=10
    ):
        """
        Return top candidates based on
        application matching score.
        """

        applications = self.list_applications()

        ranked = sorted(
            applications,
            key=lambda item: item.get(
                "overall_score",
                0
            ),
            reverse=True,
        )

        return ranked[:limit]