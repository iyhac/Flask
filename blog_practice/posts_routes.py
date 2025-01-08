from flask import request, jsonify, render_template
from flask_smorest import Blueprint, abort

#mysql을 받아야하기 때문에 함수로 만드는 것임.
def create_posts_blueprint(mysql):
    posts_blp = Blueprint( 'posts', __name__, description="posts api", url_prefix="/posts",)

# bp = Blueprint('main',__name__, url_prefix="/")
# 객체명 = Blueprint('별칭'__name__,url_prefix="/라우팅 함수의 애네테이션??URL 앞에 기본으로 붙힐 접두어 URL")
# 디스크립터(Descriptor) = 클래스를 통해 속성 접근을 제어하기 위한 프로토콜으로, 클래스 내에 get, set, delete 메소드를 구현함.
    
    
    #@@@라우팅(routing)기법 / 객체이름.route(/route경로이름/원하는 값)

    #posts_blp 경로에 "/"뒤에 methods 중 하나를 넣으면 아래 코드가 실행된다. 
    @posts_blp.route("/",methods = ["GET","POST"])
    def posts():
        cursor=mysql.connection.cursor()
        # GET 게시글 조회
        if request.method =="GET":

            sql = "SELECT * FROM posts"
            cursor.execute(sql)

            posts = cursor.fetchall()
            cursor.close()

            post_list=[]

            for post in posts:
                post_list.append({
                    'id': post[0],
                    'title' : post[1],
                    'content' : post[2]
                })

            return post_list
        
        #POST 게시글 생성
        elif request.method == "POST":
            title = request.json.get('title')
            content = request.json.get('content')

            if not title or not content:
                abort(400, message="Title or Content cannot be empty")

            sql = "INSERT INTO posts(title, content) VALUES(%s,%s)"
            cursor.execute(sql, (title,content))
            mysql.connection.commit()

            return jsonify({'msg':'successfully created post data','title':title,'content':content},201)
        


    @posts_blp.route('/<int:id>', methods=['GET','PUT','DELETE'])
    def post(id):
        cursor = mysql.connection.cursor()
        if request.method == "GET":
            sql = f"SELECT * FROM posts WHERE id={id}"
            cursor.execute(sql)
            post = cursor.fetchone()

            if not post:
                abort(404, message="해당 게시글이 없습니다.")
            return {
                "id": post[0],
                "title": post[1],
                "content": post[2],
            }
        #특정 id PUT 수정
        elif request.method == "PUT":
            title = request.json.get("title")
            content = request.json.get("content")

            if not title or not content:
                abort(400, message="title 또는 content가 없습니다.")

            sql = "SELECT * FROM posts WHERE id=%s"
            cursor.execute(sql, (id,))
            post = cursor.fetchone()

            if not post:
                abort(404, message="해당 게시글이 없습니다.")

            sql = "UPDATE posts SET title=%s, content=%s WHERE id=%s"
            cursor.execute(sql, (title, content, id))
            mysql.connection.commit()

            return jsonify({"message": "Successfully updated title & content"})

        elif request.method == "DELETE":
            sql = "SELECT * FROM posts WHERE id=%s"
            cursor.execute(sql, (id,))
            post = cursor.fetchone()

            if not post:
                abort(404, message="해당 게시글이 없습니다.")

            sql = "DELETE FROM posts WHERE id=%s"
            cursor.execute(sql, (id,))
            mysql.connection.commit()

            return jsonify({"message": "Successfully deleted post"})

    return posts_blp