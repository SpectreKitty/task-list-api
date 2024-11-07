from flask import abort, make_response
from ..db import db

# will make sure that models(goal or task) will be an integer 
# when it needs to be and respond appropriately if its not, 
# or if its empty will also send appropriate message.

def validate_model(cls, model_id):
    try:
        model_id = int(model_id)
    except:
        response = {"message": f"invalid {cls.__name__} id"}
        abort(make_response(response, 400))

    query = db.select(cls).where(cls.id == model_id)
    model = db.session.scalar(query)

    if not model:
        response = {"message": f"{cls.__name__} not found"}
        abort(make_response(response, 404))
        
    return model
