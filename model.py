from sqlalchemy.exc import SQLAlchemyError
from time import ctime
from app import db
from stripped_string import StrippedString
import logging
FORMAT = '%(message)s'
logging.basicConfig(format=FORMAT,level=logging.DEBUG)


# Create the Account Class
class Account(db.Model):
    user_id = db.Column(StrippedString, primary_key=True)
    otp = db.Column(StrippedString, nullable=False)
    access_token = db.Column(StrippedString, nullable=True)
    created_on = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    last_updated_on = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    def __init__(self, user_id, otp):
        self.user_id = user_id
        self.otp = otp
        self.created_on = ctime()
        self.last_updated_on = ctime()

    def __repr__(self):
        return '<Account %r>' % self.user_id

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


def addAccount(account):
    try:
        db.session.add(account)
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

def session_commit():
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        reason = str(e)
        logging.info(reason)
        raise e

db.create_all()

if __name__ == '__main__':
    manager.run()