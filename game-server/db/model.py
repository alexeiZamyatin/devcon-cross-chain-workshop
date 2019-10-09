from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class Teams(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    score = Column(Integer, default=0)
    submissions = Column(Integer, default=0)
    test1 = Column(Integer, default=0)
    test2 = Column(Integer, default=0)
    test3a = Column(Integer, default=0)
    test3b = Column(Integer, default=0)
    test4 = Column(Integer, default=0)
    test5 = Column(Integer, default=0)
    test6 = Column(Integer, default=0)
    test7 = Column(Integer, default=0)
    test8 = Column(Integer, default=0)
    test9 = Column(Integer, default=0)
    test10 = Column(Integer, default=0)            
    hint1 = Column(Boolean, default=False)
    hint2 = Column(Boolean, default=False)
    hint3a = Column(Boolean, default=False)
    hint3b = Column(Boolean, default=False)
    hint4 = Column(Boolean, default=False)
    hint5 = Column(Boolean, default=False)
    hint6 = Column(Boolean, default=False)
    hint7 = Column(Boolean, default=False)
    hint8 = Column(Boolean, default=False)
    hint9 = Column(Boolean, default=False)
    hint10 = Column(Boolean, default=False)            

    def __repr__(self):
        return "<User(id='{}', name='{}', score='{}')>".format(
            self.id, self.name, self.score)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}