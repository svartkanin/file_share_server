from flask import Flask, jsonify, make_response, send_file, request
from flask_httpauth import HTTPBasicAuth
import sys
import argparse
import gnupg
import re
import getpass
import zipfile
from io import BytesIO
import os
import time


app = Flask(__name__)
auth = HTTPBasicAuth()


class Encryption(object):
	"""
		Encryption container wrapper for public key import and zip file encryption
	"""
	def __init__(self):
		self._gpg = gnupg.GPG()
		self._fingerprint = None

	def import_key(self, key):
		"""
			Import the GPG public key and store the fingerprint
		:param key: Public GPG key
		"""
		res = self._gpg.import_keys(key)

		if res.results and res.results[0]:
			self._fingerprint = res.results[0]['fingerprint']

	def has_fingerprint(self):
		"""
			Check if a fingerprint for encryption is present
		:return: True if a fingerprint is set, otherwise False
		"""
		return self._fingerprint is not None

	def encrypt_zip(self, zip_file):
		"""
			Encrypt a given zip file
		:param zip_file: MemoryZip object to be encrypted
		:return: ByteIO of encrypted data
		"""
		enc_data = self._gpg.encrypt_file(zip_file.get_zip_file(), self._fingerprint, always_trust=True)
		self._fingerprint = None
		return BytesIO(enc_data.data)


class MemoryZip(object):
	"""
		In memory zip file container
	"""
	def __init__(self):
		self._memory_zip = BytesIO()

	def add_files(self, files):
		"""
			Add a list of files to a zip archive
		:param files: List of files on disk
		"""
		with zipfile.ZipFile(self._memory_zip, 'a') as zf:
			for file in files:
				with open(file.name, 'r') as fp:
					data = zipfile.ZipInfo(file.name)
					data.date_time = time.localtime(time.time())[:6]
					data.compress_type = zipfile.ZIP_DEFLATED
					zf.writestr(data, fp.read())

	def add_directories(self, directories):
		"""
			Add a list of directories to a zip archive
		:param directories: List of directories on disk
		"""
		with zipfile.ZipFile(self._memory_zip, 'a', compression=zipfile.ZIP_DEFLATED) as zf:
			for directory in directories:
				for root, dirs, files in os.walk(directory):
					for f in files:
						fullpath = os.path.join(root, f)
						archive_name = os.path.join(root, f)
						zf.write(fullpath, archive_name, zipfile.ZIP_DEFLATED)
		
	def get_zip_file(self):
		"""
			Retrieve the in memory zip file
		:return: BytesIO of the zip file
		"""
		self._memory_zip.seek(0)
		return self._memory_zip


@auth.get_password
def get_password(username):
	"""
		Get password for corresponding user
	:param username: The username received from a request
	:return: Password corresponding to the user or None
	"""
	creds = app.config['auth'].split(':')
	if username == creds[0]:
		return creds[1]
	return None


@auth.error_handler
def unauthorized():
	"""
		On error display Unauthorized access
	:return: HTTP response for unauthorized access
	"""
	return make_response(jsonify({'error': 'Unauthorized access'}), 401)


@app.route('/files/', methods=['GET', 'POST'])
@auth.login_required
def get_file():
	"""
		URL entry point to retrieve the requested files
	:return: return a HTTP response with the requested files
	"""
	enc = Encryption()

	if request.method == 'POST':
		if request.form:
			enc = process_gpg_key(request.form, enc)

	zipfile = create_zip(app.config['files'], app.config['dirs'], enc)
	return send_file(zipfile, as_attachment=True, attachment_filename='files.zip', mimetype="application/zip")


def prepare_form_data(data):
	"""
		The received public key got a bit messed up when sent so lets fix that
	:param data: Request form data
	:return: Pretty formatted public key
	"""
	prefix = '-----BEGIN PGP PUBLIC KEY BLOCK-----'
	suffix = '-----END PGP PUBLIC KEY BLOCK-----'

	data = data.to_dict()
	data = ''.join(data.keys()) + '=' + ''.join(data.values())
	data = re.split(prefix + '|' + suffix, data)
	key = prefix + ''.join(data).replace(' ', '+') + suffix
	return str.encode(key)


def process_gpg_key(data, enc):
	"""
		Process the received POST request data
	:param data: Request POST form
	:param enc: Encryption object
	:return: Encryption object
	"""
	key = prepare_form_data(data)	
	enc.import_key(key)
	return enc
		

def create_zip(files, directories, enc):
	"""
		Create a in memory zip file
	:param files: List of files
	:param directories: List of directories
	:param enc: Encryption object
	:return: ByteIO zip file stream
	"""
	zip_file = MemoryZip()

	if files:
		zip_file.add_files(files)
	if directories:
		zip_file.add_directories(directories)

	if enc.has_fingerprint():
		return enc.encrypt_zip(zip_file)

	return zip_file.get_zip_file()


def get_args():
	"""
		Create argument parser
	:return: ArgumentParser object
	"""
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--files', required=False, type=argparse.FileType('r'), nargs='+')
	parser.add_argument('-d', '--directories', nargs='+', required=False)
	parser.add_argument('-p', '--port', required=False, default='5000')
	args = parser.parse_args()
	return args


def main():
	args = get_args()

	if args.files or args.directories:
		username = input('Username: ')
		pwd = getpass.getpass('Password: ')
		pwd2 = getpass.getpass('Re-enter: ')
		
		if pwd != pwd2:
			print("Passwords don't match")
			sys.exit()

		app.config['auth'] = username + ':' + pwd
		app.config['files'] = args.files
		app.config['dirs'] = args.directories

		app.run(host='0.0.0.0', ssl_context='adhoc', port=int(args.port), debug=True)
	else:
		print("No files/directories specified!")


if __name__ == '__main__':
	main()
