from flask import Blueprint, abort, make_response, request, Response
from datetime import datetime, timezone
from .route_utilities import validate_model
from app.models.goal import Goal
from app.models.task import Task
from ..db import db

# creates the blueprint for our endpoints.
goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

# will post/create a new goal
@goals_bp.post("")
def create_goal():
    # turning json into python dict
    request_body = request.get_json()

    # if the request_body doesn't have a title returns error
    if not request_body.get("title"):
        return {"details": "Invalid data"}, 400
    
    title = request_body["title"]
    
    # creates new goal with title from request_body
    new_goal = Goal(title=title)

    # adds and saves that new goal to db
    db.session.add(new_goal)
    db.session.commit()

    # puts together dict response with new goal id and title
    response = {
        "goal":{
        "id": new_goal.id,
        "title": new_goal.title,
    }}
    
    return response, 201

# will post/create a new task linked to the goal id inputted.
@goals_bp.post("/<goal_id>/tasks")
def create_task_with_goal(goal_id):
    # turning json into python dict
    request_body = request.get_json()

    if not request_body.get("task_ids") or not isinstance(request_body["task_ids"], list):
        return {"details": "Invalid data"}, 400

    # will get the goal with goal_id from database
    goal = Goal.query.get(goal_id)

    # not sure if this would be wanted or needed
    # if not goal:
    #     return {"message": f"Goal with id {goal_id} not found"}, 404

    # creates an empty list to put the task_ids into
    new_task_ids = []
    
    # for each task_id in the request body, it will find that in the db 
    # and if task exists than it will add the ids from that task to new_task_ids list
    for task_id in request_body["task_ids"]:
        task = Task.query.get(task_id)
        if task:
            task.goal = goal  
            new_task_ids.append(task.id)  

    # it will save those changes of linking the task and id to the db
    db.session.commit()

    # builds a dictionary that will show the goal_id 
    # and list of all task ids associated/linked to that goal
    response = {
        "id": goal.id,
        "task_ids": new_task_ids  
    }

    return response, 200

# will get a list of all goals.
@goals_bp.get("")
def get_all_goals():
    # this will select all the goals 
    query = db.select(Goal)

    title_param = request.args.get("title")

    if title_param:
        query = query.where(Goal.title.ilike(f"%{title_param}%"))
    
    sort_param = request.args.get("sort")
    
    if sort_param == "asc":
        query = query.order_by(Goal.title)
    
    if sort_param == "desc":
        query = query.order_by(Goal.title.desc())
    
    # this will order the goals by goal_id
    query = query.order_by(Goal.id)

    # this will retrieve all those goals we selected into variable named goals
    goals = db.session.scalars(query)

    goals_response = []

    # builds a dict that will have a list of all the goals with their id and title
    for goal in goals:
        goals_response.append({
            "id": goal.id,
            "title": goal.title,
        })

    return goals_response

# will get the goal related to goal_id inputted.
@goals_bp.get("/<goal_id>")
def get_one_goal(goal_id):
    # handles data validation and error responses as needed
    goal = validate_model(Goal, goal_id)

    # returns dict of the specific goal selected
    return {
        "goal":{
        "id": goal.id,
        "title": goal.title,
        }}

# will get all the tasks associated with the goal_id inputted.
@goals_bp.get("/<goal_id>/tasks")
def get_tasks_by_goal(goal_id):
    # handles data validation and error responses as needed
    goal = validate_model(Goal, goal_id)
    
    # selects and retrieves all the tasks that have a goal_id 
    # that matches the goal_id that was inputted
    tasks = Task.query.where(Task.goal_id == goal_id)

    task_list = []
    
    # builds a dict for each of the tasks associated with the goal_id and adds it to task_list
    for task in tasks:
            task_list.append({
                "id": task.id,
                "goal_id": goal.id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.completed_at is not None
                })
        
    response_body = {
        "id": goal.id,
        "title": goal.title, 
        "tasks": task_list
    }

    return response_body, 200

# will replace the information associated with this goal id to the new info that was inputted.
@goals_bp.put("/<goal_id>")
def update_goal(goal_id):
    # handles data validation and error responses as needed
    goal = validate_model(Goal, goal_id)

    # turning json into python dict
    request_body = request.get_json()

    goal.title = request_body["title"]

    db.session.commit()
    
    response_body = {
            "goal": {
            "id": goal.id,
            "title": goal.title
        }}
    
    return response_body, 200

# will delete the goal associated with goal_id
@goals_bp.delete("/<goal_id>")
def delete_goal(goal_id):
    # handles data validation and error responses as needed
    goal = validate_model(Goal, goal_id)

    # deletes the goal and saves that change to db.
    db.session.delete(goal)
    db.session.commit()

    # creates response_body stating goal was successfully deleted
    response_body = f'{{"details": "Goal {goal_id} \\"{goal.title}\\" successfully deleted"}}'

    return Response(
        response_body,
        status=200,
        mimetype="application/json"
    )
