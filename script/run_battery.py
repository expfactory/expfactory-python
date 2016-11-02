#!/opt/conda/bin/python
import http.server
import socketserver
import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('document_root', help='Web server document root')
parser.add_argument('--port', help='Web server port')
args = parser.parse_args()

try:
    os.chdir(args.document_root)
    port = int(args.port)
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), Handler)
    print("Preview experiment at localhost:%s" %port)
    #webbrowser.open("http://localhost:%s" %(port))
    httpd.serve_forever()
except:
    print("Stopping web server...")
    httpd.server_close()