from __future__ import print_function  # Only Python 2.x

import json
import subprocess
import sys
import os
from subprocess import CalledProcessError

import requests

BASE = "http://localhost:3000"

def read_config():
    try:
        with open("config.json", "r") as file:
            config = json.load(file)
    except FileNotFoundError:
        config = {}
    
    return config

def update_config(config):
    with open("config.json", "w+") as file:
        json.dump(config, file)

def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)

def init():
    with open("banner.txt", "r") as file:
        banner = file.read()
    print(banner)

def register():
    URL = BASE + "/api/team"
    name = None

    while not name:
        if sys.version_info[0] < 3:
            name = raw_input("Please enter your team name: ") 
        else:
            name = input("Please enter your team name: ")

    data = json.dumps({"name": name})

    request = requests.post(URL, headers={'Content-Type': 'application/json' }, data=data)
    response = request.json()

    config["name"] = response["name"]
    config["id"] = response["id"]
    update_config(config)

    print(response["message"])

def submit():
    URL = BASE + "/api/contract"

    try:
        # compile contracts 
        for output in execute(["truffle", "compile"]):
            print(output, end="")

        # load contract file
        contract_file = os.path.join("build", "contracts", "BrokenRelay.json")
        with open(contract_file, "r") as file:
            contract = json.load(file)

        # prepare submission with team id
        data = json.dumps({
            'id': config['id'],
            'contract': contract
            })

        # submit
        request = requests.post(URL, headers={'Content-Type': 'application/json' }, data=data)
        response = request.json()

        print(response["message"])

    except CalledProcessError:
        print("===== Compiling failed ====")
    except FileNotFoundError as e:
        print(e)

def leaders():
    # get the leaderboard
    pass

def score():
    URL = BASE + "/api/score?id={}".format(config["id"])
    # get your current score and rank
    request = requests.get(URL)
    response = request.json()

    print("Your score is {}".format(response["score"]))

def test():
    try:
        for output in execute(["truffle", "test"]):
            print(output, end="")
    except CalledProcessError:
        print("===== Tests failed ====")

def display_help():
    print("")

def stop():
    print("Thanks for playing!")
    sys.exit()


config = read_config()

if __name__ == "__main__":
    init()
    register()
    command = None
    while not command:
        command = input("What would you like to do next (test/submit/score/help/quit): ")

        if command == "help":
            display_help()
        elif command == "score":
            score()
        elif command == "quit":
            stop()
        elif command == "submit":
            submit()
        elif command == "test":
            test()
        else:
            print("Command not understood. Type 'help' for help and 'quit' to exit.")
        command= None
