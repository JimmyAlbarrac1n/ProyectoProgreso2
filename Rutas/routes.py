from flask import Blueprint, abort, render_template, session, redirect, request, url_for, current_app, flash
from Rutas.forms import MaterialForm, ExtendedMaterialForm, RegisterForm, LoginForm
import uuid
import copy
import datetime
import functools
from dataclasses import asdict
from Rutas.models import Material, User
from passlib.hash import pbkdf2_sha256

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

@pages.route("/")
@login_required
def index():
    user_data = current_app.db.user.find_one({"email": session["email"]})
    if "ratings" in user_data:
        del user_data["ratings"]
    user = User(**user_data)
    if user.role == "profesor":
        materiales_data = current_app.db.material.find({"_id": {"$in": user.materials}})
    else:
        materiales_data = current_app.db.material.find({})
    materiales = [Material(**material) for material in materiales_data]
    return render_template(
        "index.html",
        title="Material Aprendizaje",
        materiales_data=materiales,
        user=user
    )

@pages.route("/register", methods=["GET", "POST"])
def register():
    if session.get("email"):
        return redirect(url_for(".index"))
    
    form = RegisterForm()

    if form.validate_on_submit():
        user = User(
            _id=uuid.uuid4().hex,
            email=form.email.data,
            username=form.username.data,
            password=pbkdf2_sha256.hash(form.password.data),
            role="estudiante"
        )
        current_app.db.user.insert_one(asdict(user))
        flash("Usuario registrado correctamente", "success")
        return redirect(url_for(".login"))
        
    return render_template("register.html", title="Registrar", form=form)

@pages.route("/login", methods=["GET", "POST"])
def login():
    if session.get("email"):
        return redirect(url_for(".index"))
    
    form = LoginForm()

    if form.validate_on_submit():
        user_data = current_app.db.user.find_one({"email": form.email.data})
        if not user_data:
            flash("Correo electrónico o contraseña incorrectos", category="danger")
            return redirect(url_for(".login"))
        
        if "ratings" in user_data:
            del user_data["ratings"]
        user = User(**user_data)
        if user and pbkdf2_sha256.verify(form.password.data, user.password):
            session["user_id"] = user._id
            session["email"] = user.email
            return redirect(url_for(".index"))
        
        flash("Correo electrónico o contraseña incorrectos", category="danger")
        
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
    return render_template(
        "material_details.html",
        material=material,
        user=user
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
    