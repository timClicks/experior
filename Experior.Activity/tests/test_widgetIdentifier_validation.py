#! /usr/env/bin python

# test_widgetIdentifier_validation tests that the validators work correctly.
# designed to be used with py.test
import gtk

from sys import path
path.append('..')

import widgetIdentifier

W = widgetIdentifier.WidgetIdentifier(gtk.Label())

def test_none_fails():
    assert not W.validateIdentifier(None)

def test_str_passes():
    assert W.validateIdentifier('should be fine')

def test_unicode_passes():
    assert W.validateIdentifier(u'should be fine')

def test_empty_string_fails():
    assert not W.validateIdentifier('')

def test_unwanted_prefixes_fail():
    for prefix in W.dontWantPrefixes:
        assert not W.validateIdentifier(prefix + "fail me")

def test_unwanted_widgets_fail():
    for widg in W.dontWant:
        assert not W.validateIdentifier(widg)
