from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.model import metadata, Teams
import json


# setup database
engine = create_engine('sqlite:///:memory:', echo=True)   
Session = sessionmaker(bind=engine)
metadata.create_all(engine, checkfirst=True)
db = Session()

class Leaderboard(RequestHandler):
    def get(self):
        teams = db.query(Teams).order_by(Teams.score).all()
        message = [team.as_dict() for team in teams]
        self.write(json.dumps(message))

class RegisterTeam(RequestHandler):
    def post(self):
        # get a team name
        submission = json.loads(self.request.body)
        # check if team name is already in use
        team = db.query(Teams).filter_by(name=submission['name']).first()
        
        response = {}

        if team:
            # return existing team id 
            response['message'] = 'Team exists with ID {}'.format(team.id) 
        else:
            # return new team id
            team = Teams(name=submission['name'])
            db.add(team)
            db.commit()
            response['message'] = 'Successfully added team {} with ID {}'.format(team.name, team.id) 

        response['id'] = team.id
        response['name'] = team.name

        self.write(response)

class SubmitContract(RequestHandler):
    def post(self):
        # get the contract address
        submission = json.loads(self.request.body)
        # check if team exists
        team = db.query(Teams).filter_by(id=submission['id']).first()

        response = {}

        if team:
            team.contract = submission["contract"]
            db.commit()

            response['message'] = "Stored contract {} for team {}".format(team.contract, team.name)
        else:
            response['message'] = "Team ID not found"

        self.write(response)


def make_app():
  urls = [
      ("/", Leaderboard),
      ("/api/team", RegisterTeam),
      ("/api/contract", SubmitContract)
      ]
  return Application(urls, debug=True)


def main():
    # setup Tornado
    app = make_app()
    app.listen(3000)
    # server = HTTPServer(app)
    # server.bind(3000)
    # server.start(0)
    IOLoop.current().start() 
  
if __name__ == '__main__':
    main()
