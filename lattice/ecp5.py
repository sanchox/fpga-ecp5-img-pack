"""
Script to pack .sea and .sed files into .img

This script packs algo file (.sea) and data file (.sed) into a single image
file (.img)

"""

from __future__ import print_function

import argparse
import struct
import platform
import datetime
import getpass
import hashlib
import subprocess

info = '''
################################
image packed {datetime}
by {user}@{host}
git description: {git}
algo sha256: {algo_hash}
data sha256: {data_hash}
extra info: {extra}
################################
'''

def _parse_args(git_label):
	# instance CLI argument parser
	parser = argparse.ArgumentParser(
		 description='Make .img file from .sea and .sed files '
			     'for ecp5-fpga-mgr driver')

	input_files_group = parser.add_argument_group('input files (mandatory)',
		'binary file\'s generated by Lattice Diamond')

	# configuring argument parser to instance file objects directly by file
	# paths from the CLI
	input_files_group.add_argument('-a', '--algo-file', metavar='FILE',
		dest='algo',
		required=True,
		type=argparse.FileType('rb'),
		help='algo file (usually .sea)')

	input_files_group.add_argument('-d', '--data-file', metavar='FILE',
		dest='data',
		required=True,
		type=argparse.FileType('rb'),
		help='data file (usually .sed)')

	output_files_group=parser.add_argument_group('ouput files')
	# optional arguments
	output_files_group.add_argument('-i', '--image-file', metavar='FILE',
		type=argparse.FileType('wb'),
		default='ecp5_sspi_fw.img',
		help='result image file name (usually .img)')

	info_group=parser.add_argument_group('addditional info',
		'Additional data appended to image')
	info_group.add_argument('-g', '--git-label',
		default=git_label, help='git label string')

	info_group.add_argument('-e', '--extra-info',
		help='extra text info to be appended to img')

	parser.add_argument('-v', '--verbose', action='store_true',
		help='be verbose and show appending info')

	return parser.parse_args()

def _pack():
	# get git description string from latest tag and commit
	_git_label = subprocess.check_output(
		["git", "describe", "--always", "--long"]
		).strip().decode("utf-8")

	# parsing args
	args = _parse_args(_git_label)

	# get file contents
	algo = args.algo.read()
	data = args.data.read()

	# calculate lengths
	algo_size = len(algo)
	data_size = len(data)

	# packing into a single byte array representing `struct lattice_fpga_sspi_firmware`
	# http://repo.ddg/common/sys/drivers/grif-drivers/blob/develop/ecp5_fpga_mgr/main.c#L26
	# plus additional information:
	#     hostname
	#     datetime
	#     git commit hash, if passed
	img = struct.pack('<II{}s{}s'.format(algo_size, data_size), algo_size, data_size, algo, data)

	# additional info for identifying build artifacts
	_datetime = datetime.datetime.utcnow()
	_user = getpass.getuser()
	_host = platform.node()
	_host_detail = platform.uname()
	_algo_hash = hashlib.sha256(algo).hexdigest()
	_data_hash = hashlib.sha256(data).hexdigest()

	global info 
	# pack additional info into one string
	info = info.format(
		datetime=_datetime,
		user=_user,
		host=_host,
		git=args.git_label,
		algo_hash=_algo_hash,
		data_hash=_data_hash,
		extra=args.extra_info)
	
	if args.verbose:
		print(info)

	# put image to file
	args.image_file.write(img)
	# append info string
	args.image_file.write(info.encode())
	# and close
	args.image_file.close()

if __name__ == "__main__":
	_pack()

