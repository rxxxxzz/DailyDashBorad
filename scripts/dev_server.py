from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

def run_server():
    # 切换到项目根目录
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    port = 8080
    server_address = ('', port)
    httpd = HTTPServer(server_address, CORSRequestHandler)
    print(f"开发服务器运行在 http://localhost:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server() 