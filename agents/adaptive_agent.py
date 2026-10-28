# =========================================================
# ADAPTIVE DIFFICULTY AGENT
# agents/adaptive_agent.py
# =========================================================


def calculate_next_difficulty(
    current_difficulty: str,
    score: int
) -> str:

    difficulty_levels = [
        "Easy",
        "Medium",
        "Hard"
    ]

    current_difficulty = (
        current_difficulty.capitalize()
    )

    if current_difficulty not in difficulty_levels:
        raise ValueError(
            "Difficulty must be Easy, Medium, or Hard."
        )

    current_index = difficulty_levels.index(
        current_difficulty
    )

    # -----------------------------------------------------
    # High Score → Increase Difficulty
    # -----------------------------------------------------

    if score >= 8:

        next_index = min(
            current_index + 1,
            len(difficulty_levels) - 1
        )

    # -----------------------------------------------------
    # Medium Score → Keep Same Difficulty
    # -----------------------------------------------------

    elif score >= 5:

        next_index = current_index

    # -----------------------------------------------------
    # Low Score → Decrease Difficulty
    # -----------------------------------------------------

    else:

        next_index = max(
            current_index - 1,
            0
        )

    return difficulty_levels[
        next_index
    ]


# =========================================================
# PUBLIC ADAPTIVE AGENT FUNCTION
# =========================================================

def get_adaptive_difficulty(
    current_difficulty: str,
    score: int
) -> str:

    print(
        f"[1] Current Difficulty : "
        f"{current_difficulty}"
    )

    print(
        f"[2] Candidate Score    : "
        f"{score}/10"
    )

    next_difficulty = calculate_next_difficulty(
        current_difficulty,
        score
    )

    print(
        f"[3] Next Difficulty    : "
        f"{next_difficulty}"
    )

    return next_difficulty


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print()

    # Test case
    current_difficulty = "Medium"
    score = 9

    next_difficulty = get_adaptive_difficulty(
        current_difficulty,
        score
    )

    print()
    print("Adaptive Decision:")
    print("-" * 70)

    print(
        f"{current_difficulty} question → "
        f"{score}/10 → "
        f"{next_difficulty} question"
    )

    print("-" * 70)