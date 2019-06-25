#coding:utf8
from flask import Flask
from flask import render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pymysql
import os

app = Flask(__name__)
# 定义数据连接
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:123456@127.0.0.1:3306/movie"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
# 定义上传路径
app.config["UP_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/")
app.config["FC_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/users/")
app.debug=True
app.config["SECRET_KEY"]='f5911629db964d869eb21cceaabefb7f'
# db 对象
db = SQLAlchemy(app)


from app.home import home as home_bulueprint
from app.admin import admin as admin_bulueprint

app.register_blueprint(home_bulueprint)
app.register_blueprint(admin_bulueprint, url_prefix="/admin")


@app.errorhandler(404)
def page_not_found(error):
    return render_template("home/404.html") , 404