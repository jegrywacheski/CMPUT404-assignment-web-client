#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse, urlencode

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return self.socket

    def get_code(self, data):
        try:
            # code will appear right after "HTTP/1.1"
            code = data.split()[1]
            return int(code)
        except:
            return None

    def get_headers(self,data):
        headers = ""
        try:
            chunks = data.split("\r\n\r\n", 1)
            headers = chunks[0]
            return headers
        except:
            return None

    def get_body(self, data):
        body = ""
        try:
            chunks = data.split("\r\n\r\n", 1)
            body = chunks[1]
            return body
        except:
            return None

    def get_host(self, parsed_url):
        host = ""
        # find host
        if ':' in parsed_url.netloc:
            host = parsed_url.netloc.split(':')[0]
        else:
            host = parsed_url.netloc

        return host

    def get_port(self, parsed_url):
        port = None
        # find port
        if parsed_url.port:
            port = parsed_url.port
        else:
            port = 80

        return port

    def get_path(self, parsed_url):
        path = ""
        if parsed_url.path == "":
            path = "/"
        else:
            path = parsed_url.path

        return path
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        
        parsed = urlparse(url)
        path = self.get_path(parsed)
        host = self.get_host(parsed)
        port = self.get_port(parsed)
        query = parsed.query

        if query:
            path += "?"
            path += query

        # send GET request
        request = "GET {} HTTP/1.1\r\n".format(path)
        request += "Host: {}\r\n".format(host)
        request += "Accept: */*\r\n"
        request += "Connection: close\r\n\r\n"

        # connect
        sock = self.connect(host, port)
        # send POST request
        self.sendall(request)
        # recieve response
        data = self.recvall(sock)
        # print data
        print(data)
        # close connection
        self.close()

        # headers = self.get_headers(data)
        code = self.get_code(data)
        body = self.get_body(data)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):

        parsed = urlparse(url)
        path = self.get_path(parsed)
        host = self.get_host(parsed)
        port = self.get_port(parsed)
        query = parsed.query

        if query:
            path += "?"
            path += query

        # create POST request
        request = "POST {} HTTP/1.1\r\n".format(path)
        request += "Host: {}\r\n".format(host)
        request += "Content-Type: application/x-www-form-urlencoded\r\n"


        if args:
            # convert to string of key=value pairs separated by & 
            encoded = urlencode(args)
            c_length = len(encoded)
            request += "Content-Length: {}\r\n\r\n".format(c_length)
            request += encoded
        else:
            request += "Content-Length: 0\r\n"
            request += "Connection: close\r\n\r\n"

        # connect
        sock = self.connect(host, port)
        # send POST request
        self.sendall(request)
        # recieve response
        data = self.recvall(sock)
        # print data
        print(data)
        # close connection
        self.close()

        # headers = self.get_headers(data)
        code = self.get_code(data)
        body = self.get_body(data)
        
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
