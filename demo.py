import socket
import threading
import os

HOST = '127.0.0.1'  #localhost
PORT = 8080

class Response_Client:
    def __init__(struct, path):
        print("path from request:  ", path , "\n")
        if path == "/" or path == "/404.html":
            path = "/index.html"
        type_File = path.split(".")[-1]   # determine type file
        if(check_exist_file(path)):
            if path == "/401.html":
                struct.status = 401
            else:
                struct.status = 200
            struct.path = "src_html_de01" + path
            
            #truong hop neu nhu client yeu truy cap den trang images.html ma chua dang nhap
            #thi se khong duoc phep (yeu cau la phai dang nhap moi truy cap vao duoc)
            if(path == "/images.html" and open("save_method.txt", "r").read() == "GET"):
                struct.status = 404
                struct.path = "src_html_de01/404.html"
        else:
            struct.status = 404
            struct.path = "src_html_de01/404.html"

        # xac dinh kieu tra ve cua file
        if(type_File == "html"):
            struct.contentType = "Content-Type: text/html"
        elif(type_File == "css"):
            struct.contentType = "Content-Type: text/css"
        elif(type_File == "png"):
            struct.contentType = "Content-Type: image/png"
        elif(type_File == "jpg"):
            struct.contentType = "Content-Type: image/jpeg"
        elif(type_File == "ico"):
            struct.contentType = "Content-Type: image/x-icon"
        else:
            struct.contentType = "Content-Type: text/html" 
        
        #xac dinh header
        if(struct.status == 200):
            status_line = "HTTP/1.1 200 OK"
        elif(struct.status == 401):
            status_line = "HTTP/1.1 401 Unauthorized"
        else:
            status_line = "HTTP/1.1 404 Not Found"
        struct.response_content = "%s\r\n%s\r\n"%(status_line, struct.contentType)

    def Send_File(struct):
        struct.data = open(struct.path, "rb")
        content = struct.data.read()
        struct.response_content += "Content-Length: %d\r\n\r\n"%(len(content))
        result = struct.response_content.encode("utf-8") + content + "\r\n".encode("utf-8")
        #in thong tin reponse 
        print("-----------------------------------------------------\n")
        print("\n")
        print("Response:\n")
        print("status: ", struct.status, "\n")
        print("path: ", struct.path, "\n")
        print(struct.contentType)
        print("\n")
        return result

       # multi_request form one client send to server
def handle_request_Client(conn, address):
    while True:
        request = get_request(conn)
        re = Request_Analyze(request)
        if(not re.empty):
            print("--------------------------------------------\n")
            print("connection: ", address, "\n")
            print("Request:\n")
            print("method: ",re.method, "\n")
            print("path: ", re.path, "\n")
            # Send HTTP response
            if(re.method == "GET"):
                GET(conn, re)
            if(re.method == "POST"):
                POST(conn, re)  
            

#send request by GET method
def GET(connection, request):
    open("save_method.txt", "w").write("GET")
    connection.sendall(Response_Client(request.path).Send_File())

#send request by POST method
def POST(conn, request):
    open("save_method.txt", "w").write("POST")
    if(request.content == "uname=admin&psw=123456&remember=on"):
        conn.sendall(Response_Client(request.path).Send_File())
    else:
        requestPath = "/401.html"
        conn.sendall(Response_Client(requestPath).Send_File())

#khoi tao struct luu method, path, content tu viec phan tich request
class Request_Analyze:
    def __init__(struct, request):
        request_Array = request.split("\n")
        if request == "":
            struct.empty = True	
        else:
            if request_Array[0] == "GET / HTTP/1.1":
                struct.empty = False
                struct.method = "GET"
                struct.path = "/index.html"
                struct.content = request_Array[-1]
            else:
                struct.empty = False
                struct.method = request_Array[0].split(" ")[0]
                struct.path = request_Array[0].split(" ")[1]
                struct.content = request_Array[-1]
       
#check duong dan cua file co ton tai hay khong  
def check_exist_file(path):
    file_path =  "./src_html_de01" + path
    return os.path.isfile(file_path)

def get_request(conn):
    request = ""
    conn.settimeout(1)
    try:
        # Receive request from client
        request = conn.recv(1024).decode()
        while (request != ""):
            request += conn.recv(1024).decode()
    except socket.timeout:
        if not request:
            i = 1
    finally:
        return request

# tao Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print("...................Waiting connention from client..................\n")


if(__name__ == "__main__"):
    #multi_client gui den server
    while True:
        connection, address = server.accept()
        thr = threading.Thread(target = handle_request_Client, args=(connection, address,))
        thr.start()