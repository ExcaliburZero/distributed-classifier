import colorama
import json
import requests
from colorama import Fore, Back, Style
from typing import Union

def run_client(api_url: str):
    keep_going = True
    while keep_going:
        command = prompt_command()

        if command == "quit":
            keep_going = False
        elif command == "job":
            get_job_command(api_url)
        elif command == "add":
            add_job_command(api_url)

def prompt_command() -> str:
    prompt = "> "
    print(Fore.YELLOW + prompt + Style.RESET_ALL, end='')

    command = input("")
    return command

def get_job_command(api_url: str):
    job = grab_job(api_url)

    if isinstance(job, str):
        print(job)
    else:
        print(job)
        result = prompt_result()

        response = send_result(api_url, job, result)
        if isinstance(response, str):
            print(response)

def add_job_command(api_url: str):
    name = input("name: ")

    value = None
    while value == None:
        try:
            value_string = input("value: ")
            value = int(value_string)
        except ValueError:
            print("Invalid value: " + value_string)

    job = {"name": name, "value": value}
    response = send_job(api_url, job)
    if isinstance(response, str):
        print(response)

def prompt_result() -> float:
    while True:
        result_string = input("Result: ")
        try:
            result = float(result_string)
            return result
        except ValueError:
            print("Invalid result: " + result_string)

def grab_job(api_url: str) -> Union[str, dict]:
    job_path = "/getjob"
    query_url = api_url + job_path

    try:
        resp = requests.get(url = query_url)

        job = json.loads(resp.text)
        return job
    except requests.exceptions.ConnectionError:
        return "Unable to connect to api url: " + query_url

def send_job(api_url: str, job: dict) -> Union[str, None]:
    add_path = "/addjob"
    post_url = api_url + add_path
    headers = {"content-type": "application/json"}

    job_string = json.dumps(job)

    try:
        requests.post(post_url, data = job_string, headers = headers)
        return None
    except requests.exceptions.ConnectionError:
        return "Unable to connect to api url: " + post_url

def send_result(api_url: str, job: dict, result: float) -> Union[str, None]:
    result_path = "/postresult"
    post_url = api_url + result_path
    headers = {"content-type": "application/json"}

    data = job.copy()
    data["result"] = result
    data_string = json.dumps(data)

    try:
        requests.post(post_url, data = data_string, headers = headers)
        return None
    except requests.exceptions.ConnectionError:
        return "Unable to connect to api url: " + post_url

if __name__ == "__main__":
    api_url = "http://localhost:5000"

    colorama.init()
    run_client(api_url)
