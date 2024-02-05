#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class IndexArticle(Resource):
    
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            article_json = jsonify(article.to_dict())

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401
    
class Login(Resource):
    
    def post(self):
        #Whatever the user inputs will be through a request... Big FYI
        #This is pretty much filtering the Users in the User class to get the username that the client inputted in their request
        user = User.query.filter(User.username == request.get_json()["username"]).first()

        #adds the user's id in the session as user_id
        #the user information will be stored in the session (browser)
        session['user_id'] = user.id

        #returns the actual user to the response.
        #This step is separate from adding things to the session.
        response = make_response(user.to_dict(), 200)

        return response
    
class Logout(Resource):

    def delete(self):
        #sets the session's user_id
        session['user_id'] = None
        return make_response({'message': '204: No Content'}, 204)
    
class CheckSession(Resource):

    def get(self):
        user = User.query.filter(User.id == session.get("user_id")).first()
        if user:
            return make_response(jsonify(user.to_dict()), 200)
        else:
            return make_response({}, 401)





api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
