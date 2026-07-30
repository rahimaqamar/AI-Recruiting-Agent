import os
import requests

URL = "http://127.0.0.1:8000/resumes"

folder = "sample_resumes"

for root, dirs, files in os.walk(folder):

    for file in files:

        if file.endswith(".pdf"):

            path = os.path.join(root, file)

            with open(path, "rb") as f:

                requests.post(
                    URL,
                    files={
                        "file": f
                    }
                )

            print(file, "uploaded")