from flask_restful import Resource, fields, marshal_with, reqparse
from application.data.database import db
from application.data.models import *
from application.utils.validation import *

output_fields = {
    "user_id": fields.Integer,
    "username": fields.String,
    "email": fields.String,
    "role": fields.String
}

class UserAPI(Resource):
    @marshal_with(output_fields)
    def get(self, user_id=None):
        if(user_id is None):
            users = User.query.all()
            for user in users:
                user.role = user.roles[0].name
            if users:
                return users
            else:
                raise NotFoundError(status_code=404)
        user = User.query.get(user_id)
        user.role = user.roles[0].name
        if user:
            return user
        else:
            raise NotFoundError(status_code=404)
