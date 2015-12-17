Sublime-Text-3-pydocstring
==========================

a Sublime Text 3 plugin to automatic generate docstring for module/class/function

docstring.py
============

docstring.py is a python docstring plugin, you can use this plugin to generate docstring
for the module, class or function automatically.

Installation
------------
Copy **[docstring.py](https://github.com/xaedes/Sublime-Text-3-pydocstring/blob/master/docstring.py)** into
your ST2 User packages folder *(Sublime Text 3 > Preferences > Browse Packages... > User)*

Usage
-----
Click on the position you want to generate docstring, but do not select anything, you could
define key bindings or menu entries to use this plugin easy and quick

I've added this to my User Key Bindings:

     {"keys": ["ctrl+alt+s"], "command": "docstring"}

...and this to Context.sublime-menu, which allow context menu access:

     { "command": "docstring", "caption": "Generate Docstring"}

![module screenshop](https://github.com/xaedes/Sublime-Text-3-pydocstring/raw/master/module_docstring.PNG)

![class screenshop](https://github.com/xaedes/Sublime-Text-3-pydocstring/raw/master/class_docstring.PNG)

![function screenshop](https://github.com/xaedes/Sublime-Text-3-pydocstring/raw/master/function_docstring.PNG)
