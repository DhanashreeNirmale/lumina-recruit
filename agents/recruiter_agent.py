import logging
from services.llm_service import GeminiService
from config.settings import is_gemini_configured
from database.repositories import get_all_candidates, get_all_jobs, get_all_applications, get_all_interviews

logger = logging.getLogger(__name__)

class RecruiterAgent:
    """
    Recruiter Coordinator Agent.
    Orchestrates recruitment tasks and answers recruiter queries about candidate database state.
    """

    def __init__(self):
        self.gemini_configured = is_gemini_configured()
        if self.gemini_configured:
            try:
                self.llm = GeminiService()
            except Exception as e:
                logger.error(f"Failed to initialize Gemini Service: {e}")
                self.gemini_configured = False
        self.memory = []

    def answer_query(self, query: str) -> str:
        """
        Answers general queries by fetching current database state and passing it to Gemini.
        If Gemini is unavailable, uses rule-based filtering.
        """
        self.memory.append(f"User: {query}")
        
        # Load database state
        candidates = get_all_candidates()
        jobs = get_all_jobs()
        applications = get_all_applications()
        interviews = get_all_interviews()
        
        if self.gemini_configured:
            try:
                response = self._answer_with_llm(query, candidates, jobs, applications, interviews)
                self.memory.append(f"Agent: {response}")
                return response
            except Exception as exc:
                logger.warning(f"Gemini query failed: {exc}")
                
        # Rule-based fallback
        response = self._rule_based_answer(query, candidates, jobs, applications)
        self.memory.append(f"Agent (Fallback): {response}")
        return response

    def _answer_with_llm(self, query: str, candidates: list, jobs: list, applications: list, interviews: list) -> str:
        # Prepare context data
        c_list = []
        for c in candidates:
            c_list.append({
                "id": c["id"],
                "name": c["name"],
                "skills": c["skills"],
                "experience_years": c["experience_years"],
                "location": c["location"],
                "degree": c["degree"],
                "notice_period": c["notice_period"],
                "expected_salary": c["expected_salary"]
            })
            
        j_list = [{"id": j["id"], "title": j["title"], "location": j["location"]} for j in jobs]
        
        prompt = f"""
You are the Lumina Recruit Orchestrator Agent.
Answer the Recruiter's question using the provided recruitment database context.

RECRUITER QUESTION:
"{query}"

CURRENT DATABASE CONTEXT:
1. Candidates:
{c_list}

2. Jobs:
{j_list}

3. Applications:
{applications}

4. Scheduled Interviews:
{interviews}

Conversation History (Memory):
{self.memory[-4:-1] if len(self.memory) > 1 else "None"}

Provide a concise, direct, and professional response. Do not hallucinate candidates. If no candidates match, politely say so.
"""
        return self.llm.generate(prompt)

    def _rule_based_answer(self, query: str, candidates: list, jobs: list, applications: list) -> str:
        query_lower = query.lower()
        
        # 1. Experience query
        if "experience" in query_lower or "exp" in query_lower:
            # Extract numbers if any
            import re
            match = re.search(r'(\d+)\s*(?:years?|yrs?)', query_lower)
            min_exp = float(match.group(1)) if match else 0.0
            
            matched_candidates = [c for c in candidates if c["experience_years"] >= min_exp]
            if not matched_candidates:
                return f"No candidates found with >= {min_exp} years of experience."
            
            res = f"Candidates with >= {min_exp} years of experience:\n"
            for c in matched_candidates:
                res += f"- **{c['name']}** ({c['experience_years']} yrs exp, Skills: {', '.join(c['skills'][:4])})\n"
            return res
            
        # 2. Skill query
        for c in candidates:
            for skill in c["skills"]:
                if skill.lower() in query_lower:
                    # Found a skill keyword
                    matched = [cand for cand in candidates if any(skill.lower() == cs.lower() for cs in cand["skills"])]
                    res = f"Candidates possessing the skill **{skill}**:\n"
                    for cand in matched:
                        res += f"- **{cand['name']}** ({cand['experience_years']} yrs exp, Location: {cand['location']})\n"
                    return res
                    
        # 3. Job query
        if "jobs" in query_lower or "roles" in query_lower:
            if not jobs:
                return "There are no jobs currently posted on the platform."
            res = "Current active jobs:\n"
            for j in jobs:
                res += f"- **{j['title']}** in {j['location']} (Max notice period: {j['max_notice_period']} days)\n"
            return res
            
        # Generic response
        return "I can help you filter candidates by skills or experience. Try asking: 'Show candidates with Python' or 'Show candidates with 2 years of experience'."
