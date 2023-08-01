

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
                    # TODO read the request and extract the URI

                    # Extract the URI from the HTTP request
                    uri = self.extract_uri(request)
                    
                    # Handle the request based on the URI
                    if self.directory_browsing and uri == "/www":
                        response = self.list_files()
                    else:
                        code, c_type, c_length, data = self.get_data(uri)
                        # print(type(data))
                        # print(code)
                        # print(c_type)
                        if c_type=='text/html':
                            data=data.decode('utf-8')
                        else:
                            data=data.decode('latin-1')
                            
                        response = self.response_headers(code, c_type, c_length)+data
                        # if isinstance(data, str):
                        #     data = data.encode('utf-8')
                        # response = response_headers + data
                    
                    conn.sendall(response.encode('utf-8'))



                    # # TODO update the parameter with the request URI
                    # uri = ""
                    # code, c_type, c_length, data = self.get_data(uri)
                    # response = self.response_headers(code, c_type, c_length) + data
                    # conn.sendall(bytes(response, 'utf8'))
                    # conn.close()

    def extract_uri(self, request):
        # Parse the HTTP request to extract the URI
        lines = request.split('\r\n')
        # print(lines)
        request_line = lines[0]
        # print(request_line)
        uri = request_line.split()[1]
        # print(uri)
        return uri

    def list_files(self):
        # List all files and directories in the 'www' directory
        files_list = os.listdir('www')
        html_list = '<h1>Directory Listing</h1><ul>'
        for filename in files_list:
            file_path = os.path.join('www', filename)
            html_list += f'<li><a href="/www/{filename}">{filename}</a></li>'
        html_list += '</ul>'
        return self.response_headers(200, 'text/html', len(html_list)) + html_list
    
    def get_data(self, uri):
        # Check if the requested file exists
        file_path = os.path.join('www', uri.lstrip('/www/'))
        if not os.path.exists(file_path):
            return 404, 'text/html', 0, '<h1>404 File Not Found</h1>'

        # Determine the content type using the mimetype module
        content_type, encoding = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = 'application/octet-stream'
        
        # Read the file data
        with open(file_path, 'rb') as f:
            data = f.read()
            content_length = len(data)
        
        # print('content-type',content_type)
        # print('content-length',content_length)
        # if content_type.startswith('text/') or content_type == 'application/json':
        #     data = data.decode('utf-8')  # Decode as UTF-8 for text-based content
        #     # return self.response_headers(200,content_type,content_length)+data.decode('utf-8')
        # else:
        #     data = data.decode('latin-1')  # Decode as Latin-1 for binary content

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
        return headers

def main():
    # test harness checks for your web server on the localhost and on port 8888
    # do not change the host and port
    # you can change  the HTTPServer object if you are not following OOP
    HTTPServer('127.0.0.1', 8888)

if __name__ == "__main__":
    main()                   