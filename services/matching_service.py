from agents.matching_agent import MatchingAgent
from database.repositories import get_candidate_by_id, get_job_by_id, update_application_score, get_application_by_id

class MatchingService:
    def evaluate_and_save_match(self, application_id: int) -> dict:
        """
        Loads application, candidate, and job profiles, runs the MatchingAgent evaluation,
        and saves score & explanation in SQLite.
        """
        app = get_application_by_id(application_id)
        if not app:
            raise ValueError(f"Application ID {application_id} not found.")
            
        candidate = get_candidate_by_id(app["candidate_id"])
        job = get_job_by_id(app["job_id"])
        
        if not candidate or not job:
            raise ValueError("Candidate or Job profile linked to application is missing.")
            
        agent = MatchingAgent()
        match_report = agent.evaluate(candidate, job)
        
        # Save score and explanation back to application row
        update_application_score(
            application_id,
            match_report["overall_score"],
            match_report["explanation"]
        )
        
        return match_report
