#  coding: utf-8 
import socketserver, os
from datetime import datetime, timezone

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Joe Ha
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/



class MyWebServer(socketserver.BaseRequestHandler):
    
    '''
        handle method services connections to the webserver.
        Parameters: none required.
        Return: none.
    '''
    def handle(self):
        # Decode data from buffer.
        self.data = self.request.recv(1024).strip().decode('utf-8')
        self.split_data = self.data.split()
        # Get http method
        self.method = self.split_data[0]
        # Get the path
        self.path = self.split_data[1]
        # print(self.split_data[1][1:]) #index.html
        # print(self.path) #/index.html
        # Get http version
        self.http_version = self.split_data[2]
        self.file_type = ''
        # Check for Method
        # Server only supports GET
        # POST, PUT, DELETE are not handled
        if (self.method == "GET"):
            full_local_path = self.http_get_request()
            # Webserver supports mime-types for HTML and CSS
            if ('html' in full_local_path or 'css' in full_local_path):
                response = self.http_get_200_request(full_local_path)
                self.request.sendall(bytearray(response,'utf-8'))
            else:
                # Local path is invalid return 404 Not Found.
                response = self.http_get_404_request()
                self.request.sendall(bytearray(response,'utf-8'))
        else:
            # For POST, PUT, DELETE and other methods not implemented.
            # Send a 405 Method Not Allowed
            response = self.http_get_405_request()
            self.request.sendall(bytearray(response,'utf-8'))
    
    '''
        current_date_time method returns the current date and time for a http response
        Parameter: none required.
        Return: str of current date in time for http header.
        
        Referenced: 
        https://stackoverflow.com/questions/9847213/how-do-i-get-the-day-of-week-given-a-date
        https://www.programiz.com/python-programming/datetime/strftime
    '''
    def current_date_time(self):
        current_moment_str = ''
        current_moment = datetime.now()
        current_moment_str += current_moment.strftime("Date: %a, %b %Y %-H:%M:%S")
        current_moment_str += ' GMT\r\n'
        return current_moment_str

    '''
        http_get_request method returns the necessary path to serve files
        for http requests.
        Parameter: none required
        Return: str of path

        Referenced:
        MDN mime-types - https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types
        os module - https://docs.python.org/3.5/library/os.html?highlight=os#module-os
        os.path - https://www.geeksforgeeks.org/os-path-module-python/
    '''
    def http_get_request(self):
        full_path =''
        # webserver can serve ONLY files ./www and deeper
        if 'www' not in self.path:
            full_path = 'www'+self.path
        complete_path = os.path.curdir + '/' + full_path
        if (self.path == '' or self.path == '/'):
            # root cases
            complete_path += 'index.html'
            self.file_type = 'html'
        elif (os.path.isfile(complete_path)):
            # path exists in ./www
            self.file_type = complete_path.split('.')[-1]
        elif (os.path.isdir(complete_path)):
            # handle re direction
            if (self.path[-1] == '/'):
                complete_path += 'index.html'
                self.file_type = complete_path.split('.')[-1]
            else:
                self.path += '/'
                self.file_type = complete_path.split('.')[-1]
                complete_path += '/index.html'
                response = self.http_get_301_request(complete_path)
                self.request.sendall(bytearray(response,'utf-8'))
                return "raise 301 status"
        else:
            # file cannot be found in path
            response = self.http_get_404_request()
            self.request.sendall(bytearray(response,'utf-8'))
            return "raise 404 exception"
        return complete_path
    
    '''
        http_get_200_request method returns the header & content for a 200
        OK status code.
        Parameter: path to file (str)
        Return: str of response (header + body)

        Referenced:
        Python file reading - https://www.w3schools.com/python/ref_file_read.asp
        String Formatting - https://realpython.com/python-string-formatting/
        http format - https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/200
    '''
    def http_get_200_request(self,path_to_file):
        get_header = '{} 200 OK\r\n'.format(self.http_version)
        get_header += self.current_date_time()
        get_header += 'Content-Type: text/{}; charset=utf-8\r\n'.format(self.file_type)
        get_header += 'Connection: Closed\r\n'
        f = open(os.path.curdir+'/'+path_to_file, 'r')
        body = f.read()
        f.close()
        # print(get_header+'\r\n'+body)
        return (get_header+'\r\n'+body)

    '''
        http_get_404_request method returns the header & content for a 404
        Not Found status code.
        Parameter: path to file (str)
        Return: str of response (header + body)

        Referenced:
        http format - https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404
    '''
    def http_get_404_request(self):
        get_header = '{} 404 Not Found\r\n'.format(self.http_version)
        get_header += self.current_date_time()
        get_header += 'Content-Type: text/html; charset=utf-8\r\n'
        get_header += 'Connection: Closed\r\n'
        body = '''<!DOCTYPE html>
        <html>
            <head>
                <title>404 Not Found</title>
            </head>
            <body>
                <h1>{} was not found.</h1>
            </body>
        </html>
        '''.format(self.path)
        # print(get_header+'\r\n'+body)
        return (get_header+'\r\n'+body)
    
    '''
        http_get_405_request method returns the header & content for a 405
        Method Not Allowed status code.
        Parameter: path to file (str)
        Return: str of response (header + body)

        Referenced:
        http format - https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/405
    '''
    def http_get_405_request(self):
        get_header = '{} 405 Method Not Allowed\r\n'.format(self.http_version)
        get_header += self.current_date_time()
        get_header += 'Content-Type: text/html; charset=utf-8\r\n'
        get_header += 'Connection: Closed\r\n'
        body = '''<!DOCTYPE html>
        <html>
            <head>
                <title>405 Method Not Allowed</title>
            </head>
            <body>
                <h1>Method Not Allowed</h1>
            </body>
        </html>
        '''
        # print(get_header+'\r\n'+body)
        return (get_header+'\r\n'+body)
    
    '''
        http_get_301_request method returns the header & content for a 301
        Moved Permanently status code.
        Parameter: path to file (str)
        Return: str of response (header + body)

        Referenced:
        http format - https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/301
    '''
    def http_get_301_request(self,path_file):
        get_header = '{} 301 Moved Permanently\r\n'.format(self.http_version)
        get_header += self.current_date_time()
        get_header += 'Content-Type: text/{}; charset=utf-8\r\n'.format(self.file_type)
        get_header += 'Connection: Closed\r\n'
        f = open(os.path.curdir+'/'+path_file, 'r')
        body = f.read()
        f.close()
        # print(get_header+'\r\n'+body)
        return (get_header+'\r\n'+body)
    
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
