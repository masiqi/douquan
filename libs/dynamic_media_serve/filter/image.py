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

import warnings
from django.conf import settings
import default
import lib_image

if hasattr(settings, "DEFAULT_IMAGE_RENDER_MODE") :
	DEFAULT_IMAGE_RENDER_MODE = settings.DEFAULT_IMAGE_RENDER_MODE
else :
	DEFAULT_IMAGE_RENDER_MODE = "ratio"

class Handler (default.Handler) :
	def __init__ (self, request, cf, **kwargs) :
		super(Handler, self).__init__(request, cf, **kwargs)

		self.mode = kwargs.get("mode", DEFAULT_IMAGE_RENDER_MODE, )
		self.update = kwargs.get("update", False)
		self.improve = kwargs.get("improve", True)

		try :
			self.width = int(kwargs.get("width", None))
		except :
			self.width = None
		else :
			self.width = (self.width > 0) and self.width or None

		try :
			self.height = int(kwargs.get("height", None))
		except :
			self.height = None
		else :
			self.height = (self.height > 0) and self.height or None

	def render (self) :
		if self.width or self.height :
			try :
				return lib_image.resize_image(
					self.cf,
					(self.width, self.height, ),
					mode=self.mode,
					improve=self.improve,
				)
			except Exception, e :
				if settings.DEBUG :
					warnings.warn("[EE] %s" % e, RuntimeWarning)

		return self.cf


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






