from resume_parser.resume_extractor import parse_resume_file
from database.repositories import create_or_update_candidate

class ResumeService:
    def process_and_save_resume(self, user_id: int, file_name: str, file_bytes: bytes) -> dict:
        """
        Parses resume bytes, maps to schema using ResumeAgent,
        and saves/updates candidate profile in database.
        """
        # Parse and extract
        parsed_data = parse_resume_file(file_name, file_bytes)
        
        # Save to SQLite database
        candidate_id = create_or_update_candidate(user_id, parsed_data)
        parsed_data["id"] = candidate_id
        
        return parsed_data
