#!/usr/bin/python
# -*- coding: utf-8 -*-

import BaseHTTPServer
import git
import difflib
import urlparse
import re
import html
import collections
import cgi
import itertools
import filedb

repo = git.Repo('/home/piotr/projekty/linux')
db = filedb.FileDb('objects')

def get_refs(request, args):
	def get_ref(ref):
		commits = html.a('commits', href=html.absolute('commits', ref.name))
		issues = html.a('issues', href=html.absolute('issues', ref.name))
		return html.li(ref.name, ' ', commits, ' ', issues)
		
	return html.ul(*map(get_ref, repo.refs))

def diff_to_html_head(diff):
	if diff.renamed:
		return 'Rename: ' + diff.rename_from + ' -> ' + diff.rename_to
	if diff.new_file:
		return 'New file: ' + diff.a_blob.path
	if diff.deleted_file:
		return 'Delete: ' + diff.b_blob.path
	else:
		return 'Changed: ' + diff.b_blob.path

def diff_to_html(diff):
	return html.li(diff_to_html_head(diff), html.pre(diff.diff))

def get_commit(request, args):
	[commit_id] = args
	commit = repo.commit(commit_id)
	parent = commit.parents[0]
	diff = parent.diff(commit, None, True)
	return html.p(html.a(commit.hexsha[0:12], href=html.absolute('commit', commit.hexsha)), ' ', commit.summary, html.ul(*map(diff_to_html, diff)))

def get_commits(request, args):
	[ref_name] = args
	ref = repo.refs[ref_name]
	lis = []
	for commit in ref.commit.iter_parents():
		check = html.input(type="checkbox", name=commit.hexsha)
		link = html.a(commit.hexsha[0:12], href=html.absolute('commit', commit.hexsha))
		lis.append(html.li(check, ' ', link, ' ', commit.summary))
		if len(lis) > 100:
			break
	create_review = html.input(value='create review', type='submit')
	return html.form(create_review, html.ul(*lis), method='post', action=html.absolute('review', 'create'))

def get_issues(request, args):
	return html.text('')

def compare_commits(left, right):
	if left == right:
		return 0 
	ileft = left.iter_parents()
	iright = right.iter_parents()

	try:
		while True:
			l = ileft.next()
			r = iright.next()
			if l == right:
				return -1
			if r == left:
				return 1
	except StopIteration:
		return 0
		
def diffs_to_affected_paths(diffs):
	paths = set()
	for diff in diffs:
		paths.update(diff_to_affected_paths(diff))
	return paths

def diff_to_affected_paths(diff):
	paths = set()
	if diff.renamed:
		paths.add(diff.rename_from)
		paths.add(diff.rename_to)
	if diff.a_blob:
		paths.add(diff.a_blob.path)
	if diff.b_blob:
		paths.add(diff.b_blob.path)
	return paths

def get_reviews(request, args):
	def review_to_html(r):
		hexsha, review = r
		return html.li(str(review))	
	return html.ul(*map(review_to_html, db.iterate('open_reviews')))


def get_review(request, args):
	[hexsha] = args
	review = db.get('open_reviews', hexsha)
	base = repo.commit(review['baseCommit'])
	last = repo.commit(review['lastCommit'])
	affectedPaths = set(review['affectedPaths'])
	
	diff = base.diff(last, None, True)
	filtered_diff = filter(lambda d: not diff_to_affected_paths(d).isdisjoint(affectedPaths), diff)
	return html.ul(*map(diff_to_html, filtered_diff))

def post_review_create(request, args, form):
	commits = map(lambda x: repo.commit(x.name), form.list)
	included = sorted(commits, cmp=compare_commits)
	first = included[-1]
	last = included[0]
	diffs = first.parents[0].diff(last)
	paths = set()
	for c in included:
		paths.update(diffs_to_affected_paths(c.diff(c.parents[0])))

	review = {
		'baseCommit': first.parents[0].hexsha,
		'lastCommit': last.hexsha,
		'affectedPaths': list(paths),
		'includedCommits': list(map(lambda c: c.hexsha, included)),
	}
	return ['review', db.add('open_reviews', review)]

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

root_handler = Handler(get_refs, None,
	commit = Handler(get_commit, None),
	commits = Handler(get_commits, None),
	review = Handler(get_review, None, 
		create= Handler(None, post_review_create),
	),
	reviews = Handler(get_reviews, None), 
)

if __name__ == '__main__':
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

	httpd = BaseHTTPServer.HTTPServer(('localhost', 8080), MyHandler)
	httpd.serve_forever()

