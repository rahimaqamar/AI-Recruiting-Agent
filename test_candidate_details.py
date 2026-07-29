import requests
import json

BASE_URL = "http://127.0.0.1:8000"


def test_candidate_detail():

    candidate_id = 913

    url = f"{BASE_URL}/resumes/{candidate_id}"

    response = requests.get(url)

    print("\nSTATUS:", response.status_code)

    print("\nRESPONSE:")
    print(json.dumps(response.json(), indent=4))


if __name__ == "__main__":
    test_candidate_detail()