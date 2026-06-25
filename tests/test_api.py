from unittest.mock import patch

from fastapi.testclient import TestClient

import api


client = TestClient(api.app)


@patch("query.ask_question")
def test_query_endpoint_returns_answer_and_citations(mock_ask):
    mock_ask.return_value = {
        "answer": "Concrete must cure for seven days.",
        "rewritten_query": "concrete curing requirements",
        "citations": [
            {
                "section": "90-1.02C",
                "title": "Concrete Requirements",
                "page": 12,
                "snippet": "Concrete shall cure for at least seven days.",
            }
        ],
    }

    response = client.post(
        "/query",
        json={"question": "What are concrete curing requirements?"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"].startswith("Concrete must cure")
    assert payload["rewritten_query"] == "concrete curing requirements"
    assert payload["citations"][0]["section"] == "90-1.02C"


def test_home_endpoint_reports_service_name():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["service"] == "transport-spec-rag-ai"
