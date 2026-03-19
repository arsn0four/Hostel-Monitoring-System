from flask import Flask, redirect, url_for
from extensions import db, login_manager, bcrypt
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from models.db_models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.auth_routes import auth
    from routes.admin_routes import admin
    from routes.warden_routes import warden
    from routes.student_routes import student
    from routes.chatbot_routes import chatbot
    
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(warden)
    app.register_blueprint(student)
    app.register_blueprint(chatbot)

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
