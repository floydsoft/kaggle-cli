# Kaggle-CLI
An unofficial Kaggle command line tool.

## Installation
```
$ pip install kaggle-cli
```

## Upgrade
```
$ pip install -U kaggle-cli
```

## Usage
Please note that you **must accept the competition rules** on the competition's page before running your commands.


### Submit
To submit an entry.

```
$ kg submit <submission-file> -u <username> -p <password> -c <competition> -m "<message>"
```

Optionally, add `-z` to zip the submission file before uploading:

```
$ kg submit <submission-file> -u <username> -p <password> -c <competition> -z -m "<message>"
```

### Download
To download the data files (resumable).

```
$ kg download -u <username> -p <password> -c <competition>
```

To download a specific data file.

```
$ kg download -u <username> -p <password> -c <competition> -f train.zip
```

### Submissions
To list submissions.

```
$ kg submissions
```

### Dataset

To download a dataset (resumable).

```
$ kg dataset -u <username> -p <password> -o <owner> -d <dataset>
```

### Config
To set global config.

> Optional: add `-z` to zip submission files before uploading.

```
$ kg config -g -u <username> -p <password> -c <competition>
```

or local config:

```
$ kg config -u <username> -p <password> -c <competition>
```

Show working config:

```
$ kg config
```

### Use Proxy
`$ export HTTPS_PROXY="YOUR_PROXY_URI"`, for example: `$ export HTTPS_PROXY="http://10.10.1.10:1080"`. For Windows user, please set environment variable HTTPS_PROXY accordingly.

## Example
```
$ kg submit sampleSubmission.csv -c titanic-gettingStarted -u USERNAME -p PASSWORD -m "Enter a brief description of this submission here."
```

or

```
$ kg config -c titanic-gettingStarted -u USERNAME -p PASSWORD
$ kg submit sampleSubmission.csv -m "Enter a brief description of this submission here."
```
