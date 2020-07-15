#!/usr/bin/python

import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter import StringVar
import csv
import pyperclip

class PasswordCalculator:
    def __init__(self):
        self.window = tk.Tk()
        mp = simpledialog.askstring(title="Key", prompt="", parent=self.window)
        self.window.title("Password Calculator")
        self.table = AccountTable(self.window, mp)
        self.table.pack()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()
    
    def on_closing(self):
        pyperclip.copy("")
        self.window.destroy()
        
class AccountTable:
    def __init__(self, parent, mp):
        self.mp = mp
        # self.tree = ttk.Treeview(parent)
        # self.tree['height'] = 15
        self.account_lister = AccountLister()
        # for i,name in enumerate(self.account_lister.account_names):
        #     self.tree.insert('', i, name, text=name, values=[name])
        self.account = StringVar()
        self.combobox = ttk.Combobox(parent, textvariable=self.account, values=self.account_lister.account_names, state="readonly", width=50)
        # self.combobox['state']

        # self.tree['selectmode'] = ["browse"]
        # self.tree.bind("<ButtonRelease-1>", self.click_table_entry)
        self.combobox.bind("<<ComboboxSelected>>", self.click_entry)

        self.hasher = Hasher()

    # def click_table_entry(self, event):
    def click_entry(self, event):
        # if len(self.tree.selection()) == 0:
        #     return
        # input_id = self.tree.selection()[0]
        # name = input_id
        name = self.account.get()

        rules = self.account_lister.get_rules(name)
        self.hasher.update_buffer(self.mp+rules["account"])
        self.hasher.set_rules(rules)
        self.hasher.apply_input_mask()
        self.hasher.hash()
        self.hasher.apply_output_mask()
        pyperclip.copy(self.hasher.output())

    def pack(self):
        # self.tree.pack()
        self.combobox.pack()
        # self.tree.grid(column=0, row=0) #, sticky=("n","s","e","w")


class AccountLister:
    def __init__(self):
        filename=".accounts.csv"
        self.account_names = []
        self.accounts = []
        self.default_rules = []
        try:
            reader = csv.reader(open(filename))
            next(reader)
            for line in reader:
                if len(line)>0:
                    rule_list = {"account"      : line[0].strip(),
                            "character limit"   : self.int0(line[1].strip()),
                            "letter minimum"    : self.int0(line[2].strip()),
                            "numeral minimum"   : self.int0(line[3].strip()),
                            "capital minimum"   : self.int0(line[4].strip()),
                            "symbol minimum"    : self.int0(line[5].strip()),
                            "expiration"        : line[6].strip(),
                            "manual appendage"  : line[7].strip()}
                self.accounts.append(rule_list)
            # indexed_names = [[row["account"], i] for i,row in enumerate(self.accounts)]
            ss = sorted(self.accounts, key= lambda x: x["account"])
            self.accounts = ss
            for rule_list in self.accounts:
                self.account_names.append(rule_list["account"])
            self.default_rules = self.accounts[0]
        except Exception as e:
            print(e)
            exit()

    def int0(self,input):
        try:
            return int(input)
        except:
            return 0

    def get_rules(self, n):
        return self.accounts[self.account_names.index(n)]

    def get_account_names(self):
        return self.account_names

import hashlib
class Hasher:
    def __init__(self):
        self.update_buffer("")

    def update_buffer(self, input):
        self.buffer = input

    def set_rules(self, r):
        self.rules = r
        
    def apply_input_mask(self):
        copy = self.buffer
        r = self.rules
        copy = copy + r["manual appendage"]
        # if(r["expiration"] in ["daily", "day"]):
        #     copy = copy + time.strftime("%d/%m/%Y")
        # if(r["expiration"] in ["monthly", "month"]):
        #     copy = copy + time.strftime("%m/%Y")
        #     if time.strftime("%d") == "01":
        #         print(r["account"]+" password changed today.")
            
        # if(r["expiration"] in ["yearly", "year"]):
        #     copy = copy + time.strftime("%Y")
        #     if time.strftime("%d%m") == "0101":
        #         print(r["account"]+" password changed today.")
            
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
        s = self.symbol_count(copy) #always zero?

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
        self.buffer = hashlib.sha512(self.buffer.encode('utf-8')).hexdigest()

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

pc = PasswordCalculator()
