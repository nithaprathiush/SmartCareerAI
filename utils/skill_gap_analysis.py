# utils/skill_gap_analysis.py


# =========================================================
# COMPARE JD SKILLS VS RESUME SKILLS
# =========================================================
def calculate_skill_gap(
    jd_skills,
    resume_skills
):

    jd_skills_set = set(
        skill.lower().strip()
        for skill in jd_skills
    )

    resume_skills_set = set(
        skill.lower().strip()
        for skill in resume_skills
    )

    # matched skills
    matched_skills = sorted(
        jd_skills_set.intersection(
            resume_skills_set
        )
    )

    # missing skills
    missing_skills = sorted(
        jd_skills_set.difference(
            resume_skills_set
        )
    )

    # similarity %
    if len(jd_skills_set) > 0:

        similarity = round(
            (
                len(matched_skills)
                / len(jd_skills_set)
            ) * 100,
            2
        )

    else:

        similarity = 0

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "similarity": similarity
    }