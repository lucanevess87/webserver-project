from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import os
from email.utils import formatdate
from components.http_request_content import *


class WebServer:
    def __init__(self, documents, errors):
        self.web_server = socket(AF_INET, SOCK_STREAM)
        self.address = 'localhost'
        self.web_server.bind((self.address, 1111))
        self.web_server.listen()
        self.inspected_folder = documents
        self.errors_folder = errors

        # Try tro create a folder with inspected_folder path, if already exists pass
        try:
            os.mkdir(self.inspected_folder)
        except FileExistsError:
            pass

        # List files of folder => array of files
        self.documents_list = os.listdir(self.inspected_folder)

    # Create handle error function (505,404,400)
    def handle_error(self, socket_client, error_type):
        first_line = f'HTTP/1.1 {error_type} '
        # Based on error type render
        if error_type == '400':
            first_line += 'Bad Request\r\n'
        elif error_type == '403':
            first_line += 'Forbidden Request'
        elif error_type == '404':
            first_line += 'Not Found\r\n'
        elif error_type == '505':
            first_line += 'HTTP Version Not Supported\r\n'

        # The proper error file is inside errors folder
        file = f'{self.errors_folder}/error{error_type}.html'

        # Designing response
        response = ''
        response += first_line
        response += f'Date: {formatdate(localtime=False, usegmt=True)}\r\n'
        response += f'Server: {self.address} (Windows)\r\n'
        response += f'Content-Length: {os.path.getsize(file)}'
        response += 'Content-Type: text/html\r\n'
        response += '\r\n'

        opened_file = open(file, 'r')
        content = opened_file.read()

        # Response created above + file html from errors folder
        response += content
        socket_client.send(response.encode())

    # Create handle success function (200)
    def handle_success(self, specifications: HTTPRequestContent, socket_client):
        # find target file
        file = self.inspected_folder + specifications.file
        if specifications.extension is not None:
            # Designing response
            response = ''
            response += 'HTTP/1.1 200 OK\r\n'
            response += f'Date: {formatdate(localtime=False, usegmt=True)}\r\n'
            response += f'Server: {self.address} (Windows)\r\n'
            response += f'Content-Length: {os.path.getsize(file)}\r\n'
            response += f'Content-Type: {specifications.extension}\r\n'
            response += '\r\n'
            socket_client.send(response.encode())
            print(response)
        try:
            # open file from inspected_folder
            opened_file = open(file, 'rb')
            while True:
                binary = opened_file.read(1024)
                if len(binary) == 0:
                    break
                # send binary version of file
                socket_client.send(binary)
        except PermissionError:
            path = file
            if self.inspected_folder in path:
                path = path.split(self.inspected_folder + '/')[1]
                path += '/'
            if ' ' in path:
                path = path.split(' ')
                path = '%20'.join(path)
            self.create_interface(socket_client, os.listdir(f'{file}'), path)

    # Create interface - When user open browser server will generate this html content, that allows user to pick some file friendlily
    def create_interface(self, socket_client, documents_list, file):
        # Designing response
        response = ''
        response += 'HTTP/1.1 200 OK\r\n'
        response += f'Date: {formatdate(localtime=False, usegmt=True)}\r\n'
        response += f'Server: {self.address} (Windows)\r\n'
        response += 'Content-Type: text/html\r\n'
        response += '\r\n'
        socket_client.send(response.encode())

        # Designing interface
        create_index_interface = '<!DOCTYPE html>\r\n'
        create_index_interface += '<html>\r\n'
        create_index_interface += '<head>\r\n'
        create_index_interface += '<title> Files - WebFiles </title>\r\n'
        create_index_interface += '</head>\r\n'
        create_index_interface += '\r\n'
        create_index_interface += '<body>\r\n'
        create_index_interface += '<h1>Available files <h1>\r\n'
        if documents_list:
            create_index_interface += '<ul>\r\n'
            for document in documents_list:
                if document.split(".")[0] != 'favicon':
                    create_index_interface += f' <li><a href="http://localhost:1111/{file}{document}"' \
                        f'>{document.split(".")[0]}</a></li>\r\n'
            create_index_interface += '<ul>\r\n'
        create_index_interface += '</body>\r\n'
        create_index_interface += '</html>\r\n'

        # send html interface to be generate on client side (server side rendering)
        socket_client.send(create_index_interface.encode())

    def handle_http_message(self, http_message):
        # ex: ['GET', '/favicon.ico', 'HTTP/1.1']
        http_request, file, http_version = http_message.split('\r\n')[
            0].split(' ')

        # If has index.html at our documents we can already assign value, else it will be generated
        if file == '/' and 'index.html' in self.documents_list:
            file = 'index.html'

        # For files like: '/Tame%20Impala%20-%20Borderline%20(Official%20Audio)%20(256%20kbps).mp3'
        if '%20' in file:
            file = file.split('%20')
            file = ' '.join(file)

        # Get file extension example: '/favicon.ico' => "ico"
        extension = file.split('.')[-1]

        # Finding correct extension
        if extension[0] == '/':
            extension = None
        if extension == 'jpg':
            extension = 'jpeg'
        elif extension == 'ico':
            extension = 'ex-icon'
        elif extension == 'htm':
            extension = 'html'
        elif extension == 'txt':
            extension = 'plain'

        # [http_request (GET, POST, PUT, etc), file, extension (jpeg, mp3, txt), http/1.1]
        return HTTPRequestContent(http_request, file, extension, http_version)

    def receive_message(self, socket_client):
        while True:
            http_message = socket_client.recv(2048).decode()
            if http_message:
                try:
                    http_content = self.handle_http_message(http_message)

                    if http_content.file == '/':
                        self.create_interface(
                            socket_client, self.documents_list, '')

                    # http version error
                    elif http_content.http_version.split('/')[1] != '1.1':
                        self.handle_error(socket_client, 505)
                        print('error 505\n')

                    # file not found error
                    elif http_content.file[1:].split('/')[0] not in self.documents_list:
                        self.handle_error(socket_client, 404)
                        print('error 404\n')

                    else:
                        self.handle_success(http_content, socket_client)
                        print('200 ok\n')
                except:
                    # server lost error
                    print('error 400\n')
                    self.handle_error(socket_client, 400)

    def start_server(self):
        while True:
            (socket_client, address_client) = self.web_server.accept()

            Thread(target=self.receive_message,
                   # Must have ","
                   args=(socket_client,)).start()
