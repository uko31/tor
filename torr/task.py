#!/usr/bin/python

import sys
import os
import os.path

if sys.platform != "win32":
    import transmissionrpc

__VERSION__ = "0.2.0"

class Task:
    def __init__(self, id, name, status = None, progress = 0):
        self._id       = id
        self._status   = status
        self._progress = float(progress)
        self._name     = name

    def __str__(self):
        return("%-3s - %-11s - [%3.00f%%] %s" % (self._id, self._status, self._progress, self._name))

class TransmissionServer:
    version = "0.2.0"
    
    def __init__(self, hostname, port):
        self._hostname = hostname
        self._port     = port
        try:
            self._conn = transmissionrpc.Client(self._hostname, port=self._port)
        except transmissionrpc.TransmissionError as e:
            print("ERROR: Transmission connection failure [%s] => exiting..." % e.info)
            exit()

    def Add(self, filename):
        try:
            tor  = self._conn.add_torrent("file://%s" % os.path.realpath(filename))
            task = Task( id   = tor.id, 
                         name = tor.name )
        except transmissionrpc.TransmissionError as e:
            print("ERROR: Download %s not added (reason: %s)" % (os.path.basename(filename), e.message))
            return(False)
            
        os.remove(filename)
        return(task)

    def Remove(self, id):
        tor = self._conn.get_torrent(id)
        task = Task( id       = tor.id, 
                     status   = tor.status, 
                     progress = tor.progress, 
                     name     = tor.name )
        self._conn.remove_torrent(id)
        return(task)

    def Purge(self, id):
        tor = self._conn.get_torrent(id)
        task = Task( id       = tor.id, 
                     status   = tor.status, 
                     progress = tor.progress, 
                     name     = tor.name )
        self._conn.remove_torrent(id, delete_data=True)
        return(task)
    
    def List(self):
        tasks = list()
        
        torrents = self._conn.get_torrents()
        if len(torrents) != 0:
            for torrent in torrents:
                tasks.append(Task( id       = torrent.id, 
                                   status   = torrent.status, 
                                   progress = torrent.progress, 
                                   name     = torrent.name))

        return(tasks)

    def Version(self):
        return("version: %s" % TransmissionServer.version)
        