"""
Defines the server.
"""
import colorama
import json
import queue
from colorama import Fore, Back, Style
from flask import Flask
from flask import request
from typing import Tuple

class Server(object):
    """
    A distributed classifier server.
    """

    app = Flask(__name__)
    jobs_queue = queue.Queue()
    active_jobs = set({})
    results = []

    def start_server(self):
        """
        Sets up and starts the server.
        """
        job1 = {"name": "First", "value": 1}
        job2 = {"name": "Second", "value": 3}
        self.jobs_queue.put(job1)
        self.jobs_queue.put(job2)
        self.app.run(threaded = True)

    def print_job(self, job: dict):
        print(Fore.YELLOW + str(job) + Style.RESET_ALL)

    def print_result(self, entry: Tuple[dict, float]):
        print(Fore.YELLOW + str(entry) + Style.RESET_ALL)

    def print_active_jobs(self):
        print("Active Jobs: " + Fore.RED + str(self.active_jobs) + Style.RESET_ALL)

    def add_job(self, job: dict):
        """
        Adds the given job to the queue.

        Parameters
        ----------
        job : dict
            The job to be added to the queue. If None then the job add will
            fail.

        Returns
        -------
        result : str
            A string indicating if the add succedded or not.
        """
        if job != None:
            self.jobs_queue.put(job)
            self.print_job(job)
            return "Job added"
        else:
            return "Invalid job format, be sure to use the application/json content type"

    def get_job(self):
        """
        Returns the next available job.

        Returns
        -------
        result : str
            A json string representing the next job.
        """
        job = self.jobs_queue.get()
        self.active_jobs.add(dict_key(job))
        self.print_job(job)
        self.print_active_jobs()
        return json.dumps(job)

    def post_result(self, job: dict, result: float):
        """
        Records the given result and removes the given job from the active jobs.

        If the given job is not active, then nothing is done and an error
        message is returned.

        Parameters
        ----------
        job : dict
          The job associated with the given result.

        result : float
          The result for the given job.
        """
        if job != None and result != None:
            try:
                self.active_jobs.remove(dict_key(job))
                entry = (job, result)
                self.results.append(entry)
                self.print_result(entry)
                self.print_active_jobs()
                return "Job result posted"
            except KeyError:
                return "The given job is not active"
        else:
            return "Invalid job or result"

def dict_key(d):
    return frozenset(d.items())

def run_server():
    """
    Creates and runs the server.
    """
    server = Server()

    @server.app.route("/addjob", methods=['POST'])
    def add_job():
        json_data = request.get_json()
        try:
            name = json_data["name"]
            value = json_data["value"]
            job = {"name": name, "value": value}
            return server.add_job(job)
        except KeyError:
            return "Invalid job add. Be sure to include the job name and value."

    @server.app.route("/getjob")
    def get_job():
        return server.get_job()

    @server.app.route("/postresult", methods=['POST'])
    def post_result():
        json_data = request.get_json()
        try:
            name = json_data["name"]
            value = json_data["value"]
            result = json_data["result"]

            job = {"name": name, "value": value}
            return server.post_result(job, result)
        except KeyError:
            return "Invalid result posting. Be sure to include the job name, value, and result."

    server.start_server()

if __name__ == "__main__":
    colorama.init()
    run_server()
