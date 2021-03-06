#!/usr/bin/python
# -*- coding: utf-8 -*-

import git
import difflib
import re
import html
import collections
import itertools
import filedb
import http
import json

def read_file(filename):
	with open(filename,'rb') as f:
		return f.read()

def read_json(filename):
	with open(filename,'rb') as f:
		return json.load(f)

config = read_json('config.json')
repo = git.Repo(config['repo'])
db = filedb.FileDb(config['storage_path'])
style = read_file('style.css')
script = read_file('script.js')

def html_page(title, *content, **arguments):
	head = html.head(
		html.link(rel="shortcut icon", href=config['favicon']),
		html.title("{} - {}".format(title, config['title'])),
		html.style(style),
	)
	nav = html.nav(html.ul(
		html.li(html.a('⚗', href=html.absolute())),
		html.li(html.a('Reviews', href=html.absolute('reviews'))),
		html.li(html.a('Commits', href=html.absolute('commits', repo.head.ref.name))),
		html.li(html.a('Tree', href=html.absolute('tree', repo.head.ref.name))),
		html.li(html.a('Refs', href=html.absolute('refs'))),
	))
	return http.Html(html.html(head, html.body(*((nav,)+content+(html.script(script),)),**arguments)))

def get_refs(request, args):
	def get_ref(ref):
		commits = html.a('commits', href=html.absolute('commits', ref.name))
		tree = html.a('tree', href=html.absolute('tree', ref.name))
		return html.tr(html.td(ref.name), html.td(commits), html.td(tree))
		
	return html_page('Refs', html.div(html.table(*map(get_ref, repo.refs), **{'class': 'list'})))

def diff_to_html(diff):
	def parse_segment_header(header):
		m = re.match('^@@ -(\d+),(\d+) \+(\d+),(\d+) @@', header)
		return (int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)))
	def line_to_html(left, right, content, classes):
		left_td = html.td() if left == 0 else html.td(str(left), **{'class': 'h', 'id': '{}L{}'.format(diff.a_blob, left)})
		right_td = html.td() if right == 0 else html.td(str(right), **{'class': 'h', 'id': '{}R{}'.format(diff.b_blob, right)})
		return html.tr(left_td, right_td, html.td(content), **{'class': classes})
	def italize_control_char(line):
		return (html.span(line[0], **{'class': 'h'}), line[1:])
	rows = []
	lines = diff.diff.split('\n')
	moved_from = lines.pop(0)
	rows.append(line_to_html(0, 0, moved_from, 'h r'))
	moved_to = lines.pop(0)
	rows.append(line_to_html(0, 0, moved_to, 'h a'))
	for line in lines:
		if len(line) == 0:
			continue
		elif line[0] == '+':
			rows.append(line_to_html(0, right_line, italize_control_char(line), 'c a'))
			right_line+=1
		elif line[0] == '-':
			rows.append(line_to_html(left_line, 0, italize_control_char(line), 'c r'))
			left_line+=1
		elif line[0] == '@':
			(left_line,_,right_line,_) = parse_segment_header(line)
			rows.append(line_to_html(0, 0, line, 'h'))
			continue
		elif line[0] == ' ':
			rows.append(line_to_html(left_line, right_line, line, 'c'))
			right_line+=1
			left_line+=1
		else:
			raise Exception()
	return html.div(html.table(*rows, **{'class': 'diff'}))

def get_commit(request, args):
	[commit_id] = args
	commit = repo.commit(commit_id)
	parent = commit.parents[0]
	diff = parent.diff(commit, None, True)
	header = html.div(html.a(commit.hexsha[0:12], href=html.absolute('commit', commit.hexsha)),	' ', commit.summary)
	diffs = map(diff_to_html, diff)
	return html_page('Commit {}'.format(commit.hexsha[0:12]), header, *diffs)

def commit_to_html(commit):
	link = html.a(commit.hexsha[0:12], href=html.absolute('commit', commit.hexsha))
	return link, ' ', commit.summary

def get_commits(request, args):
	ref_name = '/'.join(args)
	rows = []
	for commit in repo.iter_commits(ref_name, max_count=config['displayed_commits']):
		check = html.input(type="checkbox", name=commit.hexsha)
		rows.append(html.tr(html.td(check, ' ', *commit_to_html(commit))))
	create_review = html.input(value='Create Review', type='submit')
	reset = html.input(value='Reset', type='reset')
	body = html.form(create_review, reset, html.hr(), html.table(*rows, **{'class': 'list'}), method='post', action=html.absolute('review', 'create'))
	return html_page('Commits {}'.format(ref_name), html.div(body))

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

def review_to_html_summary(r):
	hexsha, review = r
	commits = html.ul(*map(lambda c: html.li(*commit_to_html(repo.commit(c))), review['includedCommits']))
	return html.div(html.h1(html.a(hexsha[0:12], href=html.absolute('review', hexsha))), commits, **{'class': 'review'})

def get_reviews(request, args):
	return html_page('Reviews', *map(review_to_html_summary, db.iterate('open_reviews')))

def review_to_diff(review):
	base = repo.commit(review['baseCommit'])
	last = repo.commit(review['lastCommit'])
	affectedPaths = set(review['affectedPaths'])
	diff = base.diff(last, None, True, U=config['diff_context'], w=config['diff_ignore_whitespace'])
	return filter(lambda d: not diff_to_affected_paths(d).isdisjoint(affectedPaths), diff)

def get_patch(request, args):
	[hexsha] = args
	review = db.get('open_reviews', hexsha)
	diff = review_to_diff(review)
	return http.Text(''.join(map(lambda d: str(d), diff)))

def get_review(request, args):
	[hexsha] = args
	review = db.get('open_reviews', hexsha)
	patch = html.a('patch', href=html.absolute('patch', hexsha))
	buttons = html.div(patch)
	header = html.div(review_to_html_summary((hexsha, review)), html.hr(), buttons)
	diff = review_to_diff(review)
	return html_page('Review {}'.format(hexsha[0:12]), header, *map(diff_to_html, diff), onload='initComments(\'{}\');'.format(hexsha))

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
	return http.Created(html.absolute('review', db.add('open_reviews', review)))

def bytes_to_human(n):
	return str(n)+' B'

def get_tree(request, args):
	ref_name = args[0]
	path = args[1:]
	ref = repo.refs[ref_name]
	rows = []
	tree = ref.commit.tree
	for p in path:
		tree = tree[p]
	if isinstance(tree, git.Blob):
		body = html.pre(tree.data_stream.read())
	else:
		rows.append(html.tr(html.th('Name'), html.th('Size'), html.th('Type')))
		if len(args)>1:
			rows.append(html.tr(html.td(html.a('..', href='/'+'/'.join(['tree']+args[:1]))), html.td(), html.td('[DIR]')))
		for d in tree.trees:
			link = html.td(html.a(d.name+'/', href='/'+'/'.join(['tree']+args+[d.name])))
			rows.append(html.tr(link, html.td(), html.td('[DIR]')))
		for blob in tree.blobs:
			link = html.td(html.a(blob.name, href='/'+'/'.join(['tree']+args+[blob.name])))
			size = html.td(bytes_to_human(blob.size))
			rows.append(html.tr(link, size, html.td(blob.mime_type)))
		body = html.table(*rows, **{'class': 'list'})
	return html_page('Tree {} /{}'.format(ref_name, '/'.join(path)), html.div(body))

def get_comments(request, args):
	[review_id] = args
	comments = []
	for id, m in db.iterate('comments_'+review_id):
		m['id'] = id
		comments.append(m)
	return http.Json(comments)

def post_comment_create(request, args, form):
	review_id = form['review_id'].value
	left_id = form['left_id'].value if form.has_key('left_id') else None
	right_id = form['right_id'].value if form.has_key('right_id') else None
	if not form.has_key('message'):
		return http.Error(400, 'Missing comment message')
	db.add('comments_' + review_id, {
		'message': form['message'].value,
		'left_id': left_id,
		'right_id': right_id
	})
	return http.Created(html.absolute('comments', review_id))

if __name__ == '__main__':
	http.serve(('localhost', 8080), http.Handler(get_reviews, None,
		review = http.Handler(get_review, None, 
			create= http.Handler(None, post_review_create),
		),
		reviews = http.Handler(get_reviews, None), 
		commit = http.Handler(get_commit, None),
		commits = http.Handler(get_commits, None),
		comment = http.Handler(None, None,
			create= http.Handler(None, post_comment_create),
		),
		comments = http.Handler(get_comments, None),
		tree = http.Handler(get_tree, None),
		refs = http.Handler(get_refs, None),
		patch = http.Handler(get_patch, None),
	))

