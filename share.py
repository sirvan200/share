# upload_server.py
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class FileUploadHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        content_type = self.headers['Content-Type']
        if not content_type.startswith('multipart/form-data'):
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Unsupported Media Type")
            return

        boundary = content_type.split("boundary=")[1].encode()
        remainbytes = int(self.headers['Content-Length'])
        line = self.rfile.readline()
        remainbytes -= len(line)

        files_saved = []
        while remainbytes > 0:
            if boundary in line:
                line = self.rfile.readline()
                remainbytes -= len(line)
                if b'filename=' in line:
                    filename = line.decode().split('filename="')[1].split('"')[0]
                    filename = os.path.basename(filename)
                    filepath = os.path.join(UPLOAD_DIR, filename)

                    # skip Content-Type and empty line
                    self.rfile.readline()
                    self.rfile.readline()
                    remainbytes -= 2 * len(line)

                    with open(filepath, 'wb') as f:
                        preline = self.rfile.readline()
                        remainbytes -= len(preline)
                        while remainbytes > 0:
                            line = self.rfile.readline()
                            remainbytes -= len(line)
                            if boundary in line:
                                preline = preline.rstrip(b'\r\n')
                                f.write(preline)
                                break
                            else:
                                f.write(preline)
                                preline = line

                    files_saved.append(filename)
                else:
                    break
            else:
                break

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Files uploaded: " + ", ".join(files_saved).encode())

    def do_GET(self):
        if self.path == "/":
            with open("upload.html", "rb") as f:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(f.read())
        else:
            super().do_GET()

httpd = HTTPServer(('0.0.0.0', 8000), FileUploadHandler)
print("Server started at http://0.0.0.0:8000")
httpd.serve_forever()
