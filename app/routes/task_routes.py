from flask import Blueprint, abort, make_response, request, Response
from datetime import datetime, timezone
from app.models.task import Task
from ..db import db
import requests
import os

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.post("")
def create_task():
    request_body = request.get_json()

    # how can I do this in validate function
    if not request_body.get("title") or not request_body.get("description"):
        return {"details": "Invalid data"}, 400
    
    title = request_body["title"]
    description = request_body["description"]
    
    new_task = Task(title=title, description=description)

    db.session.add(new_task)
    db.session.commit()

    response = {
        "task":{
        "id": new_task.id,
        "title": new_task.title,
        "description": new_task.description,
        "is_complete": new_task.completed if new_task.completed_at is not None else False
    }}
    
    return response, 201

@tasks_bp.get("")
def get_all_tasks():
    query = db.select(Task)

    # title_param = request.args.get("title")
    sort_param = request.args.get("sort")
    # description_param = request.args.get("description")

    if sort_param == "asc":
        query = query.order_by(Task.title)

    if sort_param == "desc":
        query = query.order_by(Task.title.desc())

    # if title_param:
    #     query = query.where(Task.title.ilike(f"%{title_param}%"))

    # if description_param:
    #     query = query.where(Task.description.ilike(f"%{description_param}%"))

    query = query.order_by(Task.id)

    tasks = db.session.scalars(query)
    
    # could also be written as:
    # tasks = db.session.execute(query).scalars()

    tasks_response = []
    for task in tasks:
        tasks_response.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.completed_at if task.completed_at is not None else False
        })

    return tasks_response

@tasks_bp.get("/<task_id>")
def get_one_task(task_id):
    task = validate_task(task_id)

    return {
        "task":{
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "is_complete": task.completed_at if task.completed_at is not None else False
        }}

@tasks_bp.put("/<task_id>")
def update_task(task_id):
    task = validate_task(task_id)
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

@tasks_bp.patch("/<task_id>/mark_complete")
def mark_task_as_complete(task_id):
    task = validate_task(task_id)

    task.completed_at = datetime.now(timezone.utc)

    slack_message = f"Someone just completed the task {task.title}"

    url = os.environ.get("URL")
    slack_api_key = os.environ.get("SLACK_API_KEY")
    channel = os.environ.get("CHANNEL")
    
    headers = {"Authorization": f"Bearer {slack_api_key}", "Content-Type": "application/json"}

    data = {
        "channel": channel,
        "text": slack_message
    }

    requests.post(url, json=data, headers=headers, timeout=5)

    db.session.commit()

    response_body = {
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": True
        }
    }

    return response_body, 200

@tasks_bp.patch("/<task_id>/mark_incomplete")
def mark_task_as_incomplete(task_id):
    task = validate_task(task_id)

    task.completed_at = None

    db.session.commit()

    response_body = {
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": False
        }
    }
    return response_body, 200

@tasks_bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_task(task_id)

    db.session.delete(task)
    db.session.commit()

    response_body = f'{{"details": "Task {task_id} \\"{task.title}\\" successfully deleted"}}'

    return Response(
        response_body,
        status=200,
        mimetype="application/json"
    )

def validate_task(task_id):
    try:
        task_id = int(task_id)
    except:
        response = {"message": f"invalid task id"}
        abort(make_response(response, 400))

    query = db.select(Task).where(Task.id == task_id)
    task = db.session.scalar(query)

    if not task:
        response = {"message": f"task not found"}
        abort(make_response(response, 404))
        
    return task

# may want to create to_dict function later