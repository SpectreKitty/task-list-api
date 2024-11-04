from flask import Blueprint, abort, make_response, request, Response
from datetime import datetime, timezone
from app.models.goal import Goal
from ..db import db
import requests
import os

goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

@goals_bp.post("")
def create_goal():
    request_body = request.get_json()

    # how can I do this in validate function?
    if not request_body.get("title"):
        return {"details": "Invalid data"}, 400
    
    title = request_body["title"]
    
    new_goal = Goal(title=title)

    db.session.add(new_goal)
    db.session.commit()

    response = {
        "goal":{
        "id": new_goal.id,
        "title": new_goal.title,
    }}
    
    return response, 201

@goals_bp.get("")
def get_all_goals():
    query = db.select(Goal)

    # title_param = request.args.get("title")
    # sort_param = request.args.get("sort")

    # if sort_param == "asc":
    #     query = query.order_by(Goal.title)

    # if sort_param == "desc":
    #     query = query.order_by(Goal.title.desc())

    # if title_param:
    #     query = query.where(Goal.title.ilike(f"%{title_param}%"))

    query = query.order_by(Goal.id)

    goals = db.session.scalars(query)

    goals_response = []
    for goal in goals:
        goals_response.append({
            "id": goal.id,
            "title": goal.title,
        })

    return goals_response

@goals_bp.get("/<goal_id>")
def get_one_goal(goal_id):
    goal = validate_goal(goal_id)

    return {
        "goal":{
        "id": goal.id,
        "title": goal.title,
        }}

@goals_bp.put("/<goal_id>")
def update_goal(goal_id):
    goal = validate_goal(goal_id)
    request_body = request.get_json()

    goal.title = request_body["title"]

    db.session.commit()
    
    response_body = {
        "goal": {
            "id": goal.id,
            "title": goal.title,
        }
    }
    return response_body, 200

@goals_bp.delete("/<goal_id>")
def delete_goal(goal_id):
    goal = validate_goal(goal_id)

    db.session.delete(goal)
    db.session.commit()

    response_body = f'{{"details": "Goal {goal_id} \\"{goal.title}\\" successfully deleted"}}'

    return Response(
        response_body,
        status=200,
        mimetype="application/json"
    )

def validate_goal(goal_id):
    try:
        goal_id = int(goal_id)
    except:
        response = {"message": f"invalid goal id"}
        abort(make_response(response, 400))

    query = db.select(Goal).where(Goal.id == goal_id)
    goal = db.session.scalar(query)

    if not goal:
        response = {"message": f"goal not found"}
        abort(make_response(response, 404))
        
    return goal