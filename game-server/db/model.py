from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class Teams(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    score = Column(Integer)
    contract = Column(String)

    def __repr__(self):
        return "<User(id='{}', name='{}', score='{}')>".format(
            self.id, self.name, self.score)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}