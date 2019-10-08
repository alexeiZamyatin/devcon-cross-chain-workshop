from __future__ import print_function  # Only Python 2.x

import json
import subprocess
import sys
import os
from subprocess import CalledProcessError

import requests

BASE = "http://localhost:3000"
TESTS = {
    "1": False,
    "2": False, 
    "3a": False, 
    "3b": False,
    "4": False,
    "5": False,
    "6": False,
    "7": False,
    "8": False, 
    "9": False
}

def print_file(name):
    with open(os.path.join("docs", name), "r") as file:
        text = file.read()
    print(text)

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
    print_file("banner.txt")
    print_file("intro.txt")

def register():
    URL = BASE + "/api/register"
    name = None

    while not name:
        if sys.version_info[0] < 3:
            name = raw_input("Please enter your team name: ") 
        else:
            name = input("Please enter your team name: ")

    data = json.dumps({"name": name})

    try:
        request = requests.post(URL, headers={'Content-Type': 'application/json' }, data=data)
        response = request.json()
    
    except:
        print("Something went wrong with the server")

    config["name"] = response["name"]
    config["id"] = response["id"]
    config["tests"] = TESTS
    update_config(config)

    print(response["message"])

def hint():
    # return which cases are not yet solved
    print("")
    print("You are under attack! Problems {} are not yet solved!".format([key if value else None for key, value in config["tests"].items()]))

    # as which case is solved now
    next_test = input("Please enter the number of the attack you want to have a hint for: ")

    if not next_test in config["tests"]:
        print("Please enter a valid number!")
        return

    # Print which test case is submitted
    # print("You are submitting the solution for case {}".format(next_test))
    
    # get the testcase from the server
    try:
        # submit team_id
        url = URL + "?id={}&case={}".format(config["id"], next_test)

        request = requests.get(url)
        response = request.json()

        with open(os.path.join("test", response["name"]), "w+") as test_file:
            test_file.write(response["content"])
    except:
        print("Problem with getting the test case from the server")
        return
 

def submit():
    URL = BASE + "/api/submit"

    print("Upgrading defenses...")
    # run tests locally
    results = {}
    try:
        # perform tests locally
        # parses the output line by line
        for output in execute(["truffle", "test"]):
            # check if it includes the testcases
            if "TESTCASE" in output:
                # split the output string into a list
                # list[0] is the result of the test (pass/fail)
                # list[1] is test case number plus any additional information
                output_list = output.split(" TESTCASE ", 1)
                # list[1] looks like "1: set ....". Split at : and return the first elemet
                testcase = output_list[1].split(":",1)[0]
                # store the result of the testcase
                if "✓" in output_list[0]:
                    results[testcase] = True
                    config["tests"][testcase] = True
                    update_config(config)
                    print("You successfully completed testcase {}.".format(testcase))
                else:
                    results[testcase] = False
                    print("Sorry, testcase {} failed. TIP: you can request a hint and see the testcase in the 'test' folder.".format(testcase))

    except CalledProcessError:
        print("===== Oh no, you are still vulnerable! ====")
    
    # report results to server
    # prepare submission with team id
    data = json.dumps({
        'id': config['id'],
        'results': results
    })

    # submit
    try:
        request = requests.post(URL, headers={'Content-Type': 'application/json' }, data=data)
        response = request.json()

        print(response["message"])
    except:
        print("Something went wrong with the server")

    score()


def leaders():
    URL = BASE + "/api/leaderboard"
    # get the leaderboard
    request = requests.get(URL)
    # returns a sorted list of teams
    response = request.json()

    leaderboard = []

    print(response)

    for team in response['teams']:
        leaderboard.append((team["name"], team["score"]))

    for i in range(len(leaderboard)):
        name = leaderboard[i][0]
        score = leaderboard[i][1]
        # TODO: make this output format nice
        print("{}: {}    {}".format(i+1, name, score))

    # print(json.dumps(response))

def score():
    URL = BASE + "/api/score?id={}".format(config["id"])
    # get your current score and rank
    request = requests.get(URL)
    response = request.json()

    print("Your score is {}.".format(response["score"]))

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
        command = input("What would you like to do next?\n(hint/test/submit/score/leaders/help/quit): ")

        if command == "help":
            display_help()
        elif command == "hint":
            hint()
        elif command == "score":
            score()
        elif command == "quit":
            stop()
        elif command == "submit":
            submit()
        elif command == "test":
            test()
        elif command == "leaders":
            leaders()
        else:
            print("Command not understood. Type 'help' for help and 'quit' to exit.")
        command= None
