from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, URLField, PasswordField
from wtforms.validators import InputRequired, URL, Length, Email, EqualTo

class MaterialForm(FlaskForm):
    title = StringField('Título', validators=[InputRequired(), Length(max=30, message="Máximo 30 caracteres")])
    description = TextAreaField('Descripción', validators=[InputRequired(), Length(max=100, message="Máximo 50 caracteres")])
    url = URLField('Link', validators=[InputRequired(), URL()])
    submit = SubmitField('Guardar')

class StringListField(TextAreaField):
    def _value(self):
        if self.data:
            return "\n".join(self.data)
        else:
            return ""
        
    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            self.data = [line.strip() for line in valuelist[0].split("\n")]
        else:
            self.data = []


class ExtendedMaterialForm(MaterialForm):
    tags = StringListField("Etiquetas")
    submit = SubmitField("Guardar")


class RegisterForm(FlaskForm):
    email = StringField("Correo electrónico", validators=[InputRequired(), Email()])
    username = StringField("Nombre de usuario", validators=[InputRequired(), Length(min=3, max=20)])
    password = PasswordField("Contraseña", validators=[InputRequired(), Length(min=6, max=20, message="Mínimo 6 caracteres y máximo 20 caracteres")])
    confirm_password = PasswordField("Confirmar contraseña", validators=[InputRequired(), EqualTo("password", message="Las contraseñas no coinciden")])
    submit = SubmitField("Registrar")

class LoginForm(FlaskForm):
    email = StringField("Correo electrónico", validators=[InputRequired(), Email()])
    password = PasswordField("Contraseña", validators=[InputRequired()])
    submit = SubmitField("Iniciar sesión")
