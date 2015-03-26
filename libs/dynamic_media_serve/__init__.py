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

import os, zlib, rfc822, stat, warnings, urlparse
import time, datetime
import urllib, urllib2

from django.http import Http404, HttpResponse, HttpResponseNotModified
from django.utils.text import compress_string as django_compress_string
from django.views import static as django_static
from django.core.cache import cache
from django.conf import settings

import filter
from filter.default import ContentFile

if hasattr(settings, "CACHE_MIDDLEWARE_SECONDS") :
	CACHE_MIDDLEWARE_SECONDS = settings.CACHE_MIDDLEWARE_SECONDS
else :
	CACHE_MIDDLEWARE_SECONDS = 10

if hasattr(settings, "MAX_FILE_SIZE_COMPRESS") :
	MAX_FILE_SIZE_COMPRESS = settings.MAX_FILE_SIZE_COMPRESS
else :
	MAX_FILE_SIZE_COMPRESS = 1024 * 1000 * 100  # 1M

def serve (request,
			path,					# media path.
			document_root=None,
			show_indexes=False,		# it's for the compatibility with static.serve.
			force_mimetype=None,	# force the specific mime type.
			compress=True,			# compress output content
			update=False,			# don't use cache.
			width=None,				# only for image
			height=None,			# only for image
			use_template=True,		# parse content thru django template.
			improve=True,			# improve image quality.
			mode=None,				# improve image quality.
		) :

	__argument = request.GET.copy()

	if path.startswith("http%3A%2F%2F") or path.startswith("http://") :
		if path.startswith("http%3A%2F%2F") :
			path = urllib.unquote(path)

		fullpath = path
		func_get_media = get_media_external
	else :
		document_root = os.path.abspath(document_root)

		# for multibyte url handling.
		fullpath = os.path.abspath(
			os.path.join(
				document_root,
				"/".join([urllib.unquote(str(i)) for i in path.split("/")]),
			)
		)

		# prevent to follow up the prior directory.
		if not fullpath.startswith(document_root) :
			return HttpResponse("Access Denied", status=401)

		if not os.path.exists(fullpath) :
			raise Http404, "'%s' does not exist" % fullpath

		if os.path.isdir(fullpath) : # DMS does not support directory index page.
			if show_indexes :
				return django_static.serve(request, path=path, document_root=document_root, show_indexes=True, )
			else :
				raise Http404, "Directory indexes are not allowed here."


		func_get_media = get_media_internal

	if __argument.has_key("compress") :
		compress = parse_boolean_query(__argument.get("compress"))

	if __argument.has_key("force_mimetype") :
		force_mimetype = __argument.get("force_mimetype", "").strip()

	if __argument.has_key("width") :
		width = __argument.get("width", None)

	if __argument.has_key("height") :
		height = __argument.get("height", None)

	if __argument.has_key("update") :
		update = parse_boolean_query(__argument.get("update"))

	if __argument.has_key("improve") :
		improve = parse_boolean_query(__argument.get("improve"))

	if __argument.has_key("mode") :
		mode = __argument.get("mode", mode)

	kwargs = {
		"update": update,
		"compress": compress,
		"force_mimetype": force_mimetype,
		"width": width,
		"height": height,
		"improve": improve,
		"mode": mode,
	}

	# for IE series, check 'HTTP_IF_NONE_MATCH' first.
	if not update and \
			request.META.get("HTTP_IF_NONE_MATCH", None) == get_etag(fullpath) :
		return HttpResponseNotModified()
	elif not update and func_get_media == get_media_internal and not was_modified_since(request, fullpath) :
		return HttpResponseNotModified()
	else :
		# check MAX_FILE_SIZE_COMPRESS
		if func_get_media == get_media_internal and os.stat(fullpath)[stat.ST_SIZE] > MAX_FILE_SIZE_COMPRESS :
			compress = None
			kwargs.update({"compress": compress, })

		if not update :
			# We use cache. If you did not enable the caching,
			# nothing will be happended.
			response = cache.get(get_cache_name(request, **kwargs))
			if response :
				return response

	(cf, mimetype, status_code, last_modified, ) = func_get_media(request, fullpath, **kwargs)

	if status_code == 304 :
		return HttpResponseNotModified()

	if compress :
		try :
			compress = list(set([i for i in request.META.get("HTTP_ACCEPT_ENCODING", "").split(",") if i.strip()]) & set(["gzip", "deflate"]))[0]
		except :
			pass

	response = HttpResponse(
		compress and compress_string(cf.read(), compress) or cf.read(),
		mimetype=mimetype,
	)
	response["Last-Modified"] = last_modified
	response["Expires"] = rfc822.formatdate(time.mktime((datetime.datetime.now() + datetime.timedelta(seconds=CACHE_MIDDLEWARE_SECONDS)).timetuple()))
	response["ETag"] = get_etag(fullpath)

	if compress :
		response["Content-Encoding"] = compress

	cache.set(
		get_cache_name(request, **kwargs),
		response,
		CACHE_MIDDLEWARE_SECONDS,
	)

	return response

def parse_boolean_query (s) :
	return s.lower() in ("true", "1", "on", )

def was_modified_since (request, path) :
	statobj = os.stat(path)
	return django_static.was_modified_since(
		request.META.get("HTTP_IF_MODIFIED_SINCE", None),
		statobj[stat.ST_MTIME],
		statobj[stat.ST_SIZE]
	)

def get_cache_name (request, **kwargs) :
	return urllib.quote(
		"%s?%s" % (
			request.META.get("PATH_INFO"),
			"&".join(["%s=%s" % (i, j, ) for i, j in kwargs.items()]),
		),
		"",
	)

def get_etag (path) :
	try :
		mtime = os.stat(path)[stat.ST_MTIME]
	except :
		mtime = time.time()

	return urllib.quote(path + str(mtime), "")

def compress_string (s, mode="gzip") :
	if mode == "gzip" :
		return django_compress_string(s)
	elif mode == "deflate" :
		return zlib.compress(s)
	else :
		return s

def get_media_external (request, path, **kwargs) :
	req = urllib2.Request(path)
	if request.META.get("HTTP_REFERER", None) :
		req.add_header("Referer", request.META.get("HTTP_REFERER"))

	if request.META.get("HTTP_IF_MODIFIED_SINCE", None) :
		req.add_header(
			"If-Modified-Since",
			request.META.get("HTTP_IF_MODIFIED_SINCE")
		)

	if request.META.get("HTTP_IF_NONE_MATCH", None) :
		req.add_header(
			"If-None-Match",
			request.META.get("HTTP_IF_NONE_MATCH")
		)

	try :
		r = urllib2.urlopen(req)
	except urllib2.HTTPError, e :
		return ("", None, e.code, e.headers.getheader("last-modified"), )
	else :
		last_modified = r.headers.getheader("last-modified")
		status_code = r.code

		if status_code != 200 :
			return (
				None,
				r.headers.getheader("content-type"),
				status_code,
				last_modified,
			)

		h = filter.get_mime_handler(
				None,
				mimetype=r.headers.getheader("content-type"),
			)(
				request,
				ContentFile(
					r.read(),
					name=os.path.basename(urlparse.urlsplit(path)[2]),
				),
				**kwargs
			)
		r.close()

		return (h.render(), h.mimetype, status_code, last_modified, )

def get_media_internal (request, path, **kwargs) :
	h = filter.get_mime_handler(path)(
		request,
		ContentFile(file(path, "rb").read(), name=path, ),
		**kwargs
	)

	return (h.render(), h.mimetype, 200, rfc822.formatdate(os.stat(path)[stat.ST_MTIME]), )


"""
Description
-----------


ChangeLog
---------


Usage
-----


"""

__author__ =  "Spike^ekipS <spikeekips@gmail.com>"

