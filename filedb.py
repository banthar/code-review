#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import hashlib
import os

class FileDb():
	def __init__(self, root):
		self.root = root

	def get_store(self, store):
		store_path = os.path.join(self.root, store)
		try:
			os.makedirs(store_path)
		except OSError:
			pass
		return store_path

	def add(self, store, data):
		s = json.dumps(data)
		hash = hashlib.sha1(s).hexdigest()
		with open(os.path.join(self.get_store(store), hash),'wb') as f:
			f.write(s)
		return hash

	def get(self, store, hexsha):
		path = os.path.join(self.get_store(store), hexsha)
		with open(path) as f:
			return json.load(f)

	def iterate(self, store):
		store_path = self.get_store(store)
		return map(lambda hexsha: (hexsha, self.get(store, hexsha)), os.listdir(store_path))

