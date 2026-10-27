import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

class RegistrationForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[
        DataRequired(message="Vui lòng nhập tên đăng nhập."),
        Length(min=4, max=20, message="Độ dài phải từ 4 đến 20 ký tự.")
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message="Vui lòng nhập email."),
        Email(message="Email không đúng định dạng.")
    ])
    
    password = PasswordField('Mật khẩu', validators=[
        DataRequired(message="Vui lòng nhập mật khẩu."),
        Length(min=8, message="Mật khẩu tối thiểu 8 ký tự.")
    ])
    
    confirm_password = PasswordField('Nhập lại mật khẩu', validators=[
        DataRequired(message="Vui lòng nhập lại mật khẩu."),
        EqualTo('password', message="Mật khẩu nhập lại không khớp.")
    ])
    
    accept_terms = BooleanField('Đồng ý điều khoản', validators=[
        DataRequired(message="Bạn phải đồng ý với điều khoản.")
    ])
    
    submit = SubmitField('Đăng ký')

    def __init__(self, users_dict=None, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.users_dict = users_dict if users_dict is not None else {}

    def validate_username(self, field):
        pattern = r'^[a-z0-9_]+$'
        if not re.match(pattern, field.data):
            raise ValidationError('Chỉ cho phép chữ thường không dấu, số và dấu gạch dưới (_).')
        
        if field.data in self.users_dict:
            raise ValidationError('Tên đăng nhập đã được sử dụng.')