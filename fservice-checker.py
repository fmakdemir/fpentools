#!/usr/bin/env python3
from urllib.parse import urlsplit
import traceback
import sys
import ftplib
from ftplib import FTP

class ServiceChecker(object):
	def __init__(self, host, port):
		self.host = host
		self.port = port

	def check(self):
		return False

class FTPChecker(ServiceChecker):
	def __init__(self, host, port=21):
		super().__init__(host, port)
		print('Init: '+host, port)

	def check(self):
		ftp = FTP(self.host)     # connect to host, default port
		try:
			ftp.connect(self.host, self.port)
			ftp.login() # user anonymous, passwd anonymous@
			ftp.cwd('debian')
			print('Welcome message:', ftp.getwelcome())	# list directory contents
			ftp.retrbinary('RETR README', open('README', 'wb').write)
			ftp.quit()
		except ftplib.error_perm as e:
			print('Anonymous check failed:', e)
		return False

def main():
	import argparse
	parser = argparse.ArgumentParser(description='Spider URLs in given order.\n' +
		'by Fma')
	# urls
	parser.add_argument('urls', metavar='URL', type=str, nargs='+',
						help='Path to spider')
	# verbosity level
	parser.add_argument('--verbose', metavar='INT', type=int,
		help='Verbosity level', default=0)
	parser.add_argument('--out-file', metavar='PATH', type=str,
		help='Output path', default=None)
	parser.add_argument('--no-same-domain', help='spider different domains',
		action='store_false', default=True)

	args = parser.parse_args()
	ftp_checker = FTPChecker(args.urls[0])
	try:
		ftp_checker.check()
	except KeyboardInterrupt:
		print('\n\nUser interrupted canceling and quiting\n\a')

if __name__ == "__main__":
   main()
