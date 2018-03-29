# transport.py by @nieltg

from cStringIO import StringIO
from thrift.transport import TTransport

from httplib import HTTP_PORT, HTTPConnection, HTTPS_PORT, HTTPSConnection
from os.path import basename
from sys import argv
from urllib import quote
from urlparse import urlparse
from warnings import warn


class THttpPersist (TTransport.TTransportBase):
	"""Http (keep-alive) implementation of TTransport base."""

	def __init__ (self, uri_or_host, port=None, path=None):
		"""THttpPersist supports two different types constructor parameters.
		THttpPersist(host, port, path) - deprecated
		THttpPersist(uri)
		Only the second supports https.
		"""
		if port is not None:
			warn (
				"Please use the THttpPersist('http://host:port/path') syntax",
				DeprecationWarning,
				stacklevel=2)
			self.host = uri_or_host
			self.port = port
			assert path
			self.path = path
			self.scheme = 'http'
		else:
			parsed = urlparse(uri_or_host)
			self.scheme = parsed.scheme
			assert self.scheme in ('http', 'https')
			if self.scheme == 'http':
				self.port = parsed.port or HTTP_PORT
			elif self.scheme == 'https':
				self.port = parsed.port or HTTPS_PORT
			self.host = parsed.hostname
			self.path = parsed.path
			if parsed.query:
				self.path += '?%s' % parsed.query
		self._bufr = StringIO()
		self._bufw = StringIO()
		self._conn = None
		self._timeout = None
		self._headers = None
	def open (self):
		if self._conn is not None:
			self.close()
		if self.scheme == 'http':
			self._conn = HTTPConnection (
			  self.host, self.port, timeout=self._timeout)
		else:
			self._conn = HTTPSConnection (
			  self.host, self.port, timeout=self._timeout)

	def close (self):
		if self._conn is None:
			return
		self._conn.close ()
		self._conn = None

	def isOpen (self):
		return self._conn is not None

	def setTimeout (self, ms):
		if ms is None:
			self._timeout = None
		else:
			self._timeout = ms / 1000.0
		# TODO: close connection to apply timeout

	def setCustomHeaders (self, headers):
		self._headers = headers

	def read (self, sz):
		return self._bufr.read (sz)

	def write (self, buf):
		self._bufw.write (buf)

	def flush (self):
		if not self.isOpen ():
			self.open ()

		# Pull data out of buffer
		data = self._bufw.getvalue ()
		self._bufw = StringIO ()

		# HTTP request
		self._conn.putrequest ('POST', self.path)

		# Write headers
		self._conn.putheader ('Host', self.host)
		self._conn.putheader ('Content-Type', 'application/x-thrift')
		self._conn.putheader ('Content-Length', str (len (data)))

		if not self._headers or 'User-Agent' not in self._headers:
			user_agent = 'Python/THttpClient'
			script = basename (argv[0])
			if script:
				user_agent = '%s (%s)' % (user_agent, quote(script))
			self._conn.putheader ('User-Agent', user_agent)

		if self._headers:
			for key, val in self._headers.iteritems ():
				self._conn.putheader (key, val)

		self._conn.endheaders ()

		# Write payload
		self._conn.send (data)

		# Get reply to flush the request
		response = self._conn.getresponse ()
		
		self.code = response.status
		self.message = response.reason
		self.headers = response.msg
		self._bufr = StringIO (response.read())
        
        