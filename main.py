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
import static

repo = git.Repo('/home/piotr/projekty/linux.git')
db = filedb.FileDb('objects')

def html_page(title, *content):
	head = html.head(
		html.link(rel="shortcut icon", href=static.favicon),
		html.title("{} - {}".format(title, static.title)),
		html.style(static.style),
	)
	nav = html.nav(html.ul(
		html.li(html.a('⏏', href=html.absolute())),
		html.li(html.a('Reviews', href=html.absolute('reviews'))),
		html.li(html.a('Commits', href=html.absolute('commits', repo.head.ref.name))),
		html.li(html.a('Tree', href=html.absolute('tree', repo.head.ref.name))),
		html.li(html.a('Refs', href=html.absolute('refs'))),
	))
	return html.html(head, html.body(nav, *content))

def get_refs(request, args):
	def get_ref(ref):
		commits = html.a('commits', href=html.absolute('commits', ref.name))
		tree = html.a('tree', href=html.absolute('tree', ref.name))
		return html.tr(html.td(ref.name), html.td(commits), html.td(tree))
		
	return html_page('Refs', html.div(html.table(*map(get_ref, repo.refs), **{'class': 'list'})))

def diff_to_html(diff):
	def diff_lin_to_html(line):
		if len(line) == 0:
			type = ''
		elif line[0] == '+':
			type = 'added'
		elif line[0] == '-':
			type = 'removed'
		elif line[0] == '@':
			type = 'header'
		else:
			type = ''
		return html.tr(html.td(), html.td(line), **{'class': type})
	lines = map(diff_lin_to_html , diff.diff.split('\n'))
	return html.div(html.table(*lines, **{'class': 'diff'}))

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
	ref = repo.refs[ref_name]
	rows = []
	for commit in ref.commit.iter_parents():
		check = html.input(type="checkbox", name=commit.hexsha)
		rows.append(html.tr(html.td(check), html.td(*commit_to_html(commit))))
		if len(rows) > 256:
			break
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

def get_reviews(request, args):
	def review_to_html(r):
		hexsha, review = r
		commits = html.ul(*map(lambda c: html.li(*commit_to_html(repo.commit(c))), review['includedCommits']))
		return html.div(html.h1(html.a(hexsha[0:12], href=html.absolute('review', hexsha))), commits, **{'class': 'review'})
	return html_page('Reviews', *map(review_to_html, db.iterate('open_reviews')))

def get_review(request, args):
	[hexsha] = args
	review = db.get('open_reviews', hexsha)
	base = repo.commit(review['baseCommit'])
	last = repo.commit(review['lastCommit'])
	affectedPaths = set(review['affectedPaths'])
	
	diff = base.diff(last, None, True)
	filtered_diff = filter(lambda d: not diff_to_affected_paths(d).isdisjoint(affectedPaths), diff)
	return html_page('Review {}'.format(hexsha[0:12]), *map(diff_to_html, filtered_diff))

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
	return html.absolute('review', db.add('open_reviews', review))

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
		if len(args)>1:
			rows.append(html.tr(html.td(html.a('..', href='/'+'/'.join(['tree']+args[:1]))), html.td()))
		for d in tree.trees:
			link = html.td(html.a(d.name+'/', href='/'+'/'.join(['tree']+args+[d.name])))
			rows.append(html.tr(link, html.td()))
		for blob in tree.blobs:
			link = html.td(html.a(blob.name, href='/'+'/'.join(['tree']+args+[blob.name])))
			size = html.td(bytes_to_human(blob.size))
			rows.append(html.tr(link, size))
		body = html.table(*rows, **{'class': 'list'})
	return html_page('Tree {} /{}'.format(ref_name, '/'.join(path)), html.div(body))


if __name__ == '__main__':
	http.serve(('localhost', 8080), http.Handler(get_reviews, None,
		review = http.Handler(get_review, None, 
			create= http.Handler(None, post_review_create),
		),
		reviews = http.Handler(get_reviews, None), 
		commit = http.Handler(get_commit, None),
		commits = http.Handler(get_commits, None),
		tree = http.Handler(get_tree, None),
		refs = http.Handler(get_refs, None),
	))

