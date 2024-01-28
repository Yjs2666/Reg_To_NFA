# Reg_To_NFA

prerequisite:
Download graphviz to your local device. More details: https://graphviz.org/download/

alternative:
Print out the the NFA by uncomment third last line of the code "print(nfa)". Then copy and paste the Dictionary to any online graphviz website. 

First part:
You can change the input string under the Main function: example: 
	reg_exp = "a(a+b)*b"
	#reg_exp = "(a+ab)(a*+b)"
An invalid input string will not be accepted(a printed message saying Invalid Input. Such as "a(a+b#$%@235)*b"

Bonus Question:
def in_language (nfa, s):
The "s" should change by the user.
Example: if your string is reg_exp = "(a+b)*", then your "s" should be change to 'ab' or anythings else that you would like to test out.

