import time
import logging

sugarActivityName = 'Calculate'

def sugarbot_main(widgets):
	# Test 'selected' functionality.
	assert widgets['Share with:'].selected == "Private"
	widgets['Share with:'].selected = "My Neighborhood"
	assert widgets['Share with:'].selected == "My Neighborhood"

	# Test widget fetching/assignment
	one 	= widgets['1']
	plus 	= widgets['+']
	enter 	= widgets['enter']
	
	for i in range(0,5):
		# Test click
		one.click()
		plus.click()
		one.click()
		
		# Test Entry text assignment
		assert widgets['TextEntry'].text == '1+1'
		
		enter.click()
		
		assert len(widgets['TextEntry'].text) == 0
		
		time.sleep(1)
	
	# More Entry text assignment
	widgets['TextEntry'].text = "1+5"
	assert widgets['TextEntry'].text == '1+5'
	enter.click()
