# utils/resume_parser.py

import docx
import PyPDF2


# =====================================================
# READ PDF
# =====================================================
def read_pdf(file):

    text = ""

    try:

        reader = PyPDF2.PdfReader(file)

        for page in reader.pages:

            extracted = page.extract_text()

            if extracted:
                text += extracted + "\n"

    except Exception as e:

        print(f"PDF Reading Error: {e}")

    return text.strip()


# =====================================================
# READ DOCX
# =====================================================
def read_docx(file):

    text = ""

    try:

        doc = docx.Document(file)

        paragraphs = [
            para.text
            for para in doc.paragraphs
            if para.text.strip()
        ]

        text = "\n".join(paragraphs)

    except Exception as e:

        print(f"DOCX Reading Error: {e}")

    return text.strip()


# =====================================================
# EXTRACT RESUME TEXT
# =====================================================
def extract_resume_text(uploaded_file):

    if uploaded_file is None:
        return ""

    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):

        return read_pdf(uploaded_file)

    elif filename.endswith(".docx"):

        return read_docx(uploaded_file)

    else:

        return ""