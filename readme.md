###Password Hash (paranoid version, password never stored even as a local variable)

This script is a simple, unusual password manager. You only need to remember one master password, and it is never stored for more than a second.

1. Run the Python script *password.py* in a terminal emulator. (If you'd like, you can change the name).
2. Enter a string describing the account that the password is for, like *gmail* or *bankofamerica*.
3. Enter your master password.
4. The two are hashed, and if desired, character limits are imposed and symbols added or subtracted to meet the account provider's requirements.
5. The result is copied to the system clipboard, if possible, then erased in 5 seconds. Otherwise it is printed to the terminal.

###Setting password rules for an account

List the password limitations in the file "accounts.csv", in the format:

	name, character max, letter min, numeral min, capital min, symbol min, expiration, manual appendage
	default,        100,           ,           5,          10,           ,     yearly,
	gmail,            8,           ,            ,            ,           ,           ,


* *name*  
The name of the website or provider, e.g. *gmail*.

* *character max* (number or blank)  
Limits the number of characters in the final output.		

* *letter min* (number or blank)  
Tries to ensure a minimum number of letter characters in the final output.

* *numeral min* (number or blank)  
Tries to ensure a minimum number of numerals in the final output.

* *capital min* (number or blank)  
Tries to ensure a minimum number of capital letter characters in the final output.

* *symbol min* (number or blank)  
Tries to ensure a minimum number of symbol characters (those arising as shift modifications of a numeral) in the final output.

* *expiration* ("weekly", "monthly", "yearly")  
Appends a string identifying the week/month/year prior to the hash.

* *manual appendage* (string)  
Appends the string prior to the hash. For manual "versions". 

###How it looks

	$ ./password.py

The screen clears.

	$ gmail
	$ 

Your typed password doesn't appear on the screen.  
If *xclip*, or *clipit* are not found, the hash prints:

	$ gmail
	$ d644d4c2d9e3c49

To exit, use *q*, *quit*, or *exit*:

	$ q

###Notes

* *xclip* is the recommended clipboard manager for this script.

* If using *clipit*, clipboard synchronization is recommended. Otherwise program control of the primary clipboard is limited; it can be difficult to erase the passwords that are copied to the clipboard.
