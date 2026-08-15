from matching.matcher import score_candidate


class MatchingAgent:

    def score(
        self,
        candidate,
        job
    ):

        return score_candidate(
            candidate,
            job
        )