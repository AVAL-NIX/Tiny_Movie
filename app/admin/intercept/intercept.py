# coding:utf8

# 权限装饰器
from app.models import Role, Admin, Auth
from flask import session, request, abort, redirect,url_for
from functools import wraps

# 权限装饰器
def admin_auth(f):
    """ 权限装饰器 """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin = Admin.query.join(
            Role
        ).filter(
            Role.id == Admin.role_id,
            Admin.id == session["admin_id"]
        ).first()
        auths = str(admin.role.auths)
        auths = list(map(lambda v: int(v), auths.split(",")))
        auth_list = Auth.query.all()
        urls = [v.url for v in auth_list for val in auths if val == v.id]
        rule = request.url_rule
        if rule not in urls:
            abort(404)
            return f(*args, **kwargs)

    return decorated_function


# 登录装饰器
def admin_login_req(f):
    """ 登录拦截 """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("admin.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


# 登录装饰器
def user_login_req(f):
    """ 登录拦截 """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("home.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function