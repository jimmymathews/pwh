#!/usr/bin/python

class debug_logger:

	def __init__(self):
		self.message = "Start of log.\n"

	def log(self,new_message):
		if type(new_message) is not list:
			self.message = self.message + new_message + "\n"
		else:
			for m in new_message:
				self.message = self.message + "  " + m + "\n"

	def dump(self):
		print self.message

d = debug_logger()

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
							"character limit"	: self.int0(line[1].strip()),
							"letter minimum"	: self.int0(line[2].strip()),
							"numeral minimum"	: self.int0(line[3].strip()),
							"capital minimum"	: self.int0(line[4].strip()),
							"symbol minimum"	: self.int0(line[5].strip()),
							"expiration"		: line[6].strip(),
							"manual appendage"	: line[7].strip()}
				self.accounts.append(rule_list)
			for rule_list in self.accounts:
				self.account_names.append(rule_list["account"])
			d.log("Account names:")
			d.log(self.account_names)
			self.default_rules = self.accounts[0]
		except:
			self.default_rules = 	{"account":"default",
						"character limit"       : 15,
						"letter minimum"        : 0,
						"numeral minimum"       : 0,
						"capital minimum"       : 0,
						"symbol minimum"        : 0,
						"expiration"            : "",
						"manual appendage"      : ""}

	def int0(self,input):
		try:
			return int(input)
		except:
			return 0

	def get_rules(self, n):
		return self.accounts[self.account_names.index(n)]


import time
import hashlib
class hasher:

	def __init__(self, input):
		self.buffer = input

	def set_rules(self, r):
		self.rules = r
		d.log("Using rules for " + r["account"] + ".")

	def apply_input_mask(self):
		copy = self.buffer
		r = self.rules
		d.log("Applying input mask.")

		if(r["expiration"] in ["daily", "day"]):
			copy = copy + time.strftime("%d/%m/%Y")
			d.log("Daily expiration.")
		if(r["expiration"] in ["monthly", "month"]):
			copy = copy + time.strftime("%m/%Y")
			if time.strftime("%d") == "01":
				print(r["account"]+" password changed today.")
			d.log("Monthly expiration.")
		if(r["expiration"] in ["yearly", "year"]):
			copy = copy + time.strftime("%Y")
			if time.strftime("%d%m") == "0101":
				print(r["account"]+" password changed today.")
			d.log("Yearly expiration.")

		if r["manual appendage"] != "":
			d.log("Adding manual appendage for account " + name + ".")
			copy = copy + r["manual appendage"]

		self.buffer = copy

	def apply_output_mask(self):
		r = self.rules
		copy = self.buffer

		if r["character limit"] > 0:
			copy = copy[:r["character limit"]]
		else:
			copy = copy[:15]

		l = self.lower_count(copy)
		u = self.upper_count(copy)
		if self.letter_count(copy) != (l + u): 
			d.log("Alphabetical character count failed.")
		n = self.numeral_count(copy)
		s = self.symbol_count(copy)	#always zero?

		#enforce letter min
		letter_defect = r["letter minimum"] - l - u
		if letter_defect > 0:
			list_version = list(copy)
			switched_count = 0
			for i in range(len(copy)):
				if not list_version[i].isalpha() and switched_count<letter_defect:
					list_version[i] = "a"
					switched_count = switched_count + 1
			copy = "".join(list_version)

		#enforce numeral min
		numeral_defect = r["numeral minimum"] - n
		if numeral_defect > 0:
			list_version = list(copy)
			switched_count = 0
			for i in range(len(copy)):
				if list_version[i] not in ["1","2","3","4","5","6","7","8","9","0"] and switched_count<numeral_defect:
					list_version[i] = "6"
					switched_count = switched_count + 1
			copy = "".join(list_version)
		
		#enforce capital min
		capital_defect = r["capital minimum"] - u
		if capital_defect > 0:
			list_version = list(copy)
			switched_count = 0
			for i in range(len(copy)):
				if list_version[i].islower() and switched_count < capital_defect:
					list_version[i] = list_version[i].upper()
					switched_count = switched_count + 1
			copy = "".join(list_version)

		#enforce symbol min
		symbol_defect = r["symbol minimum"] - s
		if symbol_defect > 0:
			list_version = list(copy)
			switched_count = 0
			for i in range(len(copy)):
				if list_version[len(copy)-1-i] not in ["!","@","#","$","%","^","&","*","(",")"] and switched_count < symbol_defect:
					list_version[len(copy)-1-i] = ["!","@","#","$","%","^","&","*","(",")"][(len(copy)-1-i) % 10]
					switched_count = switched_count + 1
			copy = "".join(list_version)

		self.buffer = copy

	def hash(self):
		self.buffer = hashlib.sha512(self.buffer).hexdigest()

	def output(self):
		return self.buffer

	def letter_count(self,input):
		count=0
		for char in input:
			if char.isalpha():
				count += 1
		return count

	def lower_count(self,input):
		count=0
		for char in input:
			if char.isalpha() and char.islower():
				count += 1
		return count

	def upper_count(self,input):
		count=0
		for char in input:
			if char.isalpha() and char.isupper():
				count += 1
		return count

	def numeral_count(self,input):
		count=0
		for char in input:
			if char in ["1","2","3","4","5","6","7","8","9","0"]:
				count += 1
		return count

	def symbol_count(self,input):
		count=0
		for char in input:
			if char in ["!","@","#","$","%","^","&","*","(",")"]:
				count += 1
		return count


import getpass

os.system('clear')
c = clipper()
s = account_settings(".accounts.csv")

while True:
	name = raw_input()
	if name in ["q","quit","exit"]:
		break
	h = hasher(getpass.getpass("")+name)
	print '\033[F\033[F'

	d.log("Account name is " + name + ".")

	if name in s.account_names:
		h.set_rules(s.get_rules(name))
	else:
		h.set_rules(s.default_rules)

	h.apply_input_mask()
	h.hash()
	h.apply_output_mask()

	if c.clipboard_function != "none":
		c.clip(h.output())
		thread.start_new_thread(c.delayed_clear, (5,) )	#erased after 5 seconds (change this for different delay amounts)
	else:
		print h.output()

if c.clipboard_function != "none":
	c.clear()

#d.dump()	#uncomment this to see debugging output
