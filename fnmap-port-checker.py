#!/usr/bin/env python3.5
import sys
import libnmap

class DEBUG(object):
	VERBOSE=3
	DEBUG=2
	INFO=1
	QUIET=-1

class FPortChecker(object):

	def __init__(self):
		super()



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

	parser.add_argument('--no-same-domain', help='spider different domains',
		action='store_false', default=True)



if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print('\n\nUser interrupted canceling and quiting\n\a')


