import pandas as pd
import spacy

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Load and preprocess dataset
df = pd.read_csv("FinalDB.csv")

df["fee"] = pd.to_numeric(df["fee"], errors="coerce")
df["type"] = df["type"].str.strip()
df["scholarship"] = df["scholarship"].map({"yes": True, "no": False})
df["location"] = df["location"].str.replace("\xa0", " ", regex=False)
df["domain"] = df["domain"].str.strip()
df["course"] = df["course"].str.strip()

# Filter engineering and B.Tech/M.Tech
df = df[
    (df["domain"].str.lower() == "engineering and technology")
    & (df["course"].str.lower().isin(["b.tech", "m.tech"]))
]

# Define questions
questions = [
    ("location", "Which city or state do you prefer for your college?"),
    ("specialization", "Which engineering specialization interests you most?"),
    ("course", "Would you like to pursue B.Tech or M.Tech?"),
    ("fee", "What's your maximum budget (in INR)?"),
    ("exam", "Which entrance exam did you take (JEE, GATE, etc.)?"),
    ("marks", "What was your rank or marks in the exam?"),
    ("type", "Do you prefer a government or private institution?"),
    ("accreditation", "Any specific accreditation required?"),
    ("scholarship", "Do you need scholarship support?"),
    (
        "facilities",
        "List any facilities important to you (e.g., hostel, library, sports):",
    ),
]


# Extract user intent from input
def extract_intent(question_key, user_response):
    doc = nlp(user_response.lower())
    if question_key in ["fee", "marks"]:
        for ent in doc.ents:
            if ent.label_ in ["CARDINAL", "MONEY"]:
                return float(ent.text.replace("₹", "").replace(",", "").strip())
        return float("".join(filter(str.isdigit, user_response)))

    if question_key == "facilities":
        return [chunk.text.strip() for chunk in doc.noun_chunks]

    return user_response.strip()


# Calculate relevancy scores
def calculate_relevancy(user_input):
    scores = []
    for _, row in df.iterrows():
        score = 0

        # Base scoring for location, domain, specialization, course, fee etc.
        score += 30 if user_input["location"].lower() in row["location"].lower() else 0
        score += 10 if row["domain"].lower() == "engineering and technology" else 0
        score += (
            20
            if user_input["specialization"].lower()
            in row.get("specialization", "").lower()
            else 0
        )
        score += 10 if user_input["course"].lower() == row["course"].lower() else 0
        score += (
            10 if row["fee"] != "" and float(row["fee"]) <= user_input["fee"] else 0
        )
        score += (
            10
            if user_input["exam"].lower() in row.get("relevant_exam", "").lower()
            else 0
        )

        # Dynamic scoring for marks / exam criteria
        exam = user_input["exam"].lower()
        user_marks = user_input["marks"]

        try:
            # Interpret the min_marks as either a percentile (for GATE) or a rank/cutoff (for JEE)
            college_cutoff = float(row.get("min_marks", ""))
        except:
            college_cutoff = None

        if college_cutoff is not None:
            if "gate" in exam:
                # For GATE: a higher percentile is desirable.
                if user_marks >= college_cutoff:
                    score += 10
            elif "jee" in exam:
                # For JEE: a lower rank is desirable.
                if user_marks <= college_cutoff:
                    score += 10
            else:
                # Generic check for other exams
                if user_marks >= college_cutoff:
                    score += 5

        # Additional filters for type, accreditation and scholarship.
        score += 5 if user_input["type"].lower() == row["type"].lower() else 0
        score += (
            5
            if user_input["accreditation"].lower() in row["accreditation"].lower()
            else 0
        )
        score += (
            5
            if str(user_input["scholarship"]).lower() == str(row["scholarship"]).lower()
            else 0
        )

        # Facilities matching: calculate fraction overlap
        user_facilities = set(user_input["facilities"])
        college_facilities = set(str(row.get("facilities", "")).lower().split(","))
        facilities_score = (
            (len(user_facilities & college_facilities) / len(user_facilities)) * 5
            if user_facilities
            else 0
        )
        score += facilities_score

        scores.append(score)

    df["relevancy"] = scores
    # Return the top 5 colleges with highest relevancy score
    return df.sort_values(by="relevancy", ascending=False).head(5)


# Export variables/functions for app.py
__all__ = ["questions", "extract_intent", "calculate_relevancy"]
