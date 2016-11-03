#!/usr/bin/env python
import argparse
import http.server
import os
import socketserver
import sys
import webbrowser

parser = argparse.ArgumentParser()
parser.add_argument('--folder', help='Folder with battery and experiments (document root)',default=None)
parser.add_argument('--port', help='Web server port', default=8080)

try:
    args = parser.parse_args()
except:
    parser.print_help()
    sys.exit(0)

# If folder not specified, assume user means PWD
folder = args.folder
if folder == None:
    print("No web root folder specified, serving present working directory...")
    folder = os.getcwd()

print("Serving experiment from from %s" %(folder))

try:
    os.chdir(folder)
    port = int(args.port)
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), Handler)
    print("Preview experiment at localhost:%s" %port)
    webbrowser.open("http://localhost:%s" %(port))
    httpd.serve_forever()
except:
    print("Stopping web server...")
    httpd.server_close()
