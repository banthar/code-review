#!/usr/bin/python
# -*- coding: utf-8 -*-

import BaseHTTPServer
import urlparse
import cgi
import json

class Html:
	def __init__(self, html):
		self.html = html
	def serve(self, response):
		response.send_response(200)
		response.send_header('Content-Type', 'text/html; charset=UTF-8');
		response.end_headers()
		response.wfile.write(self.html.to_string())

class Text:
	def __init__(self, text):
		self.text = text
	def serve(self, response):
		response.send_response(200)
		response.send_header('Content-Type', 'text/plain; charset=UTF-8');
		response.end_headers()
		response.wfile.write(self.text)

class Created:
	def __init__(self, location):
		self.location = location
	def serve(self, response):
		response.send_response(302)
		response.send_header('Location', self.location);
		response.end_headers()

class Handler:
	def __init__(self, do_GET, do_POST, **children):
		self.do_GET = do_GET
		self.do_POST = do_POST
		self.children = children
	def find(self, path):
		if path == [] or path[0] not in self.children:
			return (self, path)
		else:
			return self.children[path[0]].find(path[1:])

def serve(address, root_handler):
	class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
		def get_path(self):
			return self.path.split('/')[1:]

		def serve_not_found(self):
			self.send_error(404, 'invalid path: {}'.format(self.path))
		def serve_invalid_method(self, method):
			self.send_error(405, 'invalid method: {}'.format(method))
		def do_GET(self):
			(handler, args) = root_handler.find(self.get_path())
			if handler:
				if handler.do_GET:
					handler.do_GET(self, args).serve(self)
				else:
					self.serve_invalid_method('GET')
			else:
				self.serve_not_found()
		def do_POST(self):
			(handler, args) = root_handler.find(self.get_path())
			if handler:
				if handler.do_POST:
					content_type = self.headers['Content-Type']
					if content_type == 'application/x-www-form-urlencoded':
						form = cgi.FieldStorage(
							fp=self.rfile,
							headers=self.headers,
							environ={"REQUEST_METHOD": "POST"}
						)
					else:
						raise Exception("Unsupported content type: "+content_type)
					handler.do_POST(self, args, form).serve(self)
				else:
					self.serve_invalid_method('POST')
			else:
				self.serve_not_found()

	httpd = BaseHTTPServer.HTTPServer(address, MyHandler)
	httpd.serve_forever()
