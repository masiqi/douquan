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

import os, mimetypes, warnings
from StringIO import StringIO
from django.template import Template, RequestContext

class Handler (object) :

	def __init__ (self, request, cf, **kwargs) :
		self.cf = cf
		self.request = request
		self.kwargs = kwargs
		if kwargs.get("force_mimetype", None) :
			self.mimetype = kwargs.get("force_mimetype", "")
		else :
			self.mimetype = mimetypes.guess_type(os.path.basename(cf.name))[0]

	def render (self) :
		return self.cf

class ContentFile (StringIO) :

	def __init__ (self, content, name=None) :
		StringIO.__init__(self, content)
		self.name = name

	def read (self, size=None) :
		o = StringIO.read(self, size)

		if not size :
			self.seek(0)

		return o

# parse template thru django template.
def get_rendered_to_string (request, cf) :
	try :
		t = Template(cf.read())
		return ContentFile(t.render(RequestContext(request)), name=cf.name)
	except Exception, e :
		if settings.DEBUG :
			warnings.warn("[EE]%s" % e, RuntimeWarning)

		return cf



"""
Description
-----------


ChangeLog
---------


Usage
-----


"""

__author__ =  "Spike^ekipS <spikeekips@gmail.com>"




