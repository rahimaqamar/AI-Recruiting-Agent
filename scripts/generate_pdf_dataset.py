import os
import pandas as pd

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# Read dataset
df = pd.read_csv("data/dataset/Resume.csv")

# Folder where PDFs will be created
OUTPUT_FOLDER = "data/resumes"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

styles = getSampleStyleSheet()

for index, row in df.iterrows():

    resume_text = str(row["Resume_str"])

    category = str(row["Category"])

    pdf_name = f"{category}_{index+1}.pdf"

    pdf_path = os.path.join(OUTPUT_FOLDER, pdf_name)

    document = SimpleDocTemplate(pdf_path, pagesize=A4)

    story = []

    # Heading
    story.append(
        Paragraph(
            f"<b>Category:</b> {category}",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            resume_text.replace("\n", "<br/>"),
            styles["BodyText"]
        )
    )

    document.build(story)

print("Finished!")
print(f"Generated {len(df)} PDF resumes.")