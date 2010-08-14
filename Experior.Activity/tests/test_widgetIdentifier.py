from widgetIdentifier import *

class test_widgetIdentifier:
	def __init__(self):
		self.is_setup = False
		
	def setUp(self):
		assert not self.is_setup
		
		self.widget = gtk.Button()
		self.name	= "nameExample"
		
		self.widget.set_name(self.name)
		
		self.identifier = widgetIdentifier(self.widget)
		
		self.is_setup = True
		
	def tearDown(self):
		assert self.is_setup
		self.is_setup = False
		
	def test_init(self):
		assert self.identifier._widget == self.widget
		
	def test_getIdentifier(self):
		assert self.identifier.getIdentifier() == self.name
		
	def test_checkStoredIdentifier(self):
		assert not self.identifier.checkStoredIdentifier()
		
	def test_setIdentifier(self):
		assert not self.identifier.setIdentifier("GtkAnything")
	
		name = "x"
		assert self.identifier.setIdentifier(name) == name
		
	def test_setWidget(self):
		self.identifier.setWidget(None)
		assert not self.identifier.getIdentifier()
		
		widget  = gtk.Label("")
		name	= "asdf"
		widget.set_name(name)
		assert not self.identifier.getIdentifier() == name
		
		self.identifier.setWidget(widget)
		assert self.identifier.getIdentifier() == name
		
	def test_getStoredIdentifier(self):
		assert not self.identifier.getStoredIdentifier() == self.name
		
		self.identifier.getIdentifier()
		assert self.identifier.getStoredIdentifier() == self.name
		
		name = "x"
		self.identifier.setIdentifier(name)
		assert self.identifier.getStoredIdentifier() == name
		
	def test_validateIdentifier(self):
		assert not self.identifier.validateIdentifier(None)
		assert not self.identifier.validateIdentifier("")
		assert not self.identifier.validateIdentifier(1)
		assert not self.identifier.validateIdentifier("GtkAnything")
		assert not self.identifier.validateIdentifier("SugarToggleToolButton")
		assert self.identifier.validateIdentifier("ValidName")
		
class test_buttonIdentifier:
	def __init__(self):
		self.is_setup = False
		
	def setUp(self):
		assert not self.is_setup
		
		self.name	= "nameExample"
		self.widget = gtk.Button()
		
		self.identifier = buttonIdentifier(self.widget)
		
		self.is_setup = True
		
	def tearDown(self):
		assert self.is_setup
		self.is_setup = False
		
	def test_init(self):
		assert not self.identifier.getIdentifier()
		
	def test_getIdentifier1(self):	
		self.widget.set_label(self.name)
		assert self.identifier.getIdentifier() == self.name
	
	def test_getIdentifier2(self):
		self.widget.set_name(self.name)
		assert self.identifier.getIdentifier() == self.name
		
class test_toolButtonIdentifier:
	def __init__(self):
		self.is_setup = False
		
	def setUp(self):
		assert not self.is_setup
		
		self.name	= "nameExample"
		self.widget = gtk.ToolButton()
		
		self.identifier = toolButtonIdentifier(self.widget)
		
		self.is_setup = True
		
	def tearDown(self):
		assert self.is_setup
		self.is_setup = False
	
	def test_init(self):
		assert not self.identifier.getIdentifier()

	def test_getIdentifier1(self):
		self.widget.set_name(self.name)
		assert self.identifier.getIdentifier() == self.name

	def test_getIdentifier2(self):
		self.widget.set_label(self.name)	
		assert self.identifier.getIdentifier() == self.name
	
	def test_getIdentifier3(self):
		self.widget.set_icon_name(self.name)
		assert self.identifier.getIdentifier() == self.name

	def test_getIdentifier4(self):
		label = gtk.Label(self.name)
		self.widget.set_label_widget(label)
		assert self.identifier.getIdentifier() == self.name
		
class test_comboBoxIdentifier:
	def __init__(self):
		self.is_setup = False
		
	def setUp(self):
		assert not self.is_setup
		
		self.name	= "nameExample"
		self.widget = gtk.ComboBox()
		
		self.identifier = comboBoxIdentifier(self.widget)
		
		self.is_setup = True
		
	def tearDown(self):
		assert self.is_setup
		self.is_setup = False
	
	def test_init(self):
		assert not self.identifier.getIdentifier()

	def test_getIdentifier1(self):
		self.widget.set_name(self.name)
		assert self.identifier.getIdentifier() == self.name

	def test_getIdentifier2(self):
		self.widget.set_title(self.name)
		assert self.identifier.getIdentifier() == self.name
		
class test_entryIdentifier:
	def __init__(self):
		self.is_setup = False

	def setUp(self):
		assert not self.is_setup

		self.name	= "nameExample"
		self.widget = gtk.Entry()

		self.identifier = entryIdentifier(self.widget)

		self.is_setup = True

	def tearDown(self):
		assert self.is_setup
		self.is_setup = False

	def test_init(self):
		assert not self.identifier.getIdentifier()

	def test_getIdentifier1(self):
		self.widget.set_name(self.name)
		assert self.identifier.getIdentifier() == self.name

	def test_getIdentifier2(self):
		self.widget.set_text(self.name)
		assert self.identifier.getIdentifier() == self.name

# class test_paletteIdentifier:
# 	def __init__(self):
# 		self.is_setup = False
# 
# 	def setUp(self):
# 		assert not self.is_setup
# 
# 		self.name	= "nameExample"
# 		# self.widget = gtk.Entry()
# 		self.widget = Palette(self.name)
# 
# 		self.identifier = paletteIdentifier(self.widget)
# 
# 		self.is_setup = True
# 
# 	def tearDown(self):
# 		assert self.is_setup
# 		self.is_setup = False
# 
# 	def test_init(self):
# 		assert self.identifier.getIdentifier()
# 
# 	def test_getIdentifier1(self):
# 		otherName = "someOtherName"
# 		self.widget.set_name(otherName)
# 		assert self.identifier.getIdentifier() == otherName
# 
# 	def test_getIdentifier2(self):
# 		assert self.identifier.getIdentifier() == self.name

class test_toolComboBoxIdentifier:
	def __init__(self):
		self.is_setup = False

	def setUp(self):
		assert not self.is_setup

		self.name	= "nameExample"
		self.widget = ToolComboBox()
		self.widget.set_property('label-text', self.name)

		# Set the widget later...
		self.identifier = toolComboBoxIdentifier(None)

		self.is_setup = True

	def tearDown(self):
		assert self.is_setup
		self.is_setup = False
		
	def test_getIdentifier1(self):
		otherName = "someOtherName"
		self.widget.set_name(otherName)
		self.identifier.setWidget(self.widget)
		assert self.identifier.getIdentifier() == otherName

	def test_getIdentifier2(self):
		self.identifier.setWidget(self.widget)
		assert self.identifier.getIdentifier() == self.name

if __name__ == "__main__":
    unittest.main()
