from flask import Blueprint, render_template

projects_bp = Blueprint('projects', __name__, template_folder="templates", static_folder="static", static_url_path="/static/projects")

@projects_bp.route('/everyday-apps')
def everyday_apps():
    return render_template('projects/everyday_apps.html')

@projects_bp.route('/community-service-apps')
def community_service_apps():
    return render_template('projects/community_service_apps.html')

@projects_bp.route('/games')
def games():
    return render_template('projects/games.html')