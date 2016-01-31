#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi

def htmlescape(text):
	return cgi.escape(text, quote=True)

class RawNode:
	def __init__(self, content):
		self.content = content
	def to_string(self):
		return self.content

class TextNode:
	def __init__(self, content):
		self.content = content
	def to_string(self):
		return htmlescape(self.content)

class HTMLNode:
	def __init__(self, kind, children, attributes):
		def add_children(nodes):
			for node in nodes:
				if isinstance(node, str):
					self.children.append(TextNode(node))
				elif isinstance(node, unicode):
					self.children.append(TextNode(node.encode('utf-8')))
				elif isinstance(node, tuple) or isinstance(node, list):
					add_children(node)
				else:
					self.children.append(node)

		self.kind = kind
		self.children = []
		self.attributes = attributes
		add_children(children)

	def to_string(self):
		attributeText = ''
		for name, value in self.attributes.iteritems():
			attributeText += ' {}=\'{}\''.format(htmlescape(name), htmlescape(value))
		if self.children:
			return '<'+self.kind+attributeText+'>'+''.join(map(lambda x: x.to_string(), self.children))+'</'+self.kind+'>'
		else:
			return '<'+self.kind+attributeText+'/>'

def absolute(*elements):
	return '/'+relative(*elements)

def relative(*elements):
	return '/'.join(elements)


def a(*args, **attributes):
	return HTMLNode('a', args, attributes)

def h1(*args, **attributes):
	return HTMLNode('h1', args, attributes)

def ul(*args, **attributes):
	return HTMLNode('ul', args, attributes)

def nav(*args, **attributes):
	return HTMLNode('nav', args, attributes)

def li(*args, **attributes):
	return HTMLNode('li', args, attributes)

def pre(*args, **attributes):
	return HTMLNode('pre', args, attributes)

def p(*args, **attributes):
	return HTMLNode('p', args, attributes)

def span(*args, **attributes):
	return HTMLNode('span', args, attributes)

def div(*args, **attributes):
	return HTMLNode('div', args, attributes)

def input(*args, **attributes):
	return HTMLNode('input', args, attributes)

def form(*args, **attributes):
	return HTMLNode('form', args, attributes)

def html(*args, **attributes):
	return HTMLNode('html', args, attributes)

def head(*args, **attributes):
	return HTMLNode('head', args, attributes)

def body(*args, **attributes):
	return HTMLNode('body', args, attributes)

def title(*args, **attributes):
	return HTMLNode('title', args, attributes)

def link(*args, **attributes):
	return HTMLNode('link', args, attributes)

def table(*args, **attributes):
	return HTMLNode('table', args, attributes)

def tr(*args, **attributes):
	return HTMLNode('tr', args, attributes)

def td(*args, **attributes):
	return HTMLNode('td', args, attributes)

def th(*args, **attributes):
	return HTMLNode('th', args, attributes)

def hr(*args, **attributes):
	return HTMLNode('hr', args, attributes)

def style(content):
	return  HTMLNode('style', [RawNode(content)], {})

def script(content):
	return HTMLNode('script', [RawNode(content)], {})


def text(content):
	return TextNode(content)

