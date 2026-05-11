import requests


def get_random_question(year_subject: str, api_url: str) -> dict:
    """
    Fetch a random exam question from the exam API.
    Returns dict with 'question' and 'answer' keys.
    """
    response = requests.post(
        api_url,
        json={"year_subject": year_subject},
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()
