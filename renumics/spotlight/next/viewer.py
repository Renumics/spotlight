from threading import Thread

import multiprocessing
import multiprocessing.connection
from pandas import DataFrame

from renumics.spotlight.backend import create_datasource

from renumics.spotlight.backend.data_source import DataSource
from .gunicorn import StandaloneApplication

def _server_entrypoint(connection: multiprocessing.connection.Connection):
    application = StandaloneApplication("renumics.spotlight.next.app:SpotlightApp", connection, {"worker_class": "renumics.spotlight.next.uvicorn_worker.RestartableUvicornWorker", "reload": True, "bind": "localhost:8001"})
    application.run()


class Server():
    process: multiprocessing.Process
    connection: multiprocessing.connection.Connection

    def __init__(self):
        self.connection, server_connection = multiprocessing.Pipe()
        self.process = multiprocessing.Process(target=_server_entrypoint, args=(server_connection,))
        self._receiver_thread = Thread(target=self._receive)

    def start(self):
        self.process.start()

    def stop(self):
        self.process.kill()

    def transfer_datasource(self, datasource: DataSource):
        self.connection.send({"kind": "datasource", "data": datasource})

    def _receive(self):
        while True:
            self.connection.recv()

def show(df: DataFrame):
    # create datasource
    datasource = create_datasource(df)

    # setup server process
    server = Server()
    server.start()

    # transfer datasource
    server.transfer_datasource(datasource)

    return server
