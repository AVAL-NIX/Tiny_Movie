# coding:utf8
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError, EqualTo , Email
from app.models import Admin, Tag, Movie, Auth, Role



tags = Tag.query.all()


class LoginForm(FlaskForm):
    """ 管理员登录表单"""

    account = StringField(
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

    def validate_account(self, field):
        account = field.data
        admin = Admin.query.filter_by(name=account).count()
        if admin == 0:
            raise ValidationError("帐号不存在")


class MovieForm(FlaskForm):
    title = StringField(
        label="片名",
        validators=[
            DataRequired("请输入片名!")
        ],
        description="片名",
        render_kw={
            "class": "form-control",
            "id": "input_title",
            "placeholder": "请输入片名!"
        }
    )

    url = FileField(
        label="文件",
        validators=[
            DataRequired("请上传文件!"),
        ],
        description="文件",
        render_kw={
            "required":False
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

    logo = FileField(
        label="封面",
        validators=[
            DataRequired("请输入封面!")
        ],
        description="封面",
        render_kw={
            "required":False
        }
    )
    star = SelectField(
        label="星级",
        validators=[
            DataRequired("请选择星级!")
        ],
        description="简介",
        coerce=int,
        choices=[(1, "1星"), (2, "2星"), (3, "3星"), (4, "4星"), (5, "5星")],
        render_kw={
            "class": "form-control",
        }
    )
    tag_id = SelectField(
        label="标签",
        validators=[
            DataRequired("请选择标签!")
        ],
        description="标签",
        coerce=int,
        choices=[(v.id, v.name) for v in tags],
        render_kw={
            "class": "form-control",
        }
    )

    area = StringField(
        label="地区",
        validators=[
            DataRequired("请输入地区!")
        ],
        description="地区",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入地区!"
        }
    )

    length = StringField(
        label="片长",
        validators=[
            DataRequired("请输入片长!")
        ],
        description="片长",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入片长!"
        }
    )

    release_time = StringField(
        label="上映时间",
        validators=[
            DataRequired("请选择上映时间!")
        ],
        description="上映时间",
        render_kw={
            "class": "form-control",
            "placeholder": "请选择上映时间!",
            "id": "input_release_time"
        }
    )

    submit = SubmitField(
        '编辑',
        render_kw={
            "class": "btn btn-primary btn-block btn-flat",
        }
    )


class TagForm(FlaskForm):
    name = StringField(
        label="标签名",
        validators=[
            DataRequired("请输入标签名!")
        ],
        description="标签名",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入标签名!"
        }
    )

    submit = SubmitField(
        '编辑',
        render_kw={
            "class": "btn btn-primary btn-block btn-flat",
        }
    )


class PreviewForm(FlaskForm):
    title = StringField(
        label="预告标题",
        validators=[
            DataRequired("请输入标签名!")
        ],
        description="预告标题我",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入标签名!"
        }
    )

    logo = FileField(
        label="预告封面",
        validators=[
            DataRequired("请输入预告封面!")
        ],
        description="封面",
        render_kw={
            "required":False
        }
    )

    submit = SubmitField(
        '编辑',
        render_kw={
            "class": "btn btn-primary btn-block btn-flat",
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
        name = session["admin"]
        admin = Admin.query.filter_by(name = name).first()
        if not admin.check_pwd(pwd):
            raise ValidationError("老密码不一致")

# 权限
class AuthForm(FlaskForm):
    name = StringField(
        label="权限名 ",
        validators=[
            DataRequired("请输入权限名!")
        ],
        description="权限名",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入权限名!"
        }
    )

    url = StringField(
        label="权限地址 ",
        validators=[
            DataRequired("请输入权限地址!")
        ],
        description="权限地址",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入权限地址!"
        }
    )

    submit = SubmitField(
        '编辑',
        render_kw={
            "class": "btn btn-primary btn-block btn-flat",
        }
    )


# 角色
auth_list = Auth.query.all()

class RoleForm(FlaskForm):
    name = StringField(
        label="角色名 ",
        validators=[
            DataRequired("请输入角色名!")
        ],
        description="角色名",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入角色名!"
        }
    )

    auths = SelectMultipleField(
        label="权限列表 ",
        validators=[
            DataRequired("请输入权限列表!")
        ],
        description="权限列表",
        coerce=int,
        choices=[(v.id,v.name) for v in auth_list],
        render_kw={
            "class": "form-control",
            "placeholder": "请输入权限列表!"
        }
    )

    submit = SubmitField(
        '编辑',
        render_kw={
            "class": "btn btn-primary btn-block btn-flat",
        }
    )

# 管理员
role_list = Role.query.all()

class AdminForm(FlaskForm):
    name = StringField(
        label="帐号 ",
        validators=[
            DataRequired("请输入帐号!")
        ],
        description="帐号",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入帐号!"
        }
    )

    pwd = PasswordField(
        label="密码 ",
        validators=[
            DataRequired("请输入密码!"),
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
            EqualTo('pwd',"两次密码不一致")
        ],
        description="重复密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入重复密码!"
        }
    )

    role_id = SelectField(
        label="角色列表 ",
        validators=[
            DataRequired("请输入角色列表!")
        ],
        description="角色列表",
        coerce=int,
        choices=[(v.id,v.name) for v in role_list],
        render_kw={
            "class": "form-control",
            "placeholder": "请输入角色列表!"
        }
    )

    submit = SubmitField(
        '编辑',
        render_kw={
            "class": "btn btn-primary btn-block btn-flat",
        }
    )