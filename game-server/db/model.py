from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class Teams(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    score = Column(Integer, default=0)
    case1 = Column(Integer, default=0)
    case2 = Column(Integer, default=0)
    case3 = Column(Integer, default=0)
    case4a = Column(Integer, default=0)
    case4b = Column(Integer, default=0)
    case6 = Column(Integer, default=0)
    case7 = Column(Integer, default=0)
    case8 = Column(Integer, default=0)
    case9 = Column(Integer, default=0)
    case10 = Column(Integer, default=0)

    def __repr__(self):
        return "<User(id='{}', name='{}', score='{}')>".format(
            self.id, self.name, self.score)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}