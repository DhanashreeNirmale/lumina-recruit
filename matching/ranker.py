def rank_candidates(results):
    """
    Sort candidates by overall score.
    """

    return sorted(
        results,
        key=lambda item: item.get(
            "overall_score",
            0
        ),
        reverse=True,
    )