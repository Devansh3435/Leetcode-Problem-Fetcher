from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# Cached problem mapping (could be stored in a database)
problems_cache = {}

# Function to fetch all problems and cache the mapping
def fetch_all_problems():
    url = "https://leetcode.com/graphql/"
    payload = {
        "query": """
        query {
            problemsetQuestionListV2 {
                questions {
                    questionFrontendId
                    title
                    titleSlug
                    difficulty
                    topicTags {
                        name
                    }
                }
            }
        }
        """,
        "variables": {}
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        for question in data['data']['problemsetQuestionListV2']['questions']:
            problems_cache[question['questionFrontendId']] = question
    else:
        raise Exception("Failed to fetch problems list")

# Function to fetch problem details by titleSlug
def fetch_problem_details(title_slug):
    url = "https://leetcode.com/graphql/"
    payload = {
        "query": """
        query getQuestionDetails($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                title
                content
                difficulty
                topicTags {
                    name
                }
            }
        }
        """,
        "variables": {"titleSlug": title_slug}
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get('data', {}).get('question', {})
    else:
        return {"error": f"Failed to fetch problem details: {response.text}"}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_problem", methods=["POST"])
def get_problem():
    data = request.json
    question_frontend_id = data.get("questionFrontendId")
    if question_frontend_id not in problems_cache:
        return jsonify({"error": "Invalid questionFrontendId or cache not updated."}), 404

    # Get titleSlug from cached problems
    question_data = problems_cache[question_frontend_id]
    title_slug = question_data['titleSlug']

    # Fetch full problem details based on titleSlug
    problem_details = fetch_problem_details(title_slug)
    return jsonify(problem_details)

if __name__ == "__main__":
    # Fetch problems on startup
    fetch_all_problems()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
