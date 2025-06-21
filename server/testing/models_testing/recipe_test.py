import pytest
from sqlalchemy.exc import IntegrityError

from app import app
from models import db, Recipe, User

class TestRecipe:
    '''Recipe in models.py'''

    def test_has_attributes(self):
        '''has attributes title, instructions, and minutes_to_complete.'''
        
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(username="tester")
            user.password_hash = "password123"
            db.session.add(user)
            db.session.commit()

            recipe = Recipe(
                title="Delicious Shed Ham",
                instructions="Or kind rest bred with am shed then. In" * 10,
                minutes_to_complete=60,
                user_id=user.id
            )
            db.session.add(recipe)
            db.session.commit()

            new_recipe = Recipe.query.filter_by(title="Delicious Shed Ham").first()
            assert new_recipe.title == "Delicious Shed Ham"
            assert new_recipe.minutes_to_complete == 60

    def test_requires_title(self):
        '''requires each record to have a title.'''

        with app.app_context():
            Recipe.query.delete()
            db.session.commit()

            recipe = Recipe()
            with pytest.raises(IntegrityError):
                db.session.add(recipe)
                db.session.commit()

    def test_requires_50_plus_char_instructions(self):
        '''requires instructions to be 50+ characters.'''
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(username="tester2")
            user.password_hash = "securepass"
            db.session.add(user)
            db.session.commit()

            with pytest.raises((IntegrityError, ValueError)):
                recipe = Recipe(
                    title="Generic Ham",
                    instructions="idk lol",
                    user_id=user.id
                )
                db.session.add(recipe)
                db.session.commit()

    def test_user_has_list_of_recipes(self):
        '''User has a list of associated recipes.'''
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(username="chefmaster")
            user.password_hash = "fancypass"
            db.session.add(user)
            db.session.commit()

            recipe = Recipe(
                title="Chef's Secret",
                instructions="Boil with passion and stir with purpose until flavor blossoms like sunrise." * 2,
                minutes_to_complete=75,
                user_id=user.id
            )
            db.session.add(recipe)
            db.session.commit()

            assert len(user.recipes) == 1
            assert user.recipes[0].title == "Chef's Secret"
