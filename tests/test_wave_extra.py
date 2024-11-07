import pytest

#EXTRA GOALS TESTS
def test_get_goals_sorted_asc(client, three_goals):
    # Act
    response = client.get("/goals?sort=asc")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert len(response_body) == 3
    assert response_body == [
        {"id": 3, "title": "Be debt-free"},
        {"id": 1, "title": "Embrace the gardening life"},
        {"id": 2, "title": "Self-care"}
        ]

def test_get_goals_sorted_desc(client, three_goals):
    # Act
    response = client.get("/goals?sort=desc")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert len(response_body) == 3
    assert response_body == [
        {"id": 2, "title": "Self-care"},
        {"id": 1, "title": "Embrace the gardening life"},
        {"id": 3, "title": "Be debt-free"}]

def test_get_goals_filter_title(client, three_goals):
    # Act
    response = client.get("/goals?title=garden")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert len(response_body) == 1
    assert response_body == [{"id": 1, "title": "Embrace the gardening life"}]

# EXTRA TASKS TESTS
def test_get_tasks_filter_title(client, three_tasks):
    # Act
    response = client.get("/tasks?title=garden")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert len(response_body) == 1
    assert response_body == [{
            "description": "",
            "id": 1,
            "is_complete": False,
            "title": "Water the garden 🌷"}]
    
# def test_get_tasks_filter_description(client, three_tasks):
#     # Act
#     response = client.get("/tasks?description=tickets")
#     response_body = response.get_json()

#     # Assert
#     assert response.status_code == 200
#     assert len(response_body) == 1
#     assert response_body == [{
#             "description": "",
#             "id": 3,
#             "is_complete": False,
#             "title": "Pay my outstanding tickets 😭"}]



