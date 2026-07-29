import json
from langchain_core.messages import HumanMessage
from llm import llm

def extract_resume_information(resume_text):

    prompt = f'''
You are an ATS resume parser.

Extract information from the resume.

Return ONLY valid JSON.

JSON format:

{{
  "name": "",
  "skills": [],
  "location": "",
  "category": ""
}}

Rules:
- name = candidate full name
- skills = technical + professional skills
- location = city or country
- category = one job category only
- Do not include explanations.

Resume:
{resume_text}
'''

    try:
        response = llm.invoke(
            [HumanMessage(content=prompt)]
        )

        content = response.content.strip()

        content = content.replace("```json", "")
        content = content.replace("```", "").strip()

        return json.loads(content)

    except Exception as e:
        print("LLM extraction failed:", e)

        return {
            "name": "",
            "skills": [],
            "location": "Unknown",
            "category": "General"
        }