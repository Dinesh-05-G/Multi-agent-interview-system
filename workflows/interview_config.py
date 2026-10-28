import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_FILE = BASE_DIR / "data" / "interview_knowledge.json"


def load_knowledge():
    with open(
        KNOWLEDGE_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


# ============================================================
# CANDIDATE PROFILE
# ============================================================

def collect_candidate_profile():
    print("\n")
    print("=" * 70)
    print("CANDIDATE PROFILE")
    print("=" * 70)

    name = input("Name: ").strip()

    email = input("Email: ").strip()

    education = input("Education: ").strip()

    skills_input = input(
        "Skills (comma separated): "
    ).strip()

    skills = [
        skill.strip()
        for skill in skills_input.split(",")
        if skill.strip()
    ]

    projects_input = input(
        "Projects (comma separated): "
    ).strip()

    projects = [
        project.strip()
        for project in projects_input.split(",")
        if project.strip()
    ]

    experience = input("Experience: ").strip()

    target_role = input("Target Role: ").strip()

    profile = {
        "name": name,
        "email": email,
        "education": education,
        "skills": skills,
        "projects": projects,
        "experience": experience,
        "target_role": target_role
    }

    print("\n")
    print("=" * 70)
    print("CANDIDATE PROFILE")
    print("=" * 70)

    print(f"Name       : {name}")
    print(f"Email      : {email}")
    print(f"Education  : {education}")
    print(f"Skills     : {', '.join(skills)}")
    print(f"Projects   : {', '.join(projects)}")
    print(f"Experience : {experience}")
    print(f"Target Role: {target_role}")

    return profile


# ============================================================
# TOPIC
# ============================================================

def get_topics():
    knowledge = load_knowledge()

    topics = sorted(
        set(
            item["topic"]
            for item in knowledge
        )
    )

    return topics


def get_concepts(topic):
    knowledge = load_knowledge()

    concepts = sorted(
        set(
            item["concept"]
            for item in knowledge
            if item["topic"].lower() == topic.lower()
        )
    )

    return concepts


def select_topic():

    topics = get_topics()

    print("\n")
    print("=" * 70)
    print("SELECT INTERVIEW TOPIC")
    print("=" * 70)

    for index, topic in enumerate(topics, start=1):
        print(f"{index}. {topic}")

    while True:

        choice = input(
            "\nEnter topic number: "
        ).strip()

        try:

            choice = int(choice)

            if 1 <= choice <= len(topics):

                selected_topic = topics[choice - 1]

                print(
                    f"\nSelected Topic: {selected_topic}"
                )

                return selected_topic

        except ValueError:
            pass

        print(
            "Invalid choice. Please enter a valid number."
        )


# ============================================================
# CONCEPTS
# ============================================================

def select_concepts(topic):

    concepts = get_concepts(topic)

    print("\n")
    print("=" * 70)
    print(f"SELECT CONCEPTS — {topic}")
    print("=" * 70)

    for index, concept in enumerate(concepts, start=1):
        print(f"{index}. {concept}")

    print("\nYou can select multiple concepts.")
    print("Example: 1,3,5")

    while True:

        choice = input(
            "\nEnter concept numbers: "
        ).strip()

        try:

            numbers = [
                int(number.strip())
                for number in choice.split(",")
            ]

            if not numbers:
                raise ValueError

            if any(
                number < 1 or number > len(concepts)
                for number in numbers
            ):
                raise ValueError

            unique_numbers = list(
                dict.fromkeys(numbers)
            )

            selected_concepts = [
                concepts[number - 1]
                for number in unique_numbers
            ]

            print("\nSelected Concepts:")

            for concept in selected_concepts:
                print(f"  - {concept}")

            return selected_concepts

        except ValueError:

            print(
                "Invalid selection. "
                "Use numbers such as 1,2,4."
            )


# ============================================================
# QUESTION TYPE
# ============================================================

def select_question_type():

    print("\n")
    print("=" * 70)
    print("SELECT QUESTION TYPE")
    print("=" * 70)

    print("1. Coding")
    print("2. Conceptual")

    while True:

        choice = input(
            "\nEnter choice: "
        ).strip()

        if choice == "1":
            return "Coding"

        if choice == "2":
            return "Conceptual"

        print(
            "Invalid choice. Enter 1 or 2."
        )


# ============================================================
# DIFFICULTY
# ============================================================

def select_difficulty():

    print("\n")
    print("=" * 70)
    print("SELECT STARTING DIFFICULTY")
    print("=" * 70)

    print("1. Easy")
    print("2. Medium")
    print("3. Hard")

    difficulty_map = {
        "1": "Easy",
        "2": "Medium",
        "3": "Hard"
    }

    while True:

        choice = input(
            "\nEnter choice: "
        ).strip()

        if choice in difficulty_map:
            return difficulty_map[choice]

        print(
            "Invalid choice. Enter 1, 2, or 3."
        )


# ============================================================
# QUESTION COUNT
# ============================================================

def select_question_count():

    print("\n")
    print("=" * 70)
    print("NUMBER OF QUESTIONS")
    print("=" * 70)

    while True:

        choice = input(
            "\nEnter number of questions: "
        ).strip()

        try:

            count = int(choice)

            if count > 0:
                return count

        except ValueError:
            pass

        print(
            "Please enter a positive number."
        )


# ============================================================
# COMPLETE INTERVIEW CONFIGURATION
# ============================================================

def get_interview_configuration():

    print("\n")
    print("=" * 70)
    print("AI INTERVIEW CONFIGURATION")
    print("=" * 70)

    # Candidate profile
    profile = collect_candidate_profile()

    # Interview settings
    topic = select_topic()

    selected_concepts = select_concepts(topic)

    question_type = select_question_type()

    starting_difficulty = select_difficulty()

    max_questions = select_question_count()

    print("\n")
    print("=" * 70)
    print("INTERVIEW CONFIGURATION")
    print("=" * 70)

    print(f"Candidate      : {profile['name']}")
    print(f"Email          : {profile['email']}")
    print(f"Target Role    : {profile['target_role']}")
    print(f"Topic          : {topic}")

    print("Selected Concepts:")

    for concept in selected_concepts:
        print(f"  - {concept}")

    print(f"Question Type  : {question_type}")
    print(f"Difficulty     : {starting_difficulty}")
    print(f"Questions      : {max_questions}")

    print("=" * 70)

    return {
        "profile": profile,
        "topic": topic,
        "selected_concepts": selected_concepts,
        "question_type": question_type,
        "starting_difficulty": starting_difficulty,
        "max_questions": max_questions
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    configuration = get_interview_configuration()

    print("\nConfiguration object:")

    print(configuration)