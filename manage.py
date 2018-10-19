from flask_script import Manager
from app import create_app, db

app = create_app('development')

manager = Manager(app)


@manager.command
def make_shell_context():
    return dict(app=app, db=db)


if __name__ == '__main__':
    manager.run()
