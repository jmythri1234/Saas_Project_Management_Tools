from datetime import datetime, date
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user,
    login_required, logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash


# -------------------- APP CONFIGURATION --------------------

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = "projectflow-dev-key-change-before-deployment"
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" + str(INSTANCE_DIR / "project_management.db")
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# -------------------- DATABASE MODELS --------------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    projects = db.relationship(
        "Project",
        backref="owner",
        cascade="all, delete-orphan",
        lazy=True
    )


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, default="")
    status = db.Column(db.String(30), default="Active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.Date, nullable=True)

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    tasks = db.relationship(
        "Task",
        backref="project",
        cascade="all, delete-orphan",
        lazy=True
    )


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    status = db.Column(db.String(30), default="Pending")
    priority = db.Column(db.String(20), default="Medium")
    due_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("project.id"),
        nullable=False
    )


# -------------------- LOGIN MANAGER --------------------

@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None


# -------------------- HELPER FUNCTIONS --------------------

def parse_date(value):
    if not value:
        return None

    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def get_user_project(project_id):
    return Project.query.filter_by(
        id=project_id,
        owner_id=current_user.id
    ).first_or_404()


def get_user_task(task_id):
    return (
        Task.query
        .join(Project)
        .filter(
            Task.id == task_id,
            Project.owner_id == current_user.id
        )
        .first_or_404()
    )


# -------------------- HOME PAGE --------------------

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    return render_template("index.html")


# -------------------- REGISTER --------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("Please fill in all required fields.", "warning")
            return render_template("register.html")

        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "warning")
            return render_template("register.html")

        if confirm_password and password != confirm_password:
            flash("Passwords do not match.", "warning")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("This email is already registered.", "warning")
            return render_template("register.html")

        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# -------------------- LOGIN --------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Welcome back!", "success")

            next_page = request.args.get("next", "")

            if next_page.startswith("/") and not next_page.startswith("//"):
                return redirect(next_page)

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "warning")

    return render_template("login.html")


# -------------------- LOGOUT --------------------

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


# -------------------- DASHBOARD --------------------

@app.route("/dashboard")
@login_required
def dashboard():
    projects = Project.query.filter_by(
        owner_id=current_user.id
    ).order_by(Project.created_at.desc()).all()

    tasks = (
        Task.query
        .join(Project)
        .filter(Project.owner_id == current_user.id)
        .order_by(Task.created_at.desc())
        .all()
    )

    total_projects = len(projects)
    total_tasks = len(tasks)

    completed_tasks = sum(
        1 for task in tasks if task.status == "Completed"
    )

    pending_tasks = sum(
        1 for task in tasks if task.status != "Completed"
    )

    completion_rate = (
        round(completed_tasks * 100 / total_tasks)
        if total_tasks else 0
    )

    upcoming_tasks = sorted(
        [
            task for task in tasks
            if task.due_date
            and task.due_date >= date.today()
            and task.status != "Completed"
        ],
        key=lambda task: task.due_date
    )[:5]

    return render_template(
        "dashboard.html",
        projects=projects,
        tasks=tasks,
        total_projects=total_projects,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        completion_rate=completion_rate,
        upcoming_tasks=upcoming_tasks
    )


# -------------------- PROJECTS --------------------

@app.route("/projects", methods=["GET", "POST"])
@login_required
def projects():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        due_date_value = request.form.get("due_date", "")

        if not name:
            flash("Project name is required.", "warning")
        else:
            project = Project(
                name=name,
                description=description,
                due_date=parse_date(due_date_value),
                owner_id=current_user.id
            )

            db.session.add(project)
            db.session.commit()

            flash("Project created successfully!", "success")
            return redirect(url_for("projects"))

    user_projects = Project.query.filter_by(
        owner_id=current_user.id
    ).order_by(Project.created_at.desc()).all()

    return render_template(
        "projects.html",
        projects=user_projects
    )


# -------------------- PROJECT DETAILS --------------------

@app.route("/projects/<int:project_id>")
@login_required
def project_details(project_id):
    project = get_user_project(project_id)

    total_tasks = len(project.tasks)

    completed_tasks = sum(
        1 for task in project.tasks if task.status == "Completed"
    )

    progress = (
        round(completed_tasks * 100 / total_tasks)
        if total_tasks else 0
    )

    return render_template(
        "project_details.html",
        project=project,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        progress=progress
    )


# -------------------- DELETE PROJECT --------------------

@app.route("/projects/<int:project_id>/delete", methods=["POST"])
@login_required
def delete_project(project_id):
    project = get_user_project(project_id)

    db.session.delete(project)
    db.session.commit()

    flash("Project deleted successfully.", "success")
    return redirect(url_for("projects"))


# -------------------- PROJECT TASKS --------------------

@app.route(
    "/projects/<int:project_id>/tasks",
    methods=["GET", "POST"]
)
@login_required
def tasks(project_id):
    project = get_user_project(project_id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        priority = request.form.get("priority", "Medium")
        due_date_value = request.form.get("due_date", "")

        if not title:
            flash("Task title is required.", "warning")
        elif priority not in ["Low", "Medium", "High"]:
            flash("Please select a valid priority.", "warning")
        else:
            task = Task(
                title=title,
                description=description,
                priority=priority,
                due_date=parse_date(due_date_value),
                project_id=project.id
            )

            db.session.add(task)
            db.session.commit()

            flash("Task created successfully!", "success")
            return redirect(
                url_for("tasks", project_id=project.id)
            )

    project_tasks = Task.query.filter_by(
        project_id=project.id
    ).order_by(Task.created_at.desc()).all()

    return render_template(
        "tasks.html",
        project=project,
        tasks=project_tasks
    )


# -------------------- UPDATE TASK STATUS --------------------

@app.route("/tasks/<int:task_id>/status", methods=["POST"])
@login_required
def update_task_status(task_id):
    task = get_user_task(task_id)

    new_status = request.form.get("status", "").strip()

    allowed_statuses = ["Pending", "In Progress", "Completed"]

    if new_status not in allowed_statuses:
        flash("Please select a valid task status.", "warning")
    else:
        task.status = new_status
        db.session.commit()
        flash("Task status updated successfully.", "success")

    return redirect(
        url_for("tasks", project_id=task.project_id)
    )


# -------------------- TEAM PAGE --------------------

@app.route("/team")
@login_required
def team():
    return render_template("team.html")


# -------------------- CREATE DATABASE --------------------

with app.app_context():
    db.create_all()


# -------------------- RUN APPLICATION --------------------

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)