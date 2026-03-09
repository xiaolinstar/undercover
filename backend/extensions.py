from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# 作为模块被 app_factory.py 导入

db = SQLAlchemy()
migrate = Migrate()
