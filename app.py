from flask import Flask
from flask_restx import Api, Resource, fields, reqparse
from dataclasses import dataclass

app = Flask(__name__)

@dataclass
class Post:
    id: int
    title: str
    description: str

post_array = []
next_id = 1

@app.route("/")
def root_home():
    return "Welcome to the Simple Blog API!"

api = Api(
    app,
    version="1.0",
    title="Simple Blog API",
    description="An API to control a micro blog",
    doc="/swagger",
)

ns = api.namespace("posts", description="Blog posts")

post_parser = reqparse.RequestParser()
post_parser.add_argument("title", type=str, required=True, help="Post title")
post_parser.add_argument("description", type=str, required=True, help="Post content")

model = api.model("BlogModel", {
    "id": fields.Integer(readOnly=True, description="Post identifier"),
    "title": fields.String(required=True, description="Post title"),
    "description": fields.String(required=True, description="Post content"),
})

@ns.route("/")
class BlogResource(Resource):
    @ns.doc("get_posts")
    @ns.marshal_list_with(model)
    def get(self):
        return post_array

    @ns.doc("add_post")
    @ns.expect(post_parser)
    @ns.marshal_with(model, code=201)
    def post(self):
        global next_id
        args = post_parser.parse_args()
        post = Post(id=next_id, title=args["title"], description=args["description"])
        post_array.append(post)
        next_id += 1
        return post, 201

@ns.route("/<int:id>")
@ns.response(404, "Post not found")
@ns.param("id", "The post identifier")
class PostResource(Resource):
    @ns.doc("get_post")
    @ns.marshal_with(model)
    def get(self, id):
        post = next((post for post in post_array if post.id == id), None)
        if post is None:
            api.abort(404, "Post not found")
        return post

    @ns.doc("update_post")
    @ns.expect(post_parser)
    @ns.marshal_with(model)
    def put(self, id):
        post = next((post for post in post_array if post.id == id), None)
        if post is None:
            api.abort(404, "Post not found")
        args = post_parser.parse_args()
        post.title = args["title"]
        post.description = args["description"]
        return post

    @ns.doc("delete_post")
    @ns.marshal_with(model)
    def delete(self, id):
        global post_array
        post = next((post for post in post_array if post.id == id), None)
        if post is None:
            api.abort(404, "Post not found")
        post_array = [post for post in post_array if post.id != id]
        return "", 204

if __name__ == "__main__":
    app.run(debug=True)
