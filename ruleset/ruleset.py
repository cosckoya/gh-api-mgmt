import os
import json
import requests

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
API_VERSION = "2026-03-10"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "X-GitHub-Api-Version": API_VERSION,
}

BASE_URL = "https://api.github.com"


def create_ruleset(owner: str, repo: str, ruleset: dict) -> dict:
    url = f"{BASE_URL}/repos/{owner}/{repo}/rulesets"
    response = requests.post(url, headers=HEADERS, json=ruleset)
    response.raise_for_status()
    return response.json()


def list_rulesets(owner: str, repo: str) -> list:
    url = f"{BASE_URL}/repos/{owner}/{repo}/rulesets"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def delete_ruleset(owner: str, repo: str, ruleset_id: int) -> None:
    url = f"{BASE_URL}/repos/{owner}/{repo}/rulesets/{ruleset_id}"
    response = requests.delete(url, headers=HEADERS)
    response.raise_for_status()


# --- Uso ---
BASELINE_RULESET = {
    "name": "baseline-protect-default",
    "target": "branch",
    "enforcement": "active",
    "conditions": {
        "ref_name": {
            "include": ["~DEFAULT_BRANCH"],
            "exclude": []
        }
    },
    "rules": [
        {"type": "deletion"},
        {"type": "non_fast_forward"},
        {
            "type": "pull_request",
            "parameters": {
                "required_approving_review_count": 1,
                "dismiss_stale_reviews_on_push": True,
                "require_last_push_approval": True,
                "require_code_owner_review": False,
                "required_review_thread_resolution": True,
                "allowed_merge_methods": ["squash", "rebase"]
            }
        }
    ],
    "bypass_actors": [
        {
            "actor_id": 5,          # Admin role
            "actor_type": "RepositoryRole",
            "bypass_mode": "always"
        }
    ]
}

if __name__ == "__main__":
    result = create_ruleset("myorg", "my-repo", BASELINE_RULESET)
    print(f"Ruleset created: id={result['id']} name={result['name']}")
