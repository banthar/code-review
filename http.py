#!/usr/bin/python
# -*- coding: utf-8 -*-

import BaseHTTPServer
import urlparse
import cgi

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
		def serve_html(self, content):
			self.send_response(200)
			self.send_header('Content-Type', 'text/html; charset=UTF-8');
			self.end_headers()
			self.wfile.write(content.to_string())
		def serve_found(self, new_location):
			self.send_response(302, 'created')
			self.send_header('Location', new_location);
			self.end_headers()
		def serve_not_found(self):
			self.send_error(404, 'invalid path: {}'.format(self.path))
		def serve_invalid_method(self, method):
			self.send_error(405, 'invalid method: {}'.format(method))
		def do_GET(self):
			(handler, args) = root_handler.find(self.get_path())
			if handler:
				if handler.do_GET:
					self.serve_html(handler.do_GET(self, args))
				else:
					self.serve_invalid_method('GET')
			else:
				self.serve_not_found()
		def do_POST(self):
			(handler, args) = root_handler.find(self.get_path())
			if handler:
				if handler.do_POST:
					form = cgi.FieldStorage(
						fp=self.rfile,
						headers=self.headers,
						environ={"REQUEST_METHOD": "POST"}
					)
					self.serve_found(html.absolute(*handler.do_POST(self, args, form)))
				else:
					self.serve_invalid_method('POST')
			else:
				self.serve_not_found()

	httpd = BaseHTTPServer.HTTPServer(address, MyHandler)
	httpd.serve_forever()
