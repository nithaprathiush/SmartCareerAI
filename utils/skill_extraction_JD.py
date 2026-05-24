# utils/skill_extraction_JD.py

import pandas as pd
import spacy
import re

from functools import lru_cache
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# =========================================================
# LOAD SPACY MODEL
# =========================================================
nlp = spacy.load("en_core_web_sm")


# =========================================================
# LOAD SENTENCE TRANSFORMER MODEL
# =========================================================
@lru_cache()
def get_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


# =========================================================
# NORMALIZATION MAP
# =========================================================
NORMALIZATION_MAP = {

    # cloud
    "gcp": "google cloud platform",
    "aws cloud": "aws",
    "azure cloud": "azure",

    # power bi
    "powerbi": "power bi",
    "power-bi": "power bi",

    # javascript
    "js": "javascript",
    "nodejs": "node.js",
    "reactjs": "react.js",

    # ml/ai
    "ml": "machine learning",
    "dl": "deep learning",
    "tf": "tensorflow",
    "huggingface": "hugging face",
    "hugging face transformers": "hugging face",

    # databases
    "postgres": "postgresql",
    "mongo": "mongodb",

    # misc
    "ms excel": "excel"
}


# =========================================================
# IGNORE VERY GENERIC TERMS
# =========================================================
IGNORE_SKILLS = {
    "r",
    "c",
    "go"
}


# =========================================================
# NORMALIZE TERM
# =========================================================
def normalize_term(term):

    term = str(term).lower().strip()

    term = re.sub(r"\s+", " ", term)

    return NORMALIZATION_MAP.get(term, term)


# =========================================================
# REMOVE REDUNDANT / OVERLAPPING SKILLS
# =========================================================
def remove_redundant_skills(skills):

    # sort by shortest first
    skills = sorted(skills, key=len)

    filtered_skills = []

    for skill in skills:

        is_redundant = False

        for existing_skill in filtered_skills:

            # Example:
            # machine learning IN machine learning algorithms
            if existing_skill in skill:

                is_redundant = True
                break

        if not is_redundant:
            filtered_skills.append(skill)

    return filtered_skills


# =========================================================
# CLEAN TEXT
# =========================================================
def clean_text(text):

    text = text.lower()

    # preserve important symbols
    text = re.sub(r"[^a-zA-Z0-9+#./_-]", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =========================================================
# LOAD SKILLS
# COMBINE:
# - required_technical_skills
# - tools_technologies
# =========================================================
def load_skills(csv_path):

    df = pd.read_csv(csv_path)

    all_skills = []

    # -----------------------------------------------------
    # REQUIRED TECHNICAL SKILLS
    # -----------------------------------------------------
    if "required_technical_skills" in df.columns:

        tech_skills = df["required_technical_skills"].dropna()

        for item in tech_skills:

            for skill in str(item).split(","):

                skill = normalize_term(skill)

                if (
                    len(skill) > 1
                    and skill not in IGNORE_SKILLS
                ):
                    all_skills.append(skill)

    # -----------------------------------------------------
    # TOOLS & TECHNOLOGIES
    # -----------------------------------------------------
    if "tools_technologies" in df.columns:

        tools = df["tools_technologies"].dropna()

        for item in tools:

            for skill in str(item).split(","):

                skill = normalize_term(skill)

                if (
                    len(skill) > 1
                    and skill not in IGNORE_SKILLS
                ):
                    all_skills.append(skill)

    # -----------------------------------------------------
    # REMOVE DUPLICATES
    # -----------------------------------------------------
    all_skills = sorted(set(all_skills))

    return all_skills


# =========================================================
# MAIN EXTRACTION FUNCTION
# =========================================================
def extract_skills_from_jd(
    job_description,
    skill_list,
    threshold=0.72
):

    model = get_model()

    # -----------------------------------------------------
    # CLEAN JD
    # -----------------------------------------------------
    jd_clean = clean_text(job_description)

    # -----------------------------------------------------
    # APPLY NORMALIZATION
    # -----------------------------------------------------
    for alias, actual in NORMALIZATION_MAP.items():

        jd_clean = jd_clean.replace(alias, actual)

    matched_skills = set()

    # =====================================================
    # STEP 1 → EXACT MATCHING
    # =====================================================
    for skill in skill_list:

        if skill in IGNORE_SKILLS:
            continue

        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, jd_clean):
            matched_skills.add(skill)

    # =====================================================
    # STEP 2 → NLP PHRASE EXTRACTION
    # =====================================================
    doc = nlp(jd_clean)

    candidate_phrases = set()

    # noun chunks
    for chunk in doc.noun_chunks:

        phrase = normalize_term(chunk.text)

        if len(phrase) > 2:
            candidate_phrases.add(phrase)

    # entities
    for ent in doc.ents:

        phrase = normalize_term(ent.text)

        if len(phrase) > 2:
            candidate_phrases.add(phrase)

    # =====================================================
    # STEP 3 → SEMANTIC SIMILARITY FALLBACK
    # =====================================================
    remaining_skills = [
        skill for skill in skill_list
        if skill not in matched_skills
    ]

    if candidate_phrases and remaining_skills:

        skill_embeddings = model.encode(
            remaining_skills,
            show_progress_bar=False
        )

        phrase_embeddings = model.encode(
            list(candidate_phrases),
            show_progress_bar=False
        )

        similarities = cosine_similarity(
            skill_embeddings,
            phrase_embeddings
        )

        for i, skill in enumerate(remaining_skills):

            best_score = similarities[i].max()

            if best_score >= threshold:
                matched_skills.add(skill)

    # =====================================================
    # FINAL CLEANUP
    # =====================================================
    final_skills = sorted(set(
    normalize_term(skill)
    for skill in matched_skills
    if skill not in IGNORE_SKILLS
    ))

    # remove redundant skills
    final_skills = remove_redundant_skills(
        final_skills
    )

    return final_skills