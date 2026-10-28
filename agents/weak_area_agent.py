from collections import defaultdict


def analyze_weak_areas(history: list):
    """
    Analyze interview history and identify concepts
    where the candidate performed poorly.
    """

    if not history:
        return []

    concept_scores = defaultdict(list)

    # --------------------------------------------------------
    # Collect scores by concept
    # --------------------------------------------------------

    for item in history:

        concept = item["concept"]
        score = item["score"]

        concept_scores[concept].append(score)

    # --------------------------------------------------------
    # Calculate average score for each concept
    # --------------------------------------------------------

    weak_areas = []

    for concept, scores in concept_scores.items():

        average_score = sum(scores) / len(scores)

        # ----------------------------------------------------
        # Determine severity
        # ----------------------------------------------------

        if average_score < 5:
            severity = "HIGH"

        elif average_score < 7:
            severity = "MEDIUM"

        else:
            continue

        weak_areas.append({
            "concept": concept,
            "average_score": round(average_score, 2),
            "severity": severity
        })

    # --------------------------------------------------------
    # Sort weakest concepts first
    # --------------------------------------------------------

    weak_areas.sort(
        key=lambda item: item["average_score"]
    )

    return weak_areas


if __name__ == "__main__":

    test_history = [
        {
            "concept": "Tuples",
            "score": 4
        },
        {
            "concept": "Lists",
            "score": 8
        },
        {
            "concept": "Tuples",
            "score": 5
        },
        {
            "concept": "Decorators",
            "score": 3
        }
    ]

    results = analyze_weak_areas(test_history)

    print("\nWeak Areas")
    print("=" * 50)

    for item in results:
        print(
            f"Concept: {item['concept']}"
        )
        print(
            f"Average Score: {item['average_score']}/10"
        )
        print(
            f"Severity: {item['severity']}"
        )
        print()