#!/usr/bin/python

import os
import subprocess
import thread
import time
class clipper:

	def __init__(self):
		self.clipboard_function = "none"
		DEVNULL = open(os.devnull, "w");
		try:
			subprocess.check_call(["clipit","-h"], stdout=DEVNULL, stderr=DEVNULL)
			self.clipboard_function = "clipit"
		except:
			pass
		try:
			subprocess.check_call(["xclip", "-h"], stdout=DEVNULL, stderr=DEVNULL)
			self.clipboard_function = "xclip"
		except:
			pass

	def clip(self,str):
		if self.clipboard_function == "clipit":
			subprocess.check_call(["clip_scripts/custom_clipit", str])
			return
		if self.clipboard_function == "xclip":
			subprocess.call(["clip_scripts/custom_xclip", str])
			return

	def clear(self):
		self.clip("cleared")

	def delayed_clear(self, amount):
		time.sleep(amount)
		self.clear()


import csv
class account_settings:

	def __init__(self, filename):
		self.account_names = []
		self.accounts = []
		self.default_rules = []
		try:
			reader = csv.reader(open(filename))
			reader.next()
			for line in reader:
				if len(line)>0:
					rule_list =	{"account"		: line[0].strip(),
							"character limit"	: int0(line[1].strip()),
							"character minimum"	: int0(line[2].strip()),
							"letter minimum"	: int0(line[3].strip()),
							"capital minimum"	: int0(line[4].strip()),
							"symbol minimum"	: int0(line[5].strip()),
							"expiration"		: line[6].strip(),
							"manual appendage"	: line[7].strip()}
				self.accounts.append(rule_list)
			for rule_list in self.accounts:
				self.account_names.append(rule_list["account"])
			self.default_rules = self.accounts[0]
		except:
			self.default_rules = 	{"account":"default",
						"character limit":15,
						"character minimum"     : 6,
						"letter minimum"        : 0,
						"capital minimum"       : 0,
						"symbol minimum"        : 0,
						"expiration"            : "",
						"manual appendage"      : ""}

	def int0(input):
		try:
			return int(input)
		except:
			return 0

	def get_rules(self, n):
		return self.accounts[self.account_names.index(n)]


import hashlib
class hasher:

	def __init__(self, input):
		self.buffer = input

	def set_rules(self, r):
		self.rules = r

	def apply_input_mask(self):
		copy = self.buffer
		#...act on copy, using rules
		self.buffer = copy

	def apply_output_mask(self):
		character_limit = self.rules["character limit"]
		if character_limit > 0:
			copy = self.buffer[:character_limit]
		self.buffer = copy

	def hash(self):
		self.buffer = hashlib.sha512(self.buffer).hexdigest()

	def output(self):
		return self.buffer


import getpass

os.system('clear')
c = clipper()
settings = account_settings(".accounts.csv")

while True:
	name = raw_input()
	if name in ["q","quit","exit"]:
		c.clear()
		break
	h = hasher(getpass.getpass("")+name)
	print '\033[F\033[F'

	if name in settings.account_names:
		h.set_rules(settings.get_rules(name))
	else:
		h.set_rules(settings.default_rules)

	h.apply_input_mask()
	h.hash()
	h.apply_output_mask()

	if c.clipboard_function != "none":
		c.clip(h.output())
		thread.start_new_thread(c.delayed_clear, (5,) )
	else:
		print h.output()


