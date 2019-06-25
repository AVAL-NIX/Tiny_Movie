# coding:utf8

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError, TextAreaField, FileField
from wtforms.validators import DataRequired, EqualTo, Email, Regexp
from app.models import User


# 注册
class RegistForm(FlaskForm):
    name = StringField(
        label="昵称",
        validators=[
            DataRequired("请输入昵称!")
        ],
        description="昵称",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入昵称!"
        }
    )

    email = StringField(
        label="邮箱",
        validators=[
            DataRequired("请输入邮箱!"),
            Email("邮箱格式不正确")
        ],
        description="邮箱",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入邮箱!"
        }
    )

    phone = StringField(
        label="手机",
        validators=[
            DataRequired("请输入手机!"),
            Regexp("1[34589]\\d{9}", message="手机格式不正确")
        ],
        description="手机",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入手机!"
        }
    )

    pwd = PasswordField(
        label="密码 ",
        validators=[
            DataRequired("请输入密码!")
        ],
        description="密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入密码!"
        }
    )

    repwd = PasswordField(
        label="重复密码 ",
        validators=[
            DataRequired("请输入重复密码!"),
            EqualTo('pwd', "两次密码不一致")
        ],
        description="重复密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入重复密码!"
        }
    )

    submit = SubmitField(
        '注册',
        render_kw={
            "class": "btn btn-lg btn-success btn-block",
        }
    )

    def validate_name(self, field):
        name = field.data
        user = User.query.filter_by(name=name).count()
        if user >= 1:
            raise ValidationError("用户名存在")

    def validate_phone(self, field):
        phone = field.data
        phone = User.query.filter_by(phone=phone).count()
        if phone >= 1:
            raise ValidationError("手机存在")

    def validate_email(self, field):
        email = field.data
        email = User.query.filter_by(email=email).count()
        if email >= 1:
            raise ValidationError("邮箱存在")


class LoginForm(FlaskForm):
    """ 用户录表单"""

    name = StringField(
        label="帐号",
        validators=[
            DataRequired("请输入帐号!")
        ],
        description="帐号",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入账号！",
        }

    )

    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("请输入密码!")
        ],
        description="密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入密码！",
        }

    )

    submit = SubmitField(
        '登录',
        render_kw={
            "class": "btn btn-primary btn-block btn-flat",
        }
    )

    def validate_name(self, field):
        name = field.data
        user = User.query.filter_by(name=name).count()
        if user == 0:
            raise ValidationError("帐号不存在")


# 修改会员资料
class UserdeatailForm(FlaskForm):
    name = StringField(
        label="昵称",
        validators=[
            DataRequired("请输入昵称!")
        ],
        description="昵称",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入昵称!"
        }
    )

    email = StringField(
        label="邮箱",
        validators=[
            DataRequired("请输入邮箱!"),
            Email("邮箱格式不正确")
        ],
        description="邮箱",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入邮箱!"
        }
    )

    phone = StringField(
        label="手机",
        validators=[
            DataRequired("请输入手机!"),
            Regexp("1[34589]\\d{9}", message="手机格式不正确")
        ],
        description="手机",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入手机!"
        }
    )

    info = TextAreaField(
        label="简介",
        validators=[
            DataRequired("请输入简介!")
        ],
        description="简介",
        render_kw={
            "class": "form-control",
            "row": "10"
        }

    )

    face = FileField(
        label="头像",
        validators=[
            DataRequired("请输入头像!")
        ],
        description="个人头像",
        render_kw={
            "required": False
        }
    )

    submit = SubmitField(
        label='保存修改',
        render_kw={
            "class": "btn btn-success",
        }
    )

# 修改密码类
class PwdForm(FlaskForm):
    old_pwd = PasswordField(
        label="旧密码 ",
        validators=[
            DataRequired("请输入旧密码!")
        ],
        description="旧密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入旧密码!"
        }
    )

    new_pwd = PasswordField(
        label="新密码 ",
        validators=[
            DataRequired("请输入新密码!")
        ],
        description="新密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入新密码!"
        }
    )

    submit = SubmitField(
        '编辑',
        render_kw={
            "class": "btn btn-primary btn-block btn-flat",
        }
    )


    def validate_old_pwd(self, field):
        from flask import session
        pwd = field.data
        name = session["user"]
        user = User.query.filter_by(name = name).first()
        if not user.check_pwd(pwd):
            raise ValidationError("老密码不一致")


class CommentForm(FlaskForm):
    content = TextAreaField(
        label="内容",
        validators=[
            DataRequired("请输入内容!")
        ],
        description="内容",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入内容!"
        }
    )

    submit = SubmitField(
        label='提交评论',
        render_kw={
            "class": "btn btn-success",
            "id" :"btn-sub"
        }
    )