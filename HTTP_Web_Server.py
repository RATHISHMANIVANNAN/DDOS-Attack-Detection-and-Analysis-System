import http.server
import socketserver
import socket

# Set the port number you want to use
PORT = 8000

# Create a handler for the HTTP requests
Handler = http.server.SimpleHTTPRequestHandler

# Get the local IP address
local_ip = socket.gethostbyname(socket.gethostname())

# Create a TCP socket server
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at http://{local_ip}:{PORT}")
    # Start the server
    httpd.serve_forever()
