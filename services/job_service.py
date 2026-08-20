from agents.job_agent import JobAgent
from database.repositories import create_job

class JobService:
    def parse_and_save_job(self, description: str, manual_title: str = "") -> dict:
        """
        Parses the raw job description with JobAgent and saves it to the database.
        """
        agent = JobAgent()
        job_data = agent.analyze(description)
        
        # Override title if manual title provided
        if manual_title.strip():
            job_data["title"] = manual_title.strip()
            
        # Store description
        job_data["description"] = description
        
        # Save to database
        job_id = create_job(job_data)
        job_data["id"] = job_id
        
        return job_data
