#!/usr/bin/env python3.5
import requests
import re
from urllib.parse import urlsplit
import traceback
import sys

class DEBUG(object):
	VERBOSE=3
	DEBUG=2
	INFO=1
	QUIET=-1


class UrlParser(object):
	# anchor finder regexp
	URL_RE = re.compile(r'<a href="([^"]*)"', re.I)
	# protocol checker regexp
	PROT_RE = re.compile(r'^https?://', re.I)
	# href directive finder (tel:, mailto:, sms: etc)
	HREF_DIR_RE = re.compile(r'(tel|mailto|sms|callto|file|ftp):', re.I)

	# add this too?
	# r'https?://[^"]*\.[^"]*'

	@staticmethod
	def _fetch_html(url):
		# TODO: add force untrusted ssl support
		# r = requests.head(url, allow_redirects=True, verify=False)
		r = requests.head(url, allow_redirects=True, timeout=30)
		r.raise_for_status()
		if r.headers['Content-Type'].startswith('text/'):
			r = requests.get(url, allow_redirects=True, timeout=30)
			return r.text
		return ''

	@staticmethod
	def _get_base_url(url):
		return "{0.scheme}://{0.netloc}".format(urlsplit(url))

	@staticmethod
	def _get_domain(url):
		# return '.'.join(urlsplit(url).netloc.split('.')[-2:])
		return urlsplit(url).netloc

	@classmethod
	def parse(cls, top_url, url_map=[], same_domain=True):
		if not cls.PROT_RE.search(top_url):
			top_url = 'http://' + top_url
		base_url = cls._get_base_url(top_url)
		base_domain = cls._get_domain(base_url)
		html = cls._fetch_html(top_url)
		for match in cls.URL_RE.finditer(html):
			url = match.group(1).strip()
			pos = url.find('#')
			if pos > -1:
				url = url[:pos]
			# skip empty urls
			if len(url) == 0:
				continue
			# skip unwanted protocols
			if cls.HREF_DIR_RE.search(url):
				continue

			if not cls.PROT_RE.search(url):
				if url[0] != '/':
					url = '/' + url
				url = base_url + url
			# print(base_domain, cls._get_domain(url))
			if (url not in url_map and (not same_domain
				or base_domain == cls._get_domain(url))):

				url_map.append(url)

		return url_map

class FSpider(object):

	def __init__(self, urls):
		super()
		self.urls = urls
		self._verbose = DEBUG.INFO
		self._out_path = False

	def verbosity(self, val=None):
		if type(val) == int:
			self._verbose = val
		return self._verbose

	def same_domain(self, val=None):
		if type(val) == bool:
			self._same_domain = val
		return self._same_domain

	def output_file(self, val=None):
		if type(val) == str:
			self._out_path = val
		return self._out_path

	def spidey(self):
		out = False
		if self._out_path:
			try:
				out = open(self._out_path, 'w')
			except:
				traceback.print_exc(file=sys.stdout)

		for url in self.urls:
			if not UrlParser.PROT_RE.search(url):
				url = 'http://' + url

			try:
				r = requests.head(url, allow_redirects=True)
				r.raise_for_status()
				url = r.url
			except HTTPError:
				print('Can\'t reach skipping:', url)
				continue

			url = url.strip('/')

			print('Spidering: ', url)
			visited = [] # visited map
			url_map = [url]
			to_visit = [url]
			while len(to_visit) > 0:
				try:
					url = to_visit.pop()
					print('Trying:', url, '\tstatus:', end='')
					if out:
						print(url, file=out)
					url_map = UrlParser.parse(url, url_map, self._same_domain)
					visited.append(url)
					for u in url_map:
						if u not in visited and u not in to_visit:
							to_visit.append(u)
					if self._verbose >= DEBUG.VERBOSE:
						print('url_map:', url_map, len(url_map))
						print('visited:', visited, len(visited))
						print('to_visit:', to_visit, len(to_visit))
					print('SUCCESS')
				except requests.HTTPError:
					if url not in visited:
						visited.append(url)
					print('FAIL')
				except requests.ConnectionError:
					print('CONNECTION_FAIL!\a')
					if self._verbose >= DEBUG.VERBOSE:
						print ('-'*30)
						traceback.print_exc(file=sys.stdout)
						print ('-'*30)
		if out:
			out.close()

def main():
	import argparse
	parser = argparse.ArgumentParser(description='Spider URLs in given order.\n' +
		'by Fma')
	# urls
	parser.add_argument('urls', metavar='URL', type=str, nargs='+',
						help='Path to spider')
	# verbosity level
	parser.add_argument('-v', '--verbose', metavar='INT', type=int,
		help='Verbosity level', default=0)
	parser.add_argument('-o', '--output-file', metavar='PATH', type=str,
		help='Output path', default=None)
	parser.add_argument('--no-same-domain', help='spider different domains',
		action='store_false', default=True)

	args = parser.parse_args()
	spider = FSpider(args.urls)
	spider.same_domain(args.no_same_domain)
	spider.verbosity(args.verbose)
	spider.output_file(args.output_file)
	try:
		spider.spidey()
	except KeyboardInterrupt:
		print('\n\nUser interrupted. Canceling and quiting\n\a')

if __name__ == "__main__":
   main()
