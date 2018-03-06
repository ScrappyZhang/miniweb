from gevent import monkey
monkey.patch_all()

"""遵循WSGI的mini-web服务器"""
'''
@Time    : 2017/11/25 下午7:06
@Author  : scrappy_zhang
@File    : mini_web.py
'''

# web服务器的本质
"""
1.浏览器发送一个HTTP请求；
2.服务器收到请求，生成一个HTML文档；
3.服务器把HTML文档作为HTTP响应的Body发送给浏览器；
4.浏览器收到HTTP响应，从HTTP Body取出HTML文档并显示。
"""

"""
最简单的Web应用就是先把HTML用文件保存好，用一个现成的HTTP服务器软件，接收用户请求，从文件中读取HTML，返回.
例如Apache、Nginx、Lighttpd等这些常见的静态服务器。

当遇到动态请求时，则通过app本身来实现，即后端。
"""
# 进程
# import multiprocessing
import socket
import re
import gevent
import sys
import time
import os

STATIC_ROOT = './static'  # 静态目录


class HTTPServer(object):
    def __init__(self, port, app):
        """初识化操作"""
        # 1 创建TCP套接字
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 2 设置地址重用选项-让服务器重启之后可以理解重新使用绑定的端口
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # 2 绑定端口 监听  取客户端
        server_socket.bind(('', port))  #

        server_socket.listen(128)  # 128表示可监听最大连接数

        self.server_socket = server_socket

        self.app = app

    def run_forever(self):
        print('服务器已经启动！http://localhost:8888')
        while True:
            new_socket, new_addr = self.server_socket.accept()
            # 接受一个客户端连接  使用一个协程为客户服务
            gevent.spawn(self.deal_with_request, new_socket, new_addr)


    def deal_with_request(self, client_socket, client_addr):
        """针对每个客户端 使用这个函数进行服务"""
        print("接受到来自%s的连接请求" % str(client_addr))
        recv_data = client_socket.recv(4096)
        # 给client-socket 服务
        # 接收客户端请求报文数据
        # recv_data = client_socket.recv(4096)
        # print(recv_data)
        # 将Bytes类型的数据 进行解码 ----> str
        recv_str_data = recv_data.decode()

        # 对请求报文 按行进行切割 返回值就是含有每行数据的 列表   请求行就是列表中0号元素
        data_list = recv_str_data.split('\r\n')
        # print(data_list)

        request_line = data_list[0]
        # print(request_line)

        # 使用正则从 请求行 将用户请求路径 提取出来 GET /index.html HTTP/1.1
        res = re.match(r"\w+\s+(\S+)", request_line)
        if not res:
            # 匹配失败
            print("HTTP请求报文格式错误")
            client_socket.close()
            return
        # 根据匹配结果对象 获取出用户请求路径信息 在第一个分组
        path_info = res.group(1)
        print("接收到用户的请求:%s" % path_info)
        # /路径对于web服务器来讲  对应的是首页资源  是web服务器通用的潜规则
        if path_info == '/':
            path_info = '/index.html'
        path_info = path_info.lstrip('/')
        env = {
            "path": path_info
        }
        # 判断浏览器请求的资源类型 动态 还是 静态
        # 如果是动态 走动态处理的流程。这里假设.py结尾的均对应为后台app生成的动态资源
        if path_info.endswith(".py"):
            # Application相当于一般的web后端应用框架部分，主要进行请求处理业务。这边可以分离服务器与数据处理业务
            # import Application
            # app函数返回值就是响应体        HTTP请求相关的字典  函数引用
            # 调用app并返回相应头，期间app会调用web服务器的请求头设置部分。
            response_body = self.app(env, self.start_response)
            # 拼接响应状态 头部+空行+响应体
            response_data = self.status_header + response_body

            # 发送相应内容 关闭客户端套接字
            client_socket.sendall(response_data.encode())
            client_socket.close()
            return
        # 如果是静态请求，走web服务器的资源调用流程
        # ./static + /index.html
        # 根据用户请求的路径 读取指定路径下的文件数据 将数据 以HTTP响应报文格式发送给浏览器即可
        file_name = os.path.join(STATIC_ROOT, path_info)
        print('要请求的静态文件是:',file_name)

        # try:
        #     # 根据用户请求的路径 读取指定路径下的文件数据 将数据 以HTTP响应报文格式发送给浏览器即可
        #     print("./static/" + path_info)
        #     file = open("./static/" + path_info, "rb")
        #
        #     file_data = file.read()  # bytes
        #     file.close()
        # except FileNotFoundError as e:
        #     print(e)
        #     # 用户请求的资源路径不存在 应该返回404 Not Found
        #     # 响应行
        #     response_line = "HTTP/1.1 404 Not Found\r\n"
        #
        #     # 响应头
        #     response_headers = "Server: PWS4.0\r\n"
        #
        #     # 响应体
        #     response_body = "ERROR!!!!!!!!!!"
        #
        #     response_data = response_line + response_headers + "\r\n" + response_body
        #
        #     # send函数的返回值代表 成功发送的字节数----> 可能一下不能全部发送完数据
        #     client_socket.send(response_data.encode())
        # else:
        #     # 给客户端回HTTP响应报文
        #     # 响应行
        #     response_line = "HTTP/1.1 200 OK\r\n"
        #
        #     # 响应头
        #     response_headers = "Server: PWS4.0\r\n"
        #
        #     # 响应体
        #     response_body = file_data
        #
        #     # 拼接响应报文  发送给客户端
        #     response_data = (response_line + response_headers + '\r\n').encode() + response_body
        #     # send函数的返回值代表 成功发送的字节数----> 可能一下不能全部发送完数据
        #     # client_socket.send(response_data)
        #     client_socket.sendall(response_data)
        #
        # finally:
        #     # 关掉套接字
        #     client_socket.close()


        if os.path.isfile(file_name):
            with open(file_name, 'rb') as f:
                file_data = f.read()
            # print(content)
            # 文件存在，给客户端回HTTP响应报文
            # 响应行
            response_line = "HTTP/1.1 200 OK\r\n"
            # 响应头
            response_headers = "Server: PWS\r\n"
            if path_info.endswith('.html'):
                # 保证中文显示
                response_headers = response_headers + "Content-Type: text/html;charset=utf-8\r\n"
            # 响应体
            response_body = file_data
            # 拼接响应报文  发送给客户端
            response_data = (response_line + response_headers + '\r\n').encode() + response_body
            # send函数的返回值代表 成功发送的字节数----> 可能一下不能全部发送完数据
            # client_socket.send(response_data)
            client_socket.sendall(response_data)
            client_socket.close()
            return

        # 用户请求的资源路径不存在 应该返回404 Not Found
        # 响应行
        response_line = "HTTP/1.1 404 Not Found\r\n"
        # 响应头
        response_headers = "Server: PWS\r\n"
        # 响应体
        response_body = "<h1>ERROR!!</h1>"
        response_data = response_line + response_headers + "\r\n" + response_body
        # send函数的返回值代表 成功发送的字节数----> 可能一下不能全部发送完数据
        client_socket.sendall(response_data.encode())
        client_socket.close()

    def start_response(self, status, header_list):
        """保存 应用框架提供的状态和响应头"""
        response_header_default = [
            ("Data", time.ctime()),
            ("Server", "PWS")
        ]
        header_list = header_list + response_header_default
        # 该属性存储 响应状态和 响应头  在其他方法中使用
        self.status_header = "HTTP/1.1 %s\r\n" % status
        for header_name, header_value in header_list:
            self.status_header += "%s: %s\r\n" % (header_name, header_value)

        # 追加空行，空行后就是body了
        self.status_header += '\r\n'


def main():
    # python web.py 8888
    if len(sys.argv) != 3:
        print("使用方式错误 请使用:python mini_web.py 8888 应用框架名:应用名")
        return
    # sys是一个存放 命令行参数 的列表  其中每一个元素是字符串
    # 第0个元素是程序名称 888a
    port = sys.argv[1]
    if not port.isdigit():
        print("端口号只能是数字 ")
        return

    # import Application
    module_name_func_name = sys.argv[2]
    data_list = module_name_func_name.split(':')
    if len(data_list) != 2:
        print("使用方式错误 请使用:python mini_web.py 8888 应用框架名:应用名")
        return
    module_name = data_list[0]
    func_name = data_list[1]

    # 相当于app注册
    # app = Application.app
    try:
        mod = __import__(module_name)
        app = getattr(mod, func_name)
    except Exception as e:
        print("应用框架或者应用名错误 请使用:python mini_web.py 8888 应用框架名:应用名")
        return
    else:

        portnumber = int(port)
        # port = 8888
        # 创建一个HTTPServer类型的对象
        http_server = HTTPServer(portnumber, app)

        # 启动对象 开始启动HTTP服务
        http_server.run_forever()


if __name__ == '__main__':
    main()
