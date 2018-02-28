# File server
A simple server for file and directory sharing. When starting the server specific files and directories can be defined to be made available for download.

For the download by default HTTPS is enabled and HTTP authentication is required. When starting the server a username and password prompt appears. All selected files and directories for download will be zipped and optionally encrypted.

## Encryption
By default the application uses HTTPS and HTTP authentication. The credentials have to be specified when starting the server (a prompt will appear).

In addition, GPG encryption is available for which the public key has to be send via a POST request (e.g. wget).

## Usage
Starting the server

```
usage: app.py [-h] [-f FILES [FILES ...]] [-d DIRECTORIES [DIRECTORIES ...]] [-p PORT]

optional arguments:
  -h, --help            show this help message and exit
  -f FILES [FILES ...], --files FILES [FILES ...]
  -d DIRECTORIES [DIRECTORIES ...], --directories DIRECTORIES [DIRECTORIES ...]
  -p PORT, --port PORT
```

Accessing the data via the brower 

`https://<ip>:<port>/files/`

or via command line

`wget https://<ip>:<port>/files/ --no-check-certificate --user=<username> --ask-password -O files.zip`

For GPG encryption the public key can be passed with `wget`

`wget https://<ip>:<port>/files/ --no-check-certificate --user=<username> --ask-password -O files.gpg --post-file <public-key-file>`

#### Requirements
To run the server python3, Flask and Flask HTTP authentication packages must be installed:

`pip3 install -r requirements.txt`
