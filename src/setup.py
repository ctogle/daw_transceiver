#!/usr/bin/python
from os.path import isfile, join
import glob
import os
import re

import appdirs

from setuptools import setup#, Extension

import pdb

if isfile("MANIFEST"):
    os.unlink("MANIFEST")

TOPDIR = os.path.dirname(__file__) or "."
#VERSION = re.search('__version__ = "([^"]+)"',
#	open(TOPDIR + "/src/pkg1/__init__.py").read()).group(1)
VERSION = '1.0'

core_modules = [
	'modular_dt.libdawcommander', 
	'modular_dt.libsignaler', 
	'modular_dt.libinstruction', 
	'modular_dt.libsorter', 

	'modular_dt.gui.libqtgui_daw_transceiver', 
				]

def ignore_res(f):
	#if f.startswith('__') or f.startswith('_.'): return True
	#else: return False
	if f.endswith('daw_transceiver_settings.txt'): return False
	else: return True

res_dir = 'modular_dt/resources/'
res_fis = [f for f in os.listdir(os.path.join(
	os.getcwd(), 'modular_dt', 'resources')) 
			if not ignore_res(f)]
res_files = [res_dir + f for f in res_fis]

requirements = [
	'modular_core >= 1.0', 
			]

setup(
	name="modular_daw_transceiver-pkg",
	version = VERSION,
	description = "modular daw transceiver pkg",
	author = "ctogle",
	author_email = "cogle@vt.edu",
	url = "http://github.com/ctogle/daw_transceiver",
	license = "MIT License",
	long_description =
"""\
This is the daw transceiver program of modular
""",
	#install_requires = requirements, 
	#scripts = [], 
	packages = ['modular_dt', 'modular_dt.gui'], 
	py_modules = core_modules, 
	zip_safe = False,
	data_files=[(os.path.join(appdirs.user_config_dir(), 
		    'modular_resources'), res_files)], 
	)

