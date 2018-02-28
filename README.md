# File server
A simple file server for local file sharing for files and directories. When starting the server specific files and directories can be defined to be available for download.

For the download HTTPS is enabled and the HTTP authentication is required. When starting the server a username and password has to be provided. All files and directories selected for download will be zipped in memory and can then be downloaded.

## Encryption
By default the application uses HTTPS and HTTP authentication. The credentials have to be specified when starting the server (a prompt will appear).

In addition, also GPG encryption is available for which the public key has to be send via a POST request (e.g. wget).

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

`https://0.0.0.0:<port>/files/`

or via command line

`wget https://0.0.0.0:<port>/files/ --no-check-certificate --user=<username> --ask-password -O files.zip`

For GPG encryption the public key can be passed with `wget`

`wget https://0.0.0.0:<port>/files/ --no-check-certificate --user=<username> --ask-password -O files.gpg --post-file <public-key>`

#### Requirements
To run the server python3, Flask and Flask HTTP authentication packages must be installed:

`pip3 install -r requirements.txt`
