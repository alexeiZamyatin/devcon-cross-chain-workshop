import json
import requests
import sys

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

    config = read_config()
    config["name"] = response["name"]
    config["id"] = response["id"]
    update_config(config)

    print(response["message"])

def submit():
    pass

def display_help():
    print("")

def stop():
    print("Thanks for playing!")
    sys.exit()

if __name__ == "__main__":
    init()
    register()
    command = None
    while not command:
        command = input("What would you like to do next (help/submit/quit): ")

        if command == "help":
            display_help()
            command = None
        elif command == "quit":
            stop()
        elif command == "submit":
            submit()
            command = None
        else:
            print("Command not understood. Type 'help' for help and 'quit' to exit.")