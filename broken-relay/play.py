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
    update_config(config)

    print(response["message"])

def submit():
    URL = BASE + "/api/submit"

    results = {}

    # try:
        # get the testcase from the server
        # submit team_id

    # run tests locally
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
                results[testcase] = True if "✓" in output_list[0] else False

    except CalledProcessError:
        print("===== Tests failed ====")
    
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


def leaders():
    URL = BASE
    # get the leaderboard
    request = requests.get(URL)
    response = request.json()

    print(json.dumps(response))

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
        elif command == "leaders":
            leaders()
        else:
            print("Command not understood. Type 'help' for help and 'quit' to exit.")
        command= None
