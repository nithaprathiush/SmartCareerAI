# utils/career_recommender.py

import pandas as pd

from utils.skill_extraction_JD import (
    normalize_term
)


# =====================================================
# LOAD CAREER DATA
# =====================================================
def load_career_data(csv_path):

    df = pd.read_csv(csv_path)

    return df


# =====================================================
# GET ROLE SKILLS
# =====================================================
def get_role_skills(row):

    skills = []

    # ---------------------------------------------
    # required technical skills
    # ---------------------------------------------
    if pd.notna(
        row.get("required_technical_skills")
    ):

        skills.extend(

            str(
                row[
                    "required_technical_skills"
                ]
            ).split(",")
        )

    # ---------------------------------------------
    # tools & technologies
    # ---------------------------------------------
    if pd.notna(
        row.get("tools_technologies")
    ):

        skills.extend(

            str(
                row[
                    "tools_technologies"
                ]
            ).split(",")
        )

    # normalize
    skills = [

        normalize_term(skill)

        for skill in skills

        if str(skill).strip()
    ]

    return sorted(set(skills))


# =====================================================
# CAREER RECOMMENDATION
# =====================================================
def recommend_careers(

    resume_skills,
    career_df,
    threshold=60
):

    recommendations = []

    # normalize resume skills
    resume_skills = set([

        normalize_term(skill)

        for skill in resume_skills
    ])

    # -------------------------------------------------
    # iterate through all job roles
    # -------------------------------------------------
    for _, row in career_df.iterrows():

        role = row["job_title"]

        role_skills = set(
            get_role_skills(row)
        )

        if not role_skills:
            continue

        # matched skills
        matched = resume_skills.intersection(
            role_skills
        )

        # similarity %
        similarity = (

            len(matched)
            / len(role_skills)

        ) * 100

        similarity = round(
            similarity,
            2
        )

        # threshold filter
        if similarity >= threshold:

            recommendations.append({

                "job_title": role,

                "similarity": similarity,

                "matched_skills": sorted(
                    matched
                ),

                "missing_skills": sorted(

                    role_skills.difference(
                        matched
                    )
                )
            })

    # -------------------------------------------------
    # sort descending
    # -------------------------------------------------
    recommendations = sorted(

        recommendations,

        key=lambda x: x["similarity"],

        reverse=True
    )

    return recommendations[:10]