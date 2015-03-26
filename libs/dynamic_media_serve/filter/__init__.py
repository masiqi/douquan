# -*- coding: utf-8 -*-
"""
 Copyright 2005 Spike^ekipS <spikeekips@gmail.com>

	This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import re, os, mimetypes

MAP_MIMETYPE = (
	(r"^image\/svg",		"svg", ),
	(r"^image\/",			"image", ),
	(r"^text\/css$",		"css", ),
	(r"^text\/javascript$",	"javascript", ),
	(".*",					"default", ),
)

__map_mimetype = list()
for (i, j, ) in MAP_MIMETYPE :
	try :
		handler = __import__("%s" % j, globals(), None).Handler
	except Exception, e :
		handler = __import__("default", globals(), None).Handler

	__map_mimetype.append((re.compile(i), handler, ), )

HANDLER_MIMETYPE_DEFAULT = __import__("default", globals(), None).Handler
MAP_MIMETYPE = __map_mimetype

def get_mime_handler (filepath, mimetype=None) :
	if not mimetype :
		mimetype = mimetypes.guess_type(os.path.basename(filepath))[0]

	if mimetype is not None :
		for (k, handler, ) in MAP_MIMETYPE :
			if k.findall(mimetype) :
				return handler

	return HANDLER_MIMETYPE_DEFAULT


"""
Description
-----------


ChangeLog
---------


Usage
-----


"""

__author__ =  "Spike^ekipS <spikeekips@gmail.com>"
__version__=  "0.1"
__nonsense__ = ""




