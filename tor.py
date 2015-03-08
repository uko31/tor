#!/usr/bin/python

import argparse
import json
import os.path
import transmissionrpc

class transmission:
   def __init__(self, hostname, port):
      self.hostname = hostname
      self.port = port
      try:
          self.tc = transmissionrpc.Client(self.hostname, port=self.port)
      except transmissionrpc.TransmissionError as e:
          print("Transmission connection error [%s] => exiting..." % e.info)
          exit()
          

   def add(self, torrent):
      self.tc.add_torrent("file://%s" % os.path.realpath(torrent))
      os.remove(torrent)

   def addall(self, path):
      for torrent in os.walk(path):
          self.add(torrent)

   def remove(self, id):
      self.tc.rm_torrent(id)

   def clear(self):
      # add a loop through all available torrent and remove finished ones
      for torrent in self.tc.get_torrents():
          if torrent.status == "seeding":
              print("remove torrent: %d - %s" % (torrent.id, torrent.name))
              self.tc.remove_torrent(torrent.id)
      return(True)
   
   def purge(self):
      # add loop through all available tasks and remove them
      return(True)
   
   def view(self):
      # a a loop to dipslay each and every tasks.
      for torrent in self.tc.get_torrents():
         print("%d - %-11s - %3.0f%% - %s" % (torrent.id, torrent.status, torrent.progress, torrent.name))
      return(True)

class configuration:
   def __init__(self, filename):
      self.filename = filename
      default_cfg="""{
         "hostname": "nas",
         "input": "~/dl",
         "output": "~/mnt/nas/downloads",
         "port": "9091",
         "ext": "*.torrent",
         "sqlite": "~/mnt/nas/downloads/.database",
         "sqlite_update": "yes"
      }
      """

      if os.path.isfile(self.filename):
         f = open(self.filename, "r")
         self.var = json.load(f)
         f.close()
      else:
         self.var = json.loads(default_cfg)
         self.update()

   def update(self):
      if not os.path.isdir(os.path.dirname(self.filename)):
         os.makedirs(os.path.dirname(self.filename))
      f = open(self.filename, "w")
      json.dump(self.var, f, indent=3)
      f.close()

parser = argparse.ArgumentParser()

# global operations:
parser.add_argument("-d", "--download", action="store_true", help="download all file from the input directory")
parser.add_argument("-v", "--view",     action="store_true", help="display all download tasks")
parser.add_argument("-c", "--clear",    action="store_true", help="remove all finished tasks")
parser.add_argument("-p", "--purge",    action="store_true", help="purge all downloadtasks")

# single operations:
parser.add_argument("-a", "--add",    help="download file specified")
parser.add_argument("-r", "--remove", help="remove download task specified by id")

# update configuration:
parser.add_argument("--input",  help="update input configuration variable")
parser.add_argument("--output", help="update output configuration variable")
parser.add_argument("--port",   help="update port configuration variable", type=int)
parser.add_argument("--ext",    help="update ext configuration variable")

options = parser.parse_args()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Main Program
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

cfg = configuration(os.getenv("HOME") + "/.config/tor/tor.json")
#print("DEBUG: %s" % cfg.var)
tr = transmission(cfg.var["hostname"], cfg.var["port"] )
   
if ( options.input ):
   print("update input configuration variable: %s" % options.input)
   cfg.var["input"] = options.input
   cfg.update()
   #print("DEBUG: %s" % cfg.var)
if ( options.output ):
   print("update output configuration variable: %s" % options.output)
   cfg.var["output"] = options.output
   cfg.update()
   #print("DEBUG: %s" % cfg.var)
if ( options.port ):
   print("update port configuration variable: %s" % options.port)
   cfg.var["port"] = options.port
   cfg.update()
   #print("DEBUG: %s" % cfg.var)
if ( options.ext ):
   print("update port configuration variable: %s" % options.ext)
   cfg.var["ext"] = options.ext
   cfg.update()
   #print("DEBUG: %s" % cfg.var)

if ( options.add ):
   print("add download task %s" % options.add)
   tr.add(options.add)

if ( options.remove ):
   print("remove download task %s" % options.remove)
   tr.remove(options.remove)

if ( options.download ):
   print("download all")
   tr.addall(os.path.realpath(cfg.var["input"]))

if ( options.clear ):
   print("clear all finished downloads")
   tr.clear()

if ( options.purge ):
   print("purge all download tasks")
   tr.purge()
   
if ( options.view ):
   print("view current download tasks")
   tr.view()
