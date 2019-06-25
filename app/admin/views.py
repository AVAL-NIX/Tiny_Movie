# coding:utf8

from . import admin
from flask import render_template, redirect, url_for, flash, session, request, abort
from app.admin.forms import LoginForm, TagForm, MovieForm, PreviewForm, PwdForm, AuthForm, RoleForm, AdminForm
from app.models import Admin, Tag, Movie, Preview, User, Comment, Moviecol, Oplog, Adminlog, Userlog, Auth, Role
from functools import wraps
from app import db, app
from werkzeug.utils import secure_filename
import os
from app.admin.intercept.utils import change_filename
import datetime
from app.admin.intercept.intercept import admin_auth, admin_login_req


# 上下应用处理器
@admin.context_processor
def tpl_extra():
    data = dict(
        online_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    return data



# 首页
@admin.route("/", methods=['GET', 'POST'])
@admin_login_req
def index():
    return render_template("admin/index.html")


# 登录
@admin.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=data["account"]).first()
        if not admin.check_pwd(data["pwd"]):
            flash("密码错误!", "err")
            return redirect(url_for("admin.login"))
        session["admin"] = data["account"]
        session["admin_id"] = admin.id

        # log
        adminlog = Adminlog(
            admin_id=admin.id,
            ip=request.remote_addr,
        )
        db.session.add(adminlog)
        db.session.commit()
        print(request.args.get("next"))
        return redirect(request.args.get("next") or url_for("admin.index"))
    return render_template("admin/login.html", form=form)


# 退出
@admin.route("/logout/")
def logout():
    session.pop("admin", None)
    session.pop("admin_id", None)
    return redirect(url_for("admin.login"))


# 修改管理员密码
@admin.route("/pwd/", methods=["GET", "POST"])
@admin_login_req
def pwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        adminId = session["admin_id"]
        admin = Admin.query.get_or_404(int(adminId))
        if admin.check_pwd(data["new_pwd"]):
            flash("新密码不能与老密码不一致!", "err")
            return redirect(url_for("admin.pwd"))

        from werkzeug.security import generate_password_hash
        admin.pwd = generate_password_hash(data["new_pwd"])

        db.session.add(admin)
        db.session.commit()
        flash("修改密码成功!", "ok")

        return redirect(url_for("admin.logout"))

    return render_template("admin/pwd.html", form=form)


#  标签添加
@admin.route("/tag/add/", methods=["POST", "GET"])
@admin_login_req
def tag_add():
    form = TagForm()
    if form.validate_on_submit():
        data = form.data
        tag_count = Tag.query.filter_by(name=data["name"]).count()
        if tag_count >= 1:
            flash("名称已经存在!", "err")
            return redirect(url_for("admin.tag_add"))
        tag = Tag(
            name=data["name"]
        )
        db.session.add(tag)
        db.session.commit()
        flash("添加成功", "ok")

        # 操作日记
        oplog = Oplog(
            admin_id=session['admin_id'],
            ip=request.remote_addr,
            reason="添加标签%s" % data['name']
        )
        db.session.add(oplog)
        db.session.commit()

        return redirect(url_for("admin.tag_add"))
    return render_template("admin/tag_add.html", form=form)


# 标签编辑
@admin.route("/tag/edit/<int:id>/", methods=["POST", "GET"])
@admin_login_req
def tag_edit(id):
    form = TagForm()
    tag = Tag.query.get_or_404(id)
    if form.validate_on_submit():
        data = form.data
        tag_count = Tag.query.filter_by(name=data["name"]).count()
        if tag.name != data["name"] and tag_count >= 1:
            flash("名称已经存在!", "err")
            return redirect(url_for("admin.tag_edit"))
        tag.name = data["name"]
        db.session.add(tag)
        db.session.commit()
        flash("修改标签成功", "ok")
        return redirect(url_for("admin.tag_edit", id=id))
    return render_template("admin/tag_edit.html", form=form, tag=tag)


# 标签删除
@admin.route('/tag/del/<int:id>/', methods=["GET"])
@admin_login_req
def tag_del(id=None):
    tag = Tag.query.filter_by(id=id).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    flash("删除标签成功", "ok")
    return redirect(url_for('admin.tag_list', page=1))


# 标签列表
@admin.route("/tag/list/<int:page>/", methods=["GET"])
@admin_login_req
def tag_list(page=None, name=None):
    if page is None:
        page = 1
    page_data = Tag.query.filter_by().order_by(
        Tag.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/tag_list.html", page_data=page_data)


# 电影添加
@admin.route("/movie/add/", methods=["GET", "POST"])
@admin_login_req
def movie_add():
    form = MovieForm()
    if form.validate_on_submit():
        data = form.data
        file_url = secure_filename(form.url.data.filename)
        file_logo = secure_filename(form.logo.data.filename)
        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            # os.chmod(app.config["UP_DIR"], "rw")
        url = change_filename(file_url)
        logo = change_filename(file_logo)
        form.url.data.save(app.config["UP_DIR"] + url)
        form.logo.data.save(app.config["UP_DIR"] + logo)
        movie = Movie(
            title=data['title'],
            url=url,
            info=data["info"],
            logo=logo,
            star=int(data["star"]),
            playnum=0,
            commentnum=0,
            tag_id=int(data["tag_id"]),
            area=data["area"],
            release_time=data["release_time"],
            length=data["length"],
        )
        db.session.add(movie)
        db.session.commit()
        flash("添加电影成功", "ok")
        return redirect(url_for('admin.movie_add'))
    return render_template("admin/movie_add.html", form=form)


# 电影编辑
@admin.route("movie/edit/<int:id>/", methods=["GET", "POST"])
@admin_login_req
def movie_edit(id=None):
    form = MovieForm()
    movie = Movie.query.get_or_404(int(id))
    form.url.validators = []
    form.logo.validators = []
    if request.method == "GET":
        form.info.data = movie.info
        form.tag_id.data = movie.tag_id
        form.star.data = movie.star
    if form.validate_on_submit():
        data = form.data

        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            #  os.chmod(app.config["UP_DIR"], "rw")

        if form.url.data.filename != "":
            file_url = secure_filename(form.url.data.filename)
            movie.url = change_filename(file_url)
            form.url.data.save(app.config["UP_DIR"] + movie.url)

        if form.logo.data.filename != "":
            file_logo = secure_filename(form.logo.data.filename)
            movie.logo = change_filename(file_logo)
            form.logo.data.save(app.config["UP_DIR"] + movie.logo)

        movie_count = Movie.query.filter_by(title=data["title"]).count()
        if movie_count == 1 and movie.title != data["title"]:
            flash("片名已经存在!", "err")
            return redirect(url_for('admin.movie_edit', id=movie.id))

        movie.star = data["star"]
        movie.tag_id = data["tag_id"]
        movie.info = data["info"]
        movie.title = data["title"]
        movie.area = data["area"]
        movie.length = data["length"]
        movie.release_time = data["release_time"]
        db.session.add(movie)
        db.session.commit()
        flash("修改电影成功", "ok")
        return redirect(url_for('admin.movie_edit', id=movie.id))
    return render_template("admin/movie_edit.html", form=form, movie=movie)


# 电影列表
@admin.route("/movie/list/<int:page>", methods=["GET"])
@admin_login_req
def movie_list(page=None):
    if page is None:
        page = 1

    page_data = Movie.query.join(Tag).filter(
        Tag.id == Movie.tag_id
    ).order_by(
        Movie.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/movie_list.html", page_data=page_data)


# 删除电影
@admin.route('/movie/del/<int:id>/', methods=["GET"])
@admin_login_req
def movie_del(id=None):
    movie = Movie.query.get_or_404(int(id))
    db.session.delete(movie)
    db.session.commit()
    flash("删除电影成功!", "ok")
    return redirect(url_for('admin.movie_list', page=1))


# 预告添加
@admin.route("/preview/add/", methods=["GET", "POST"])
@admin_login_req
def preview_add():
    form = PreviewForm()
    if form.validate_on_submit():
        data = form.data

        preview_count = Preview.query.filter_by(title=data['title']).count()
        if preview_count > 0:
            flash("预告编辑标题存在!", "err")
            return redirect(url_for('admin.preview_add'))

        file_logo = secure_filename(form.logo.data.filename)

        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])

        logo = change_filename(file_logo)
        form.logo.data.save(app.config["UP_DIR"] + logo)

        preview = Preview(
            title=data['title'],
            logo=logo

        )
        db.session.add(preview)
        db.session.commit()
        flash("预告添加成功!", "ok")
        return redirect(url_for('admin.preview_add'))
    return render_template("admin/preview_add.html", form=form)


# 预告编辑
@admin.route("/preview/edit/<int:id>/", methods=['GET', "POST"])
@admin_login_req
def preview_edit(id=None):
    form = PreviewForm()
    form.logo.validators = []

    preview = Preview.query.get_or_404(int(id))

    if request.method == "GET":
        form.title.data = preview.title

    if form.validate_on_submit():
        data = form.data

        preview_count = Preview.query.filter_by(title=data['title']).count()
        if preview_count >= 1 and preview.title != data['title']:
            flash("预告编辑标题存在!", "err")
            return redirect(url_for('admin.preview_edit', id=preview.id))

        if form.logo.data.filename != "":
            file_logo = secure_filename(form.logo.data.filename)
            preview.logo = change_filename(file_logo)
            form.logo.data.save(app.config["UP_DIR"] + preview.logo)

        db.session.add(preview)
        db.session.commit()
        flash("预告编辑成功!", "ok")
        return redirect(url_for('admin.preview_edit', id=preview.id))
    return render_template("admin/preview_edit.html", form=form, preview=preview)


# 预告删除
@admin.route("/preview/del/<int:id>/")
@admin_login_req
def preview_del(id=None):
    preview = Preview.query.get_or_404(int(id))
    db.session.delete(preview)
    db.session.commit()
    flash("删除成功!", "ok")
    return redirect(url_for("admin.preview_list", page=1))


# 预告列表
@admin.route("/preview/list/<int:page>/", methods=["POST", "GET"])
@admin_login_req
def preview_list(page=None):
    if page is None:
        page = 1

    page_data = Preview.query.filter_by().order_by(
        Preview.addtime.desc()
    ).paginate(page=page, per_page=10)

    return render_template("admin/preview_list.html", page_data=page_data)


@admin.route('/user/list/<int:page>/', methods=["POST", "GET"])
@admin_login_req
def user_list(page=None):
    if page is None:
        page = 1

    page_data = User.query.filter_by().order_by(
        User.addtime.desc()
    ).paginate(page=page, per_page=10)

    return render_template('admin/user_list.html', page_data=page_data)


# 用户视图
@admin.route('/user/view/<int:id>/')
@admin_login_req
def user_view(id=None):
    user = User.query.get_or_404(int(id))
    return render_template('admin/user_view.html', user=user)


# 用户删除
@admin.route('/user/del/<int:id>/')
@admin_login_req
def user_del(id=None):
    user = User.query.get_or_404(int(id))
    db.session.delete(user)
    db.session.commit()
    flash("用户删除成功!", "ok")
    return redirect(url_for('admin.user_list', page=1))


# 评论列表
@admin.route("/comment/list/<int:page>/")
@admin_login_req
def comment_list(page=None):
    if page is None:
        page = 1

    page_data = Comment.query.join(
        User
    ).join(
        Movie
    ).filter(
        Movie.id == Comment.movie_id,
        User.id == Comment.user_id
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/comment_list.html", page_data=page_data)


# 评论删除
@admin.route("comment/del/<int:id>/")
@admin_login_req
def comment_del(id=None):
    comment = Comment.query.get_or_404(int(id))
    db.session.delete(comment)
    db.session.commit()
    flash("删除成功!", "ok")
    redirect(url_for('admin.comment_list', page=1))


@admin.route("/moviecol/list/<int:page>/", methods=["GET"])
@admin_login_req
def moviecol_list(page=None):
    if page is None:
        page = 1

    page_data = Moviecol.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Moviecol.movie_id,
        User.id == Moviecol.user_id
    ).order_by(
        Moviecol.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/moviecol_list.html", page_data=page_data)


@admin.route("/moviecol/del/<id>/")
@admin_login_req
def moviecol_del(id=None):
    moviecol = Moviecol.query.get_or_404(int(id))
    db.session.delete(moviecol)
    db.session.commit()
    flash("删除收藏成功!", "ok")
    return redirect(url_for("admin/moviecol_list.html", page=1))


# 操作日记
@admin.route("/oplog/list/<page>/", methods=["GET"])
@admin_login_req
def oplog_list(page=None):
    page = int(page)
    if page is None:
        page = 1
    page_data = Oplog.query.join(
        Admin
    ).filter(
        Admin.id == Oplog.admin_id
    ).order_by(
        Oplog.addtime.desc()
    ).paginate(page=page, per_page=10)

    return render_template("admin/oplog_list.html", page_data=page_data)


# 管理员操作日记
@admin.route("/adminloginlog/list/<page>/", methods=["GET"])
@admin_login_req
def adminloginlog_list(page):
    page = int(page)

    if page is None:
        page = 1
    page_data = Adminlog.query.join(
        Admin
    ).filter(
        Admin.id == Adminlog.admin_id
    ).order_by(
        Adminlog.addtime.desc()
    ).paginate(page=page, per_page=10)

    return render_template("admin/adminloginlog_list.html", page_data=page_data)


#  用户日记
@admin.route("/userloginlog/list/<int:page>/", methods=["GET"])
@admin_login_req
def userloginlog_list(page=None):
    if page is None:
        page = 1

    page_data = Userlog.query.join(
        User
    ).filter(
        User.id == Userlog.user_id
    ).order_by(
        Userlog.addtime.desc()
    ).paginate(page=page, per_page=10)

    return render_template("admin/userloginlog_list.html", page_data=page_data)


# 权限添加
@admin.route("/auth/add/", methods=["GET", "POST"])
@admin_login_req
def auth_add():
    form = AuthForm()
    if form.validate_on_submit():
        data = form.data
        auth = Auth(
            name=data["name"],
            url=data["url"]
        )
        db.session.add(auth)
        db.session.commit()
        flash("添加权限成功!", "ok")
        redirect(url_for('admin.auth_add'))
    return render_template("admin/auth_add.html", form=form)


# 权限编辑
@admin.route("/auth/edit/<int:id>/", methods=["GET", "POST"])
@admin_login_req
def auth_edit(id=None):
    form = AuthForm()
    auth = Auth.query.get_or_404(int(id))

    if request.method == "GET":
        form.name.data = auth.name
        form.url.data = auth.url

    if form.validate_on_submit():
        data = form.data

        auth.name = data["name"]
        auth.url = data["url"]

        db.session.add(auth)
        db.session.commit()
        flash("编辑权限成功!", "ok")
        redirect(url_for('admin.auth_edit', id=id))
    return render_template("admin/auth_edit.html", form=form, auth=auth)


# 权限删除
@admin.route("/auth/edit/<int:id>/", methods=["GET", "POST"])
@admin_login_req
def auth_del(id=None):
    auth = Auth.query.get_or_404(int(id))
    db.session.delete(auth)
    db.session.commit()
    flash("权限删除成功!", "ok")

    redirect(url_for('admin.auth_list', page=1))


# 权限列表
@admin.route("/auth/list/<int:page>/", methods=["GET"])
@admin_login_req
def auth_list(page=None):
    if page is None:
        page = 1
    page_data = Auth.query.filter().order_by(
        Auth.addtime.desc()
    ).paginate(page=page, per_page=10)

    return render_template("admin/auth_list.html", page_data=page_data)


# 角色添加
@admin.route("/role/add/", methods=["GET", "POST"])
@admin_login_req
def role_add():
    form = RoleForm()
    if form.validate_on_submit():
        data = form.data
        role = Role(
            name=data["name"],
            auths=",".join(map(lambda v: str(v), data['auths']))
        )
        db.session.add(role)
        db.session.commit()
        flash("添加角色成功!", "ok")

        return redirect(url_for("admin.role_add"))
    return render_template("admin/role_add.html", form=form)


# 角色编辑
@admin.route("/role/edit/<int:id>/", methods=["GET", "POST"])
@admin_login_req
def role_edit(id=None):
    form = RoleForm()
    role = Role.query.get_or_404(int(id))

    if request.method == "GET":
        form.name.data = role.name
        auths = role.auths
        form.auths.data = list(map(lambda v: int(v), auths.split(",")))

    if form.validate_on_submit():
        data = form.data

        role.name = data["name"];
        role.auths = ",".join(map(lambda v: str(v), data['auths']))
        db.session.add(role)
        db.session.commit()
        flash("编辑角色成功!", "ok")
        redirect(url_for('admin.role_edit', id=id))
    return render_template("admin/role_edit.html", form=form, role=role)


# 角色列表
@admin.route("/role/list/<int:page>/")
@admin_login_req
def role_list(page=None):
    if page is None:
        page = 1
    page_data = Role.query.filter().order_by(
        Role.addtime.desc()
    ).paginate(page=page, per_page=10)

    return render_template("admin/role_list.html", page_data=page_data)


# 角色删除
@admin.route("/role/del/<int:id>/", methods=["GET", "POST"])
@admin_login_req
def role_del(id=None):
    role = Role.query.get_or_404(int(id))
    db.session.delete(role)
    db.session.commit()
    flash("角色删除成功!", "ok")

    return redirect(url_for('admin.role_list', page=1))


# 管理员添加
@admin.route("/admin/add/", methods=["GET", "POST"])
@admin_login_req
def admin_add():
    form = AdminForm()
    if form.validate_on_submit():
        data = form.data

        from werkzeug.security import generate_password_hash
        admin = Admin(
            name=data["name"],
            role_id=data["role_id"],
            pwd=generate_password_hash(data["pwd"]),
            is_super=1
        )

        db.session.add(admin)
        db.session.commit()
        flash("角色添加成功!", "ok")
        return redirect(url_for("admin.admin_add"))

    return render_template("admin/admin_add.html", form=form)


# 管理员编辑
@admin.route("/admin/edit/<int:id>/", methods=["GET", "POST"])
@admin_login_req
def admin_edit(id=None):
    form = AdminForm()
    admin = Admin.query.get_or_404(int(id))

    if request.method == "GET":
        form.role_id.data = admin.role_id
        form.name = admin.name

    if form.validate_on_submit():
        data = form.data

        from werkzeug.security import generate_password_hash
        admin.name = data["name"]
        admin.role_id = data["role_id"]
        admin.pwd = generate_password_hash(data["pwd"])
        admin.is_super = 1

        db.session.add(admin)
        db.session.commit()
        flash("角色编辑成功!", "ok")

        return redirect(url_for("admin.admin_edit", id=admin.id))
    return render_template("admin/admin_edit.html", form=form)


# 管理员删除
# @admin.route("/admin/del/<int:id>/")
# @admin_login_req
# def admin_del(id=None):
#     admin = Admin.query.get_or_404(int(id))
#     db.session.delete(admin)
#     db.session.commit()
#     flash("管理员删除成功!", "ok")
#
#     return redirect(url_for("admin.admin_list", page=1))


# 管理员列表
@admin.route("/admin/list/<int:page>/")
@admin_login_req
def admin_list(page=None):
    if page is None:
        page = 1
    page_data = Admin.query.join(
        Role
    ).filter(
        Role.id == Admin.role_id
    ).order_by(
        Admin.addtime.desc()
    ).paginate(page=page, per_page=10)

    return render_template("admin/admin_list.html", page_data=page_data)
