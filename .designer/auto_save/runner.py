__author__ = 'ethan'

import os
import os.path
import subprocess

# os.chdir(os.path.join(os.path.curdir, 'kivi_test01'))
py_file = "/Applications/Kivy.app/Contents/Resources/kivy/examples/widgets/lists/list_simple.py"

py_file = "main.py"

kivy_thread = subprocess.Popen("/usr/local/bin/kivy '%s'" % py_file, shell=True)
kivy_thread.wait()
