# coding:utf8
import os

from werkzeug.utils import secure_filename

from app.admin.intercept.intercept import user_login_req
from app.admin.intercept.utils import change_filename
from . import home
from flask import render_template, redirect, url_for, flash, session, request
from app.home.forms import RegistForm, LoginForm, UserdeatailForm, PwdForm, CommentForm
from app.models import User, Userlog, Comment, Preview, Tag, Movie, Moviecol
from app import db, app
import uuid


# 首页
# 首页
@home.route("/", methods=["GET"])
def index():
    tags = Tag.query.all()
    tid = request.args.get("tid", 0)

    page_data = Movie.query

    # 标签
    if tid != '' and int(tid) != 0:
        page_data = page_data.filter_by(tag_id=int(tid))

    # 星际
    star = request.args.get("star", 0)
    if star != '' and int(star) != 0:
        page_data = page_data.filter_by(star=int(star))

    # 时间
    time = request.args.get("time", 0)
    if time != '' and int(time) != 0:
        if int(time) == 1:
            page_data = page_data.order_by(Movie.addtime.desc())
        else:
            page_data = page_data.order_by(Movie.addtime.asc())

    # 播放量
    pm = request.args.get("pm", 0)
    if pm != '' and int(pm) != 0:
        if int(pm) == 1:
            page_data = page_data.order_by(Movie.playnum.desc())
        else:
            page_data = page_data.order_by(Movie.playnum.asc())

    # 评论量
    cm = request.args.get("cm", 0)
    if cm != '' and int(cm) != 0:
        if int(cm) == 1:
            page_data = page_data.order_by(Movie.commentnum.desc())
        else:
            page_data = page_data.order_by(Movie.commentnum.asc())

    page = request.args.get("page", 1)
    page_data = page_data.paginate(page=int(page), per_page=10)

    p = dict(
        tid=tid,
        star=star,
        time=time,
        pm=pm,
        cm=cm
    )
    return render_template("home/index.html", tags=tags, p=p, page_data=page_data)


@home.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(name=data['name']).first()
        if not user.check_pwd(data["pwd"]):
            flash("密码错误!", "err")

            return redirect(url_for('home.login'))

        session["user"] = user.name
        session["user_id"] = user.id

        # log
        userlog = Userlog(
            user_id=user.id,
            ip=request.remote_addr
        )
        db.session.add(userlog)
        db.session.commit()

        return redirect(request.args.get("next") or url_for('home.user'))

    return render_template("home/login.html", form=form)


@home.route("/logout/")
def logout():
    session.pop("user", None)
    session.pop("user_id", None)

    flash("退出成功!", "ok")
    return redirect(url_for("home.login"))


@home.route("/regist/", methods=['GET', 'POST'])
def regist():
    form = RegistForm()

    if form.validate_on_submit():
        data = form.data

        from werkzeug.security import generate_password_hash

        user = User(
            name=data['name'],
            pwd=generate_password_hash(data['pwd']),
            phone=data['phone'],
            email=data['email'],
            uuid=uuid.uuid4().hex
        )
        db.session.add(user)
        db.session.commit()

        flash("注册成功!", "ok")
        return redirect(url_for('home.login'))

    return render_template("home/regist.html", form=form)


@home.route("/user/", methods=["POST", "GET"])
@user_login_req
def user():
    form = UserdeatailForm()
    user = User.query.get_or_404(int(session["user_id"]))
    form.face.validators = []

    if request.method == "GET":
        pass
        form.name.data = user.name
        form.email.data = user.email
        form.phone.data = user.phone
        form.face.data = user.face
        form.info.data = user.info

    if form.validate_on_submit():
        data = form.data

        name_count = User.query.filter_by(name=data['name']).count()
        if data['name'] != user.name and name_count >= 1:
            flash("昵称已经存在!", "err")

            return redirect(url_for('home.user'))

        email_count = User.query.filter_by(email=data['email']).count()
        if data['email'] != user.email and email_count >= 1:
            flash("昵称已经存在!", "err")

            return redirect(url_for('home.user'))

        name_phone = User.query.filter_by(phone=data['phone']).count()
        if data['phone'] != user.phone and name_phone >= 1:
            flash("昵称已经存在!", "err")

            return redirect(url_for('home.user'))

        if form.face.data.filename != "":
            file_face = secure_filename(form.face.data.filename)

            if not os.path.exists(app.config["FC_DIR"]):
                os.makedirs(app.config["FC_DIR"])

            user.face = change_filename(file_face)
            form.face.data.save(app.config["FC_DIR"] + user.face)

        user.name = data['name']
        user.email = data['email']
        user.phone = data['phone']
        user.info = data['info']
        db.session.add(user)
        db.session.commit()

        flash("修改用户信息成功!", "ok")

        return redirect(url_for('home.user'))
    return render_template("home/user.html", form=form)


@home.route("/pwd/", methods=['POST', 'GET'])
@user_login_req
def pwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        user_id = session["user_id"]
        user = User.query.get_or_404(int(user_id))
        if user.check_pwd(data["new_pwd"]):
            flash("新密码不能与老密码不一致!", "err")
            return redirect(url_for("home.pwd"))

        from werkzeug.security import generate_password_hash
        user.pwd = generate_password_hash(data["new_pwd"])

        db.session.add(user)
        db.session.commit()
        flash("修改密码成功!", "ok")

        return redirect(url_for("home.logout"))

    return render_template("home/pwd.html", form=form)


@home.route("/comments/<int:page>/")
@user_login_req
def comments(page=None):
    if page is None:
        page = 10
    page_data = Comment.join(Movie).join(User).query.filter(
        Movie.id == Comment.movie_id,
        User.id == session["user_id"]
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=10)

    return render_template("home/comments.html", page_data=page_data)


@home.route("/loginlog/<int:page>/")
@user_login_req
def loginlog(page=None):
    if page is None:
        page = 10
    page_data = Userlog.query.order_by(
        Userlog.addtime.desc()
    ).paginate(page=page, per_page=10)

    return render_template("home/loginlog.html", page_data=page_data)


@home.route("/moviecol/<int:page>/")
@user_login_req
def moviecol(page=None):
    if page is None:
        page = 1

    page_data = Moviecol.query.join(
        Movie
    ).join(
        User
    ).filter(
        User.id == Moviecol.user_id,
        Movie.id == Moviecol.movie_id,
        Moviecol.user_id == int(session['user_id'])
    ).order_by(
        Moviecol.addtime.desc()
    ).paginate(page=page, per_page=10)

    return render_template("home/moviecol.html", page_data=page_data)


# 预览图
@home.route("/animation/")
def animation():
    data = Preview.query.all()
    return render_template("home/animation.html", data=data)


@home.route("/search/")
def search():
    key = request.args.get('key', '')
    page = request.args.get('page', 1)

    page_data = Movie.query
    if key != '':
        page_data = page_data.filter(
            Movie.title.ilike('%' + key + '%')
        )

    page_data = page_data.order_by(Movie.addtime.desc()).paginate(page=int(page), per_page=10)

    return render_template("/home/search.html ", page_data=page_data, key=key)


@home.route("/play/", methods=["GET", "POST"])
def play():
    id = int(request.args.get("id", 0))

    movie = Movie.query.join(Tag).filter(
        Tag.id == Movie.tag_id,
        Movie.id == int(id)
    ).first_or_404()
    # 电影操作
    movie.playnum = movie.playnum + 1
    db.session.add(movie)
    db.session.commit()

    form = CommentForm()

    # if "user" not in session:
    #     flash("请先登录!")
    #     return redirect(url_for("home.login"))

    if ("user" in session) and form.validate_on_submit():
        data = form.data
        comment = Comment(
            content=data['content'],
            movie_id=id,
            user_id=session["user_id"]
        )
        db.session.add(comment)
        db.session.commit()

        # 电影增加
        movie.commentnum = movie.commentnum + 1
        db.session.add(movie)
        db.session.commit()

        flash("添加评论成功!", "ok")

        return redirect(url_for("home.play", id=id))

    page = int(request.args.get("page", 1))
    if page is None:
        page = 1
    page_data = Comment.query.filter(
        Comment.movie_id == Movie.id
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=10)

    return render_template("/home/play.html", movie=movie, form=form, page_data=page_data)


# 电影收藏
@home.route("/moviecol/add/", methods=["POST"])
@user_login_req
def moviecol_add():
    import json
    uid = request.values.get("uid", "")
    mid = request.values.get("mid", "")
    moviecol = Moviecol.query.filter_by(
        user_id=int(uid),
        movie_id=int(mid)
    ).count()
    data = dict(ok=0)
    if moviecol >= 1:
        data = dict(code=1, msg="收藏失败,已经收藏!")
    else:
        moviecol = Moviecol(
            user_id=int(uid),
            movie_id=int(mid)
        )
        db.session.add(moviecol)
        db.session.commit()

        data = dict(code=1, msg="收藏成功!")

    return json.dumps(data)


#弹幕
