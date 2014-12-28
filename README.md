autofritz
=========

Command line script to control call forwarding on AVM Fritz!Box 7490

This Python script lets you turn on and off preconfigured call forwarding (call deflection, call diversion) settings
on an AVM Fritz!Box 7490. You can use it to control your Fritz!Box from a cron job or other event.
It uses web scraping parsing the HTML and Javascript output of the Fritz!Box.

Usage
-----
Preset call deflection on your Fritz!Box using its web interface. Configure one or more settings.
Set your Fritz!Box password in autofritz.py.
After that you can use autofritz:

to query the current state of call deflection:
`./autofritz.py`

to turn off call all preconfigured settings for call deflection:
`./autofritz.py -r`

to turn on settings 0 and 1 of call deflection:
`./autofritz.py -r0 -r1`


Requirements:

* Python 2.7
* lxml
* requests

autofritz makes use of jsparser.py from the PyNarcissus package.

