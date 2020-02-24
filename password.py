#!/usr/bin/python

import os
import subprocess
import thread
import time
from sys import platform

class clipper:
	def __init__(self):
		ascertain_platform()
		ascertain_clipboard_functionality()

	def ascertain_platform():
		if platform == "linux" or platform == "linux2":
			self.platform = "linux"
		elif platform == "darwin":
			self.platform = "osx"
		elif platform == "win32":
			self.platform = "win32"
			print("Windows not supported yet.")
			exit()

	def ascertain_clipboard_functionality():
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

	def clip(self,string):
		if self.platform == "osx":
			p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
			p.stdin.write(string)
			p.stdin.close()
			retcode = p.wait()
			return

		if self.platform == "linux":
			if self.clipboard_function == "clipit":
				subprocess.check_call(["clip_scripts/custom_clipit", string])
				return
			if self.clipboard_function == "xclip":
				subprocess.call(["clip_scripts/custom_xclip", string])
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

	def get_account_names(self):
		return self.account_names


import time
import hashlib
class hasher:

	def __init__(self, input):
		self.buffer = input

	def set_rules(self, r):
		self.rules = r
		

	def apply_input_mask(self):
		copy = self.buffer
		r = self.rules
		
		copy = copy + r["manual appendage"]

		if(r["expiration"] in ["daily", "day"]):
			copy = copy + time.strftime("%d/%m/%Y")
			
		if(r["expiration"] in ["monthly", "month"]):
			copy = copy + time.strftime("%m/%Y")
			if time.strftime("%d") == "01":
				print(r["account"]+" password changed today.")
			
		if(r["expiration"] in ["yearly", "year"]):
			copy = copy + time.strftime("%Y")
			if time.strftime("%d%m") == "0101":
				print(r["account"]+" password changed today.")
			

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
		# if self.letter_count(copy) != (l + u): .... then "Alphabetical character count failed."
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



from cursesmenu import *
from cursesmenu.items import *
import getpass

os.system('clear')
c = clipper()
s = account_settings(".accounts.csv")

gp = getpass.getpass("")

def calculate_password(r):
	h = hasher(gp+r["account"])
	h.set_rules(r)
	h.apply_input_mask()
	h.hash()
	h.apply_output_mask()
	c.clip(h.output())

menu = CursesMenu()
for name in s.account_names:
	function_item = FunctionItem(name, calculate_password, [s.get_rules(name)])
	menu.append_item(function_item)
menu.show()
c.clear()

