# app.py

import streamlit as st

from utils.resume_parser import (
    extract_resume_text
)

from utils.skill_extraction_JD import (
    load_skills,
    extract_skills_from_jd
)

from utils.skill_gap_analysis import (
    calculate_skill_gap
)

from utils.career_recommender import (
    load_career_data,
    recommend_careers
)


# =====================================================
# LOAD SKILLS
# =====================================================
@st.cache_resource
def get_skills():

    return load_skills(
        "data/job_titles_skillsets.csv"
    )


# =====================================================
# LOAD CAREER DATA
# =====================================================
@st.cache_resource
def get_career_data():

    return load_career_data(
        "data/job_titles_skillsets.csv"
    )


skill_list = get_skills()

career_df = get_career_data()


# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Smart Career AI",
    layout="wide"
)


# =====================================================
# TITLE
# =====================================================
st.title("📊 Skill Gap Analyzer & Career Recommender")


st.markdown("""
Analyze resume skills against Job Description
and get career recommendations.
""")


# =====================================================
# RESUME UPLOAD
# =====================================================
uploaded_file = st.file_uploader(
    "Upload Resume",
    type=["pdf", "docx"]
)

resume_text = ""

resume_skills = []

if uploaded_file:

    resume_text = extract_resume_text(
        uploaded_file
    )

    st.success(
        "✅ Resume uploaded successfully!"
    )

    # extract resume skills
    resume_skills = extract_skills_from_jd(
        resume_text,
        skill_list
    )


# =====================================================
# JD INPUT
# =====================================================
jd_text = st.text_area(
    "Paste Job Description",
    height=300
)


# =====================================================
# BUTTONS
# =====================================================
#col1, col2 = st.columns(2)
col1, col2, col3 = st.columns([1,1,4])

# skill_gap_clicked = col1.button(
#     "📈 Analyze Skill Gap"
# )

# career_clicked = col2.button(
#     "🚀 Recommend Career Path"
# )

with col1:
    skill_gap_clicked = st.button(
        "📈 Analyze Skill Gap"
    )

with col2:
    career_clicked = st.button(
        "🚀 Recommend Career Path"
    )

# =====================================================
# SKILL GAP ANALYSIS
# =====================================================
if skill_gap_clicked:

    if not uploaded_file:

        st.warning(
            "Please upload resume."
        )

    elif not jd_text.strip():

        st.warning(
            "Please paste Job Description."
        )

    else:

        # JD skills
        jd_skills = extract_skills_from_jd(
            jd_text,
            skill_list
        )

        # compare
        result = calculate_skill_gap(
            jd_skills,
            resume_skills
        )

        similarity = result["similarity"]

        matched_skills = result[
            "matched_skills"
        ]

        missing_skills = result[
            "missing_skills"
        ]

        # score
        st.subheader(
            "📈 Resume Match Score"
        )

        st.progress(similarity / 100)

        st.metric(
            "Similarity %",
            f"{similarity}%"
        )

        # matched
        st.subheader(
            "✅ Skills Found in Resume"
        )

        cols = st.columns(3)

        for idx, skill in enumerate(
            matched_skills
        ):

            cols[idx % 3].success(skill)

        # missing
        st.subheader(
            "❌ Missing Skills"
        )

        cols = st.columns(3)

        for idx, skill in enumerate(
            missing_skills
        ):

            cols[idx % 3].error(skill)


# =====================================================
# CAREER RECOMMENDATION
# =====================================================
if career_clicked:

    if not uploaded_file:

        st.warning(
            "Please upload resume."
        )

    else:

        recommendations = recommend_careers(
            resume_skills,
            career_df,
            threshold=60
        )

        st.subheader(
            "🚀 Recommended Career Paths"
        )

        if recommendations:

            for rec in recommendations:

                with st.container():

                    st.markdown("---")

                    st.subheader(
                        rec["job_title"]
                    )

                    st.metric(
                        "Similarity",
                        f'{rec["similarity"]}%'
                    )

                    # matched skills
                    st.markdown(
                        "### ✅ Matching Skills"
                    )

                    cols1 = st.columns(3)

                    for idx, skill in enumerate(
                        rec["matched_skills"]
                    ):

                        cols1[idx % 3].success(
                            skill
                        )

                    # missing skills
                    st.markdown(
                        "### ❌ Missing Skills"
                    )

                    cols2 = st.columns(3)

                    for idx, skill in enumerate(
                        rec["missing_skills"]
                    ):

                        cols2[idx % 3].error(
                            skill
                        )

        else:

            st.warning(
                "No suitable career paths found."
            )