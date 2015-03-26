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

import mimetypes
import image
import lib_svg
import default

class Handler (default.Handler) :

	def __init__ (self, request, cf, **kwargs) :
		super(Handler, self).__init__(request, cf, **kwargs)

		try :
			self.convert = mimetypes.guess_extension(kwargs.get("force_mimetype", "").strip()).split(".")[1]
		except :
			self.convert = None

	def render (self) :
		if self.convert not in ("png", "jpg", "gif", ) :
			return self.cf
		else :
			try :
				s = lib_svg.SVG(self.cf)
				output = s.render(
					outputtype=self.convert,
					width=self.kwargs.get("width", None),
					height=self.kwargs.get("height", None),
				)

				img = image.Handler(self.request, output, **self.kwargs)
				return img.render()
			except Exception, e :
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






