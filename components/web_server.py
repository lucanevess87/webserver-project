from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import os


class WebServer:
    def __init__(self, documents, errors):
        self.web_server = socket(AF_INET, SOCK_STREAM)
        self.address = 'localhost'
        self.web_server.bind((self.address, 4000))
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
    def handle_error(self):
        print("handle_error")

    # Create handle success function (200)
    def handle_success(self):
        print("handle_success")

    def handle_http_message(self, http_message):
        # ex: ['GET', '/favicon.ico', 'HTTP/1.1']
        http_request, file, http_version = http_message.split('\r\n')[
            0].split(' ')

        # If has index.html at our documents we can already assign value else it will be generate
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
        # Create a class interface to http_request_content!!

        return print(http_request, file, extension, http_version)

    def receive_message(self, socket_client):
        while True:
            http_message = socket_client.recv(2048).decode()
            if http_message:
                try:
                    http_content = self.handle_http_message(http_message)

                    if http_content.file == '/':
                        self.create_index(
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
