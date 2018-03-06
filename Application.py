"""
请求数据处理——相当于web应用
它是由WSGI服务器来调用
"""
'''
@Time    : 2017/11/25 下午7:12
@Author  : scrappy_zhang
@File    : Application.py
'''
"""
根据WSGI协议
仅需要应用开发者实现一个函数来响应HTTP请求。
例如：
def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    return '<h1>Hello, web!</h1>'
该application函数便是一个复合WSGI标准的应用函数：
它接收两个参数environ、start_response.
environ:是一个包含所有HTTP请求信息的dict对象，由web服务器提供给后端应用。
start_response：一个由服务器提供的发送HTTP响应的函数，其第一个参数为请求响应状态码，第二个参数为其他发送给浏览器的响应头。
该application函数返回响应体等。

那么我们在application.py里只需要专注于解析environ这个字典类型对象，拿到合适的HTTP请求信息，
然后根据请求构造合适的动态HTML返回给服务器，并根据请求信息，告诉服务器回复浏览器何种响应头。
"""

import time
import os

template_root = "./templates"


def index(file_name):
    file_name = file_name.replace(".py", ".html")
    # file_name = file_name.lstrip('/')
    file = os.path.join(template_root, file_name)
    print(os.path.isfile(file))
    if os.path.isfile(file):
        with open(file) as f:
            content = f.read()
        return content
    else:
        return '<h1>404 页面不存在</h1>'


def center(file_name):
    file_name = file_name.replace(".py", ".html")
    # file_name = file_name.lstrip('/')
    # print(file_name)
    file = os.path.join(template_root, file_name)
    print(file)
    if os.path.exists(file):
        with open(file) as f:
            content = f.read()
        return content
    else:
        return '<h1>404 页面不存在</h1>'


def app(environ, start_response):
    if environ['path'].endswith('.py'):
        file_name = environ['path']
        print(file_name)
        status = '200 OK'
        response_headers = [('Content-Type', 'text/html'), ('Content-Type', 'text/html;charset=utf-8')]
        start_response(status, response_headers)
        if file_name == "index.py":
            return index(file_name)
        elif file_name == "center.py":
            return center(file_name)
    start_response('404 OK', [('Content-Type', 'text/html'), ('Content-Type', 'text/html;charset=utf-8')])
    return '<h1>你好,ERROR</h1><hr>现在是时间:' + time.ctime()
