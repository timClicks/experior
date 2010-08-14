import time
import logging

sugarActivityName = 'Terminal'

def sugarbot_main(widgets):
	#assert 1
	term = widgets['VteTerminal']
	term.typeText("whoami\r")
	term.typeText("ls -la\r")
	term.typeText("exit\r")