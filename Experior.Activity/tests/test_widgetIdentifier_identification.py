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
