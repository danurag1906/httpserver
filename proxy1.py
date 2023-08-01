import socket
import mimetypes
import os

class HTTPServer:
    def __init__(self, IP, port):
        super().__init__()
        self.directory_browsing = True

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP) as self.s:
            self.s.bind((IP, port))
            self.s.listen()

            while True:
                conn, addr = self.s.accept()
                with conn:
                    print('Connected by', addr)
                    request = conn.recv(1024).decode('utf-8')
                    if not request:
                        continue

                    uri = self.extract_uri(request)

                    if self.directory_browsing and uri == "/www":
                        response = self.list_files()
                    else:
                        code, c_type, c_length, data = self.get_data(uri)

                        # Handle binary data without decoding
                        response = self.response_headers(code, c_type, c_length) + data

                    conn.sendall(response)

    def extract_uri(self, request):
        lines = request.split('\r\n')
        request_line = lines[0]
        uri = request_line.split()[1]
        return uri

    def list_files(self):
        files_list = os.listdir('www')
        html_list = '<h1>Directory Listing</h1><ul>'
        for filename in files_list:
            file_path = os.path.join('www', filename)
            html_list += f'<li><a href="/www/{filename}">{filename}</a></li>'
        html_list += '</ul>'
        return self.response_headers(200, 'text/html', len(html_list)) + html_list.encode('utf-8')

    def get_data(self, uri):
        file_path = os.path.join('www', uri.lstrip('/www/'))
        if not os.path.exists(file_path):
            return 404, 'text/html', 0, '<h1>404 File Not Found</h1>'.encode('utf-8')

        content_type, encoding = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = 'application/octet-stream'

        with open(file_path, 'rb') as f:
            data = f.read()
            content_length = len(data)

        return 200, content_type, content_length, data

    def response_headers(self, status_code, content_type, length):
        line = "\r\n"
        response_code = {
            200: "200 OK",
            404: "404 Not Found"
        }

        headers = ""
        headers += "HTTP/1.1 " + response_code[status_code] + line
        headers += "Content-Type: " + content_type + line
        headers += "Content-Length: " + str(length) + line
        headers += "Connection: close" + line
        headers += line
        return headers.encode('utf-8')

def main():
    HTTPServer('127.0.0.1', 8888)

if __name__ == "__main__":
    main()
