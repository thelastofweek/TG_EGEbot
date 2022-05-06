import datetime
import sqlalchemy
from . import db_session


class User(db_session.SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)
    chat_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    nickname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    fio = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    avg_mark = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    done_count = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)