import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("NEWS_API_KEY")

url = (
    f"https://newsapi.org/v2/everything?"
    f"q=india economy OR RBI OR inflation OR GDP"
    f"&language=en"
    f"&sortBy=publishedAt"
    f"&apiKey={api_key}"
)

response = requests.get(url)

print("Status Code:", response.status_code)

data = response.json()

print("Status:", data.get("status"))
print("Total Results:", data.get("totalResults"))

articles = data.get("articles", [])

if articles:
    print("\nFirst Article:")
    print(articles[0]["title"])