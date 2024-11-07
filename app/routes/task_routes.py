from flask import Blueprint, abort, make_response, request, Response
from datetime import datetime, timezone
from app.models.task import Task
from .route_utilities import validate_model
from ..db import db
import requests
import os

# will create blueprint for tasks endpoints
tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

# will create/post a new task
@tasks_bp.post("")
def create_task():
    # turning json into python dict
    request_body = request.get_json()

    # if the request body is missing title or description, will return 400
    if not request_body.get("title") or not request_body.get("description"):
        return {"details": "Invalid data"}, 400
    
    title = request_body["title"]
    description = request_body["description"]
    
    # creates a new task with info from request_body
    new_task = Task(title=title, description=description)

    # adds and saves the created task to the db
    db.session.add(new_task)
    db.session.commit()

    # creates the response that is sent back to user which changes None to False for "is_complete"
    response = {
        "task":{
        "id": new_task.id,
        "title": new_task.title,
        "description": new_task.description,
        "is_complete": new_task.completed if new_task.completed_at is not None else False
    }}
    
    return response, 201

# gets a list of all tasks
@tasks_bp.get("")
def get_all_tasks():
    # selects all the records for tasks
    query = db.select(Task)

    # creates a variable sort_param if "sort" is in the url
    sort_param = request.args.get("sort")

    # if the sort_param is "asc" then it lists the tasks 
    # in ascending alphabetical order by title
    if sort_param == "asc":
        query = query.order_by(Task.title)

    # if the sort_param is "desc" then it lists the tasks 
    # in descending alphabetical order by title
    if sort_param == "desc":
        query = query.order_by(Task.title.desc())

    # creates a variable title_param if "title" is in the url
    title_param = request.args.get("title")

    # if there is a title_param than look for the title_param in the title of the tasks
    if title_param:
        query = query.where(Task.title.ilike(f"%{title_param}%"))

    # description_param = request.args.get("description")

    # if description_param:
    #     query = query.where(Task.description.ilike(f"%{description_param}%"))

    # orders the tasks by id
    query = query.order_by(Task.id)

    # actually retrieves all the tasks and puts them into tasks variable
    tasks = db.session.scalars(query)

    # puts together all the tasks into a list of dictionaries to send as response to user
    # again changing "is_complete" to False if its None/not completed
    tasks_response = []
    for task in tasks:
        tasks_response.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.completed_at if task.completed_at is not None else False
        })

    return tasks_response

# get a specific task based on task_id
@tasks_bp.get("/<task_id>")
def get_one_task(task_id):
    # handles data validation and error responses as needed
    task = validate_model(Task, task_id)

    # puts together the task into a dictionary to send as response to user
    # again changing "is_complete" to False if its None/not completed
    task_response = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "is_complete": task.completed_at if task.completed_at is not None else False
    }

    # if it has a goal_id it will add it to the dictionary above
    if task.goal_id:
        task_response["goal_id"] = task.goal_id

    return {"task": task_response}

# replaces the information of the task with 
# corresponding task_id based on information submitted.
@tasks_bp.put("/<task_id>")
def update_task(task_id):
    # handles data validation and error responses as needed
    task = validate_model(Task, task_id)

    # turning json into python dict
    request_body = request.get_json()

    task.title = request_body["title"]
    task.description = request_body["description"]

    db.session.commit()
    
    response_body = {
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.completed if task.completed_at is not None else False
        }
    }
    return response_body, 200

# will mark a task as completed
@tasks_bp.patch("/<task_id>/mark_complete")
def mark_task_as_complete(task_id):
    # handles data validation and error responses as needed
    task = validate_model(Task, task_id)

    # changes the tasks "completed_at" value to the date and time it was marked completed
    task.completed_at = datetime.now(timezone.utc)

    # puts together the message we want slack api to post when task marked as completed
    slack_message = f"Someone just completed the task {task.title}"

    # builds the pieces of the api call info from the .env variables
    url = os.environ.get("URL")
    slack_api_key = os.environ.get("SLACK_API_KEY")
    channel = os.environ.get("CHANNEL")
    
    # builds the header for the api call
    headers = {"Authorization": f"Bearer {slack_api_key}", "Content-Type": "application/json"}

    # builds the data for the api call
    data = {
        "channel": channel,
        "text": slack_message
    }
    # does a post on the slack api call putting together the pieces we had previously built
    requests.post(url, json=data, headers=headers, timeout=5)

    # saves the change on the db
    db.session.commit()

    # builds a dict for the response that reflects "is_complete" as True
    response_body = {
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": True
        }
    }

    return response_body, 200

# will mark a task as incomplete
@tasks_bp.patch("/<task_id>/mark_incomplete")
def mark_task_as_incomplete(task_id):
    # handles data validation and error responses as needed
    task = validate_model(Task, task_id)

    # changes task's completed_at to None since being marked as incomplete
    task.completed_at = None

    # saves this change to db
    db.session.commit()

    # build dict response body that reflects complete as False
    response_body = {
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": False
        }
    }
    return response_body, 200

# will delete a task
@tasks_bp.delete("/<task_id>")
def delete_task(task_id):
    # handles data validation and error responses as needed
    task = validate_model(Task, task_id)

    db.session.delete(task)
    db.session.commit()

    response_body = f'{{"details": "Task {task_id} \\"{task.title}\\" successfully deleted"}}'

    return Response(
        response_body,
        status=200,
        mimetype="application/json"
    )