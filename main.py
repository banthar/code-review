#!/usr/bin/python
# -*- coding: utf-8 -*-

import BaseHTTPServer
import git
import difflib
import urlparse
import re
import html

config = {
	'issue_regex': '(BUG-\d+)',
	'issue_url_format': r'/issue/\1',
}

repo = git.Repo('/home/piotr/projekty/review/test_repo.git')

def link_issues(text):
	return re.sub(config['issue_regex'], r'[\1](' + config['issue_url_format'] + ')', text)

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
		return 'New file: ' + diff.a_blob.name
	if diff.deleted_file:
		return 'Delete: ' + diff.b_blob.name
	else:
		return 'Changed: ' + diff.b_blob.name

def diff_to_html(diff):
	return html.li(diff_to_html_head(diff), html.pre(diff.diff))

def get_commit(request, args):
	[_, commit_id] = args
	commit = repo.commit(commit_id)
	try:
		[parent] = commit.parents
	except ValueError:
		return 'no parent'
	diff = parent.diff(commit, None, True)
	return html.p(html.a(commit.hexsha[0:12], href=html.absolute('commit', commit.hexsha)), ' ', commit.summary, html.ul(*map(diff_to_html, diff)))

def get_commits(request, args):
	[_, ref_name] = args
	ref = repo.refs[ref_name]
	commit = ref.commit
	lis = []
	while commit:
		try:
			[parent] = commit.parents
		except ValueError:
			break
		diff = parent.diff(commit, None, True)
		changes = html.ul(*map(lambda c: html.li(diff_to_html_head(c)), diff))
		lis.append(html.li(html.a(commit.hexsha[0:12], href=html.absolute('commit', commit.hexsha)), ' ', commit.summary, changes))
		commit = parent

	return html.ul(*lis)

def get_issues(request, args):
	return ''

def get_test(request, args):
	request.wfile.write("\n".join(list(difflib.context_diff(['a','b'], ['a','c']))))

if __name__ == '__main__':
	handlers = {
			'': get_refs,
			'test': get_test,
			'commit': get_commit,
			'commits': get_commits,
			'issues': get_issues,
		}

	class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
		def do_GET(s):
			path = s.path.split('/')[1:]
			command = '' if len(path) == 0 else path[0]
			if command in handlers:
				content = handlers[command](s, path)
				s.send_response(200)
				s.send_header('Content-Type', 'text/html; charset=UTF-8');
				s.end_headers()
				s.wfile.write(content.to_string())
			else:
				s.send_error(404, 'invalid path: {}'.format(s.path))

	httpd = BaseHTTPServer.HTTPServer(('localhost', 8080), MyHandler)
	httpd.serve_forever()

