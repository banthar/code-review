
import cgi

def htmlescape(text):
	return cgi.escape(text, quote=True)

class TextNode:
	def __init__(self, content):
		self.content = content
	def to_string(self):
		return htmlescape(self.content)

class HTMLNode:
	def __init__(self, kind, children, attributes):
		def create_node(node):
			if isinstance(node, str):
				return TextNode(node)
			if isinstance(node, unicode):
				return TextNode(node.decode('utf-8'))
			else:
				return node

		def create_nodes(nodes):
			return map(create_node, nodes)

		self.kind = kind
		self.children = create_nodes(children)
		self.attributes = attributes
	def to_string(self):
		attributeText = ''
		for name, value in self.attributes.iteritems():
			attributeText += ' {}=\'{}\''.format(htmlescape(name), htmlescape(value))
		if self.children:
			return '<'+self.kind+attributeText+'>'+''.join(map(lambda x: x.to_string(), self.children))+'</'+self.kind+'>'
		else:
			return '<'+self.kind+attributeText+'/>'

def absolute(*elements):
	return '/'+'/'.join(elements)

def a(*args, **attributes):
	return HTMLNode('a', args, attributes)

def li(*args, **attributes):
	return HTMLNode('li', args, attributes)

def ul(*args, **attributes):
	return HTMLNode('ul', args, attributes)

def pre(*args, **attributes):
	return HTMLNode('pre', args, attributes)

def p(*args, **attributes):
	return HTMLNode('p', args, attributes)


