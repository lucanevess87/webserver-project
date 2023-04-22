prefix = {'html': 'text', 'js': 'text',  'plain': 'text', 'css': 'text',
          'png': 'image', 'ex-icon': 'image', 'gif': 'image', 'jpeg': 'image',
          'ogg': 'audio'}


class HTTPRequestContent:
    def __init__(self, http_request, file, extension, http_version):
        self.http_request = http_request
        self.file = file
        self.http_version = http_version
        self.extension = None

        if extension:
            try:
                # example: prefix[jpeg] + / + jpeg ==> image/jpeg
                self.extension = prefix[extension] + '/' + extension
            except KeyError:
                self.extension = 'application' + '/' + extension
