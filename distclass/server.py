"""
Defines the server.
"""
import json
import queue
from flask import Flask
from flask import request

class Server(object):
    """
    A distributed classifier server.
    """

    app = Flask(__name__)
    jobs_queue = queue.Queue()

    def start_server(self):
        """
        Sets up and starts the server.
        """
        job1 = {"name": "First", "value": 1}
        job2 = {"name": "Second", "value": 3}
        self.jobs_queue.put(job1)
        self.jobs_queue.put(job2)
        self.app.run()

    def add_job(self, json_data):
        """
        Adds the given job to the queue.

        Parameters
        ----------
        json_data : dict
            The job to be added to the queue. If None then the job add will
            fail.

        Returns
        -------
        result : str
            A string indicating if the add succedded or not.
        """
        if json_data != None:
            name = json_data["name"]
            value = json_data["value"]
            job = {"name": name, "value": value}
            self.jobs_queue.put(job)
            print(str(job))
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
        print(str(job))
        return json.dumps(job)

def run_server():
    """
    Creates and runs the server.
    """
    server = Server()

    @server.app.route("/addjob", methods=['POST'])
    def add_job():
        json_data = request.get_json()
        return server.add_job(json_data)

    @server.app.route("/getjob")
    def get_job():
        return server.get_job()

    server.start_server()

if __name__ == "__main__":
    run_server()
