class AssessmentService:
    """
    Common interface for assessment providers.

    The application should use this interface rather than
    directly depending on one provider everywhere.
    """

    def create_assessment(
        self,
        candidate_id,
        job_id,
        assessment_name
    ):
        raise NotImplementedError

    def get_result(self, assessment_id):
        raise NotImplementedError