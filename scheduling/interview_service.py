from database.repositories import (
    schedule_interview,
    get_interviews_by_candidate,
    get_interviews_by_job,
    get_all_interviews,
    update_interview_status
)

class InterviewService:
    def book_interview(self, candidate_id: int, job_id: int, date_str: str, time_str: str, mode: str, venue_link: str = "", notes: str = ""):
        """Schedules a candidate interview."""
        return schedule_interview(candidate_id, job_id, date_str, time_str, mode, venue_link, notes)

    def get_candidate_schedule(self, candidate_id: int) -> list:
        """Fetches interviews scheduled for a candidate."""
        return get_interviews_by_candidate(candidate_id)

    def get_job_schedule(self, job_id: int) -> list:
        """Fetches interviews scheduled for a job."""
        return get_interviews_by_job(job_id)

    def get_all_schedules(self) -> list:
        """Fetches all interviews."""
        return get_all_interviews()

    def set_status(self, interview_id: int, status: str):
        """Updates interview status (Scheduled, Completed, Cancelled)."""
        return update_interview_status(interview_id, status)
