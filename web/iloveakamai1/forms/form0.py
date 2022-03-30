from flask import flash, escape
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired


class form0(FlaskForm):
    TextData = TextAreaField("TextData_Lable", default='', render_kw={"placeholder": "text"}, validators=[DataRequired(message='Field required')])
    form0Submit = SubmitField('form0')


def run(form):
    lines = escape(form['TextData'].data)
    flash(lines, 'success')
    return None
