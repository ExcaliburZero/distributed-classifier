from typing import Union
import json
import requests

def run_client(api_url: str):
    keep_going = True
    while keep_going:
        command = input("> ")

        if command == "quit":
            keep_going = False
        elif command == "job":
            get_job_command(api_url)

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
    run_client(api_url)
