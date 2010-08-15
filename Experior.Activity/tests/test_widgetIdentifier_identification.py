#! /usr/env/bin python

# test_widgetIdentifier_validation tests that the validators work correctly.
# designed to be used with py.test
import gtk

from sys import path
path.append('..')

from widgetIdentifier import *

L = gtk.Label('Test subject')

def test_label_matches():
    W = WidgetIdentifier(L)
    assert W.getIdentifier() == 'Test subject'

L2 = gtk.Label('Test subject')
L2.set_name('1')
def test_set_name_matches():
    W = WidgetIdentifier(L2)
    assert W.getIdentifier() == '1'


B = ButtonIdentifier(gtk.Button('Stop'))
def test_button_id():
    assert B.getIdentifier() == 'Stop'

def test_button_id_sub():
    assert B.getIdentifierSub() == 'Stop'

def test_toolbutton_no_label():
    tb = gtk.ToolButton('stock_id_1')
    assert ToolButtonIdentifier(tb).getIdentifier() == 'stock_id_1'

def test_toolbutton_with_label():
    tb = gtk.ToolButton('stock_id_2')
    tb.set_label('Start')
    assert ToolButtonIdentifier(tb).getIdentifier() == 'Start'

def test_toolbutton_with_label_widget():
    tb = gtk.ToolButton('stock_id_3')
    label = gtk.Label('Starting now')
    tb.set_label_widget(label)
    assert ToolButtonIdentifier(tb).getIdentifier() == 'Starting now'

def test_toolbutton_with_icon_name():
    tb = gtk.ToolButton('stock_id_2')
    tb.set_icon_name('Start')
    assert ToolButtonIdentifier(tb).getIdentifier() == 'Start'

def test_toolbutton_with_icon_widget():
    tb = gtk.ToolButton('stock_id_3')
    ico = gtk.Label('Starting now')
    tb.set_icon_widget(ico)
    assert ToolButtonIdentifier(tb).getIdentifier() == 'Starting now'

def test_toolbutton_label_priority():
    tb = gtk.ToolButton('stock_id')
    tb.set_label('Start')
    tb.set_icon_name('Stop')
    assert ToolButtonIdentifier(tb).getIdentifier() == 'Start'
