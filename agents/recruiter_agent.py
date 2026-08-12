from agents.matching_agent import MatchingAgent
from agents.resume_agent import ResumeAgent
from agents.job_agent import JobAgent


class RecruiterAgent:

    def __init__(self):

        self.resume_agent = ResumeAgent()
        self.job_agent = JobAgent()
        self.matching_agent = MatchingAgent()

    def analyze_resume(self, resume_text):

        return self.resume_agent.analyze(
            resume_text
        )

    def analyze_job(self, job_description):

        return self.job_agent.analyze(
            job_description
        )

    def explain_match(
        self,
        candidate,
        job,
        result
    ):

        return self.matching_agent.explain_match(
            candidate,
            job,
            result
        )