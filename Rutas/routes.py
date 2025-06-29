from flask import Blueprint, abort, render_template, session, redirect, request, url_for, current_app, flash
from Rutas.forms import MaterialForm, ExtendedMaterialForm, RegisterForm, LoginForm
from Rutas.UserRepository import UserRepository
import uuid
import uuid
import copy
import datetime
import functools
from dataclasses import asdict
from Rutas.models import Material, User
from Rutas.UserService import UserService
import uuid
from passlib.hash import pbkdf2_sha256

user_repo = UserRepository()
user_service = UserService(user_repo)

pages = Blueprint(
    "pages", __name__, template_folder="templates", static_folder="static"
)

def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if session.get("email") is None:
            return redirect(url_for(".login"))
        return route(*args, **kwargs)
    return route_wrapper

def role_required(role):
    def decorator(route):
        @functools.wraps(route)
        def wrapper(*args, **kwargs):
            user_data = current_app.db.user.find_one({"email": session.get("email")})
            if not user_data or user_data.get("role") != role:
                abort(403)
            return route(*args, **kwargs)
        return wrapper
    return decorator

def admin_required(route):
    @functools.wraps(route)
    def wrapper(*args, **kwargs):
        user_data = current_app.db.user.find_one({"email": session.get("email")})
        if not user_data or user_data.get("role") != "admin":
            abort(403)
        return route(*args, **kwargs)
    return wrapper

@pages.route("/")
@login_required
def index():
    user_data = current_app.db.user.find_one({"email": session["email"]})
    if "ratings" in user_data:
        del user_data["ratings"]
    user = User(**user_data)
    if user.role == "admin":
        return redirect(url_for(".admin_users"))
    if user.role == "profesor":
        materiales_data = current_app.db.material.find({"_id": {"$in": user.materials}})
    else:
        materiales_data = current_app.db.material.find({})
    materiales = []
    materiales_profesores = []
    for material in materiales_data:
        mat = Material(**material)
        # Buscar el profesor dueño del material
        profesor_data = current_app.db.user.find_one({"materials": mat._id, "role": "profesor"})
        profesor = User(**profesor_data) if profesor_data else None
        materiales.append(mat)
        materiales_profesores.append(profesor)
    materiales_zip = list(zip(materiales, materiales_profesores))
    return render_template(
        "index.html",
        title="Material Aprendizaje",
        materiales_zip=materiales_zip,
        user=user
    )

@pages.route("/register", methods=["GET", "POST"])
def register():
    if session.get("email"):
        return redirect(url_for(".index"))
    form = RegisterForm()
    if form.validate_on_submit():
        success, message = user_service.register_user(
            form.email.data, form.username.data, form.password.data
        )
        flash(message, "success" if success else "danger")
        if success:
            return redirect(url_for(".login"))
        return redirect(url_for(".register"))
    return render_template("register.html", title="Registrar", form=form)

@pages.route("/login", methods=["GET", "POST"])
def login():
    if session.get("email"):
        return redirect(url_for(".index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = user_service.authenticate(form.email.data, form.password.data)
        if not user:
            flash("Correo electrónico o contraseña incorrectos", category="danger")
            return redirect(url_for(".login"))
        session["user_id"] = user["_id"]
        session["email"] = user["email"]
        return redirect(url_for(".index"))
    return render_template("login.html", title="Iniciar sesión", form=form)

@pages.route("/logout")
def logout():
    session.clear()
    return redirect(url_for(".login"))

@pages.route("/add", methods=["GET", "POST"])
@login_required
@role_required("profesor")
def add_material():
    form = MaterialForm()
    if form.validate_on_submit():
        material = Material(
            _id=uuid.uuid4().hex,
            title=form.title.data,
            description=form.description.data,
            url=form.url.data,
        )
        material_dict = asdict(material)
        # Asegúrate de que created_at sea datetime
        if isinstance(material_dict["created_at"], str):
            from datetime import datetime
            material_dict["created_at"] = datetime.strptime(material_dict["created_at"], "%Y-%m-%dT%H:%M:%S.%f")
        current_app.db.material.insert_one(material_dict)
        current_app.db.user.update_one(
            {"_id": session["user_id"]},
            {"$push": {"materials": material._id}}
        )
        return redirect(url_for(".index"))

    return render_template(
        "new_material.html", 
        title="Nuevo Material",
        form=form
    )

@pages.route("/edit/<material_id>", methods=["GET", "POST"])
@login_required
@role_required("profesor")
def edit_material(material_id: str):
    material = Material(**current_app.db.material.find_one({"_id": material_id}))
    form = ExtendedMaterialForm(obj=material)
    if form.validate_on_submit():
        material.title = form.title.data
        material.description = form.description.data
        material.url = form.url.data
        material.tags = form.tags.data
        current_app.db.material.update_one({"_id": material_id}, {"$set": asdict(material)})
        return redirect(url_for(".material", material_id=material_id))
   
    return render_template("material_form.html", material=material, form=form)

@pages.get("/material/<material_id>")
@login_required
def material(material_id: str):
    material_data = current_app.db.material.find_one({"_id": material_id})
    if not material_data:
        abort(404)
    material = Material(**material_data)
    user_data = current_app.db.user.find_one({"email": session["email"]})
    if "ratings" in user_data:
        del user_data["ratings"]
    user = User(**user_data)
    # Obtener el profesor dueño del material
    profesor_data = None
    profesor = None
    if hasattr(material, 'created_at'):
        # Buscar el profesor que tenga este material en su lista
        profesor_data = current_app.db.user.find_one({"materials": material._id, "role": "profesor"})
        if profesor_data:
            profesor = User(**profesor_data)
    return render_template(
        "material_details.html",
        material=material,
        user=user,
        profesor=profesor
    )

@pages.get("/material/<material_id>/rate")
@login_required
@role_required("estudiante")
def rate_material(material_id):
    rating = int(request.args.get("rating"))
    user_id = session["user_id"]
    material_data = current_app.db.material.find_one({"_id": material_id})
    if not material_data:
        abort(404)
    ratings = material_data.get("ratings", {})
    ratings[user_id] = rating
    avg_rating = round(sum(ratings.values()) / len(ratings), 2)
    current_app.db.material.update_one(
        {"_id": material_id},
        {"$set": {"ratings": ratings, "rating": avg_rating}}
    )
    return redirect(url_for(".material", material_id=material_id))

@pages.get("/material/<material_id>/watch")
@login_required
@role_required("estudiante")
def watch_today(material_id):
    current_app.db.user.update_one(
        {"_id": session["user_id"]},
        {"$addToSet": {"watched": material_id}}
    )
    return redirect(url_for(".material", material_id=material_id))

@pages.get("/toggle-theme")
def toggle_theme():
    current_theme = session.get("theme", "light")
    if current_theme == "dark":
        session["theme"] = "light"
    else:
        session["theme"] = "dark"
    return redirect(request.args.get("current_page", url_for("pages.index")))

@pages.get("/profesor/<profesor_id>/rate")
@login_required
@role_required("estudiante")
def rate_profesor(profesor_id):
    rating = int(request.args.get("rating"))
    user_id = session["user_id"]
    profesor_data = current_app.db.user.find_one({"_id": profesor_id, "role": "profesor"})
    if not profesor_data:
        abort(404)
    ratings = profesor_data.get("ratings", {})
    ratings[user_id] = rating
    avg_rating = round(sum(ratings.values()) / len(ratings), 2)
    current_app.db.user.update_one(
        {"_id": profesor_id},
        {"$set": {"ratings": ratings, "rating": avg_rating}}
    )
    # Redirigir a la página de material si viene de ahí, o a la principal
    next_url = request.args.get("next")
    if next_url:
        return redirect(next_url)
    return redirect(url_for(".index"))

@pages.route("/admin/users")
@login_required
@admin_required
def admin_users():
    users = list(current_app.db.user.find({"role": {"$in": ["profesor", "estudiante"]}}))
    return render_template("admin_users.html", users=users)

@pages.route("/admin/users/create", methods=["GET", "POST"])
@login_required
@admin_required
def admin_create_user():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            _id=uuid.uuid4().hex,
            email=form.email.data,
            username=form.username.data,
            password=pbkdf2_sha256.hash(form.password.data),
            role=request.form.get("role", "profesor")
        )
        current_app.db.user.insert_one(asdict(user))
        flash("Usuario creado correctamente", "success")
        return redirect(url_for(".admin_users"))
    return render_template("admin_user_form.html", form=form, action="Crear")

@pages.route("/admin/users/edit/<user_id>", methods=["GET", "POST"])
@login_required
@admin_required
def admin_edit_user(user_id):
    user_data = current_app.db.user.find_one({"_id": user_id})
    if not user_data:
        abort(404)
    form = RegisterForm(data=user_data)
    if form.validate_on_submit():
        update_data = {
            "email": form.email.data,
            "username": form.username.data,
            "role": request.form.get("role", user_data.get("role", "profesor"))
        }
        if form.password.data:
            update_data["password"] = pbkdf2_sha256.hash(form.password.data)
        current_app.db.user.update_one({"_id": user_id}, {"$set": update_data})
        flash("Usuario actualizado", "success")
        return redirect(url_for(".admin_users"))
    return render_template("admin_user_form.html", form=form, action="Editar")

@pages.route("/admin/users/delete/<user_id>", methods=["POST"])
@login_required
@admin_required
def admin_delete_user(user_id):
    current_app.db.user.delete_one({"_id": user_id})
    flash("Usuario eliminado", "success")
    return redirect(url_for(".admin_users"))
