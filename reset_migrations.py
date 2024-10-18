from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'your_database_uri_here'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

def reset_migrations():
    with app.app_context():
        db.engine.execute("DELETE FROM alembic_version")
        print("Cleared alembic_version table")

if __name__ == '__main__':
    reset_migrations()

