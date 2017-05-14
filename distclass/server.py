"""
Defines the server.
"""
import curses
import json
import logging
import queue
import time
from flask import Flask
from flask import request
from typing import Tuple

import job_queue

class Server(object):
    """
    A distributed classifier server.
    """

    app = None
    jobs_queue = None
    active_jobs = None
    results = None
    stdscr = None
    updating = None

    def __init__(self, stdscr):
        self.app = Flask(__name__)
        self.jobs_queue = job_queue.JobQueue()
        self.active_jobs = set({})
        self.results = []
        self.stdscr = stdscr

    def start_server(self):
        """
        Sets up and starts the server.
        """
        job1 = {"name": "First", "value": 1}
        job2 = {"name": "Second", "value": 3}
        self.jobs_queue.append(job1)
        self.jobs_queue.append(job2)

        curses.noecho()
        self.updating = False
        self.update_screen()

        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        self.app.run(threaded = True)

    def update_screen(self):
        while self.updating:
            time.sleep(0.001)

        self.updating = True
        self.stdscr.clear()
        line = 0

        # Display job queue
        self.stdscr.addstr(line, 0, "Queued Jobs")
        line += 1
        self.stdscr.addstr(line, 0, "-----------")
        line += 1

        count = 1
        queue_copy = self.jobs_queue.copy()
        for job in queue_copy:
            output = " " + str(count) + ") " + job["name"] + " ~ " + str(job["value"])
            self.stdscr.addstr(line, 0, output)
            line += 1
            count += 1

        # Display active jobs
        line += 1
        self.stdscr.addstr(line, 0, "Active Jobs")
        line += 1
        self.stdscr.addstr(line, 0, "-----------")
        line += 1

        count = 1
        active = self.active_jobs.copy()
        for job in active:
            job = dict(job)
            output = " " + str(count) + ") " + job["name"] + " ~ " + str(job["value"])
            self.stdscr.addstr(line, 0, output)
            line += 1
            count += 1

        # Display completed jobs
        line += 1
        self.stdscr.addstr(line, 0, "Completed Jobs")
        line += 1
        self.stdscr.addstr(line, 0, "-----------")
        line += 1

        count = 1
        results = self.results.copy()
        for result in results:
            job = result[0]
            output = " " + str(count) + ") " + job["name"] + " ~ " + str(job["value"]) + " => " + str(result[1])
            self.stdscr.addstr(line, 0, output)
            line += 1
            count += 1

        self.stdscr.refresh()
        self.updating = False

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
            self.jobs_queue.append(job)
            self.update_screen()
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
        job = self.jobs_queue.popleft()
        self.active_jobs.add(dict_key(job))
        self.update_screen()
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
                self.update_screen()
                return "Job result posted"
            except KeyError:
                return "The given job is not active"
        else:
            return "Invalid job or result"

def dict_key(d):
    return frozenset(d.items())

def run_server(stdscr):
    """
    Creates and runs the server.
    """
    server = Server(stdscr)

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
    curses.wrapper(run_server)
