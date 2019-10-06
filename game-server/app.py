import json
import subprocess
from shutil import copy
from os import path
from subprocess import CalledProcessError

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application, HTTPError, RequestHandler

from db.model import Teams, metadata
from scores import scores
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# setup database
engine = create_engine('sqlite:///teams.db', echo=True)   
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

class Score(RequestHandler):
    def get(self):
        id = self.get_argument('id', None)
        team = db.query(Teams).filter_by(id=id).first()
        if not team: raise HTTPError(404)
        self.write({'id': team.id, 'score': team.score})


class SubmitContract(RequestHandler):
    def get(self):
        pass
    
    def post(self):
        # get the contract
        submission = json.loads(self.request.body)
        # check if team exists
        team = db.query(Teams).filter_by(id=submission['id']).first()

        response = {}

        if team and submission['results']:
            response['message'] = "Submitted results for team {}".format(team.name)
            update_score(team, submission['results'])
        elif team:
            response['message'] = "Please submit your results"
        else:
            response['message'] = "Team ID not found"

        self.write(response)

# parse results and update score of the team
def update_score(team, results):
    # TODO: check if already submitted same code
    team.submission += 1
    # loop through the results
    for case, result in results.items():
        # if result is true update score
        # else leave score as is
        if result:
            team.score += scores[case]
    db.commit()



# not used at the moment
def execute_test(test):
    try:
        output = subprocess.run(["truffle", "test"], stdout=subprocess.PIPE, check=True)
        result = output.stdout.rstrip()

        score = 0

        return score
    except CalledProcessError:
        raise HTTPError(500)

def make_app():
  urls = [
      ("/", Leaderboard),
      ("/api/register", RegisterTeam),
      ("/api/submit", SubmitContract),
      ("/api/score", Score)
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
