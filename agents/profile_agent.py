from pathlib import Path
import sys
import json

# ---------------------------------------------------------
# Project Root
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


# ---------------------------------------------------------
# Gemini
# ---------------------------------------------------------

from agents.gemini_agent import ask_gemini


# =========================================================
# PROFILE ANALYZER
# =========================================================

def analyze_profile(
    name: str,
    education: str,
    skills: list,
    projects: list,
    experience: str,
    target_role: str
):
    """
    Analyze candidate information and create
    a structured interview profile.
    """

    skills_text = ", ".join(skills)
    projects_text = ", ".join(projects)

    prompt = f"""
You are an expert technical interview profile analyzer.

Analyze the candidate information below and create a
structured profile for an AI technical interview system.

================ CANDIDATE INFORMATION ================

Name:
{name}

Education:
{education}

Skills:
{skills_text}

Projects:
{projects_text}

Experience:
{experience}

Target Role:
{target_role}

========================================================

Return EXACTLY this format:

Candidate Profile:
<short profile summary>

Technical Skills:
- <skill>
- <skill>

Primary Areas:
- <area>
- <area>

Project Experience:
- <project>
- <project>

Experience Level:
<Fresher / Beginner / Intermediate / Experienced>

Target Role:
<role>

Interview Focus Areas:
- <area>
- <area>
- <area>

Potential Weak Areas:
- <area>
- <area>

Recommended Starting Difficulty:
<Easy / Medium / Hard>

IMPORTANT:
- Use only the information provided.
- Do not invent experience or skills.
- Do not ask questions.
- Do not include internal reasoning.
- Keep the analysis concise and professional.
"""

    print("\n[PROFILE AGENT] Analyzing candidate profile...")

    result = ask_gemini(prompt)

    if not result:
        print(
            "[PROFILE AGENT] "
            "Failed to generate profile analysis."
        )
        return ""

    print(
        "[PROFILE AGENT] "
        "Profile analysis generated successfully."
    )

    return result.strip()


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    test_profile = analyze_profile(
        name="Dinesh",
        education="B.E. Computer Science",
        skills=[
            "Python",
            "Machine Learning",
            "SQL",
            "FastAPI",
            "LangChain"
        ],
        projects=[
            "AI Interview System",
            "Medical VR Training System"
        ],
        experience="Fresher",
        target_role="Python Developer"
    )

    print("\n")
    print("=" * 70)
    print("CANDIDATE PROFILE ANALYSIS")
    print("=" * 70)

    print(test_profile)