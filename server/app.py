#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

# ---------- Signup ----------
class Signup(Resource):
    def post(self):
        json = request.get_json()
        try:
            if not json.get("username") or not json.get("password"):
                raise ValueError("Username and password are required.")

            user = User(
                username=json["username"],
                image_url=json.get("image_url"),
                bio=json.get("bio")
            )
            user.password_hash = json["password"]
            db.session.add(user)
            db.session.commit()

            session["user_id"] = user.id
            return user.to_dict(), 201

        except (IntegrityError, ValueError) as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 422

# ---------- Check Session ----------
class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        if user_id:
            user = User.query.get(user_id)
            if user:
                return user.to_dict(), 200
        return {"error": "Unauthorized"}, 401

# ---------- Login ----------
class Login(Resource): 
    def post(self):
        json = request.get_json()
        user = User.query.filter_by(username=json.get("username")).first()

        if user and user.authenticate(json.get("password")):
            session["user_id"] = user.id
            return user.to_dict(), 200
        return {"error": "Invalid credentials"}, 401

# ---------- Logout ----------
class Logout(Resource):
    def delete(self):
        if session.get("user_id"):
            session.pop("user_id")
            return {}, 204
        return {"error": "Unauthorized"}, 401

# ---------- Recipes (GET & POST) ----------
class RecipeIndex(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        recipes = Recipe.query.all()
        return [recipe.to_dict() for recipe in recipes], 200

    def post(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        json = request.get_json()

        try:
            title = json.get("title")
            instructions = json.get("instructions")
            minutes_raw = json.get("minutes_to_complete")

            if not title or not instructions or minutes_raw is None:
                raise ValueError("All fields are required.")

            minutes = int(minutes_raw)

            recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes,
                user_id=user_id
            )
            db.session.add(recipe)
            db.session.commit()

            return recipe.to_dict(), 201

        except (ValueError, TypeError) as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 422

# ---------- Register Resources ----------
api.add_resource(Signup, "/signup", endpoint="signup")
api.add_resource(CheckSession, "/check_session", endpoint="check_session")
api.add_resource(Login, "/login", endpoint="login")
api.add_resource(Logout, "/logout", endpoint="logout")
api.add_resource(RecipeIndex, "/recipes", endpoint="recipes")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
