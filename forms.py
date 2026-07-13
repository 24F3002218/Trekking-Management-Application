from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    role = SelectField("Register As", choices=[("user", "Trekker (User)"), ("staff", "Trek Staff")])
    phone = StringField("Phone", validators=[Optional(), Length(max=20)])
    contact = StringField("Contact / Emergency Number", validators=[Optional(), Length(max=100)])
    experience_years = IntegerField("Years of Experience", validators=[Optional(), NumberRange(min=0)])
    specialization = StringField("Specialization", validators=[Optional(), Length(max=150)])
    submit = SubmitField("Register")


class ProfileForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField("Phone", validators=[Optional(), Length(max=20)])
    address = StringField("Address", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Update Profile")


class TrekForm(FlaskForm):
    name = StringField("Trek Name", validators=[DataRequired(), Length(max=150)])
    location = StringField("Location", validators=[DataRequired(), Length(max=150)])
    difficulty = SelectField("Difficulty", choices=[("Easy", "Easy"), ("Moderate", "Moderate"), ("Hard", "Hard")])
    duration_days = IntegerField("Duration (Days)", validators=[DataRequired(), NumberRange(min=1, max=60)])
    max_slots = IntegerField("Maximum Slots", validators=[DataRequired(), NumberRange(min=1, max=500)])
    start_date = DateField("Start Date", validators=[DataRequired()], format="%Y-%m-%d")
    end_date = DateField("End Date", validators=[DataRequired()], format="%Y-%m-%d")
    description = TextAreaField("Description", validators=[Optional()])
    status = SelectField(
        "Status",
        choices=[
            ("Pending", "Pending"),
            ("Approved", "Approved"),
            ("Open", "Open"),
            ("Closed", "Closed"),
            ("Completed", "Completed"),
        ],
    )
    assigned_staff_id = SelectField("Assigned Staff", coerce=int, validators=[Optional()])
    submit = SubmitField("Save Trek")


class StaffTrekUpdateForm(FlaskForm):
    available_slots = IntegerField("Available Slots", validators=[DataRequired(), NumberRange(min=0)])
    status = SelectField("Status", choices=[("Open", "Open"), ("Closed", "Closed")])
    submit = SubmitField("Update Trek")


class SearchForm(FlaskForm):
    q = StringField("Search", validators=[Optional()])
    submit = SubmitField("Search")


class TrekFilterForm(FlaskForm):
    location = StringField("Location", validators=[Optional()])
    difficulty = SelectField(
        "Difficulty",
        choices=[("", "All"), ("Easy", "Easy"), ("Moderate", "Moderate"), ("Hard", "Hard")],
    )
    submit = SubmitField("Filter")
