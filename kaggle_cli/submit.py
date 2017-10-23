import os
import time
import re
import json
import uuid
from argparse import ArgumentTypeError
import zipfile

from cliff.command import Command

from . import common
from .config import get_final_config


class Submit(Command):
    'Submit an entry to a specific competition.'

    def get_parser(self, prog_name):
        parser = super(Submit, self).get_parser(prog_name)

        parser.add_argument('entry', help='entry file')

        parser.add_argument('-m', '--message', help='message')
        parser.add_argument('-c', '--competition', help='competition')
        parser.add_argument('-u', '--username', help='username')
        parser.add_argument('-p', '--password', help='password')
        parser.add_argument('-z', '--zip', help='zip the submission file before uploading?', action='store_true')

        return parser

    def take_action(self, parsed_args):
        config = get_final_config(parsed_args)

        username = config.get('username', '')
        password = config.get('password', '')
        competition = config.get('competition', '')
        zip_flag = config.get('zip', 'no')

        zip = Submit._str2bool(zip_flag)

        browser = common.login(username, password)
        base = 'https://www.kaggle.com'
        competition_url = '/'.join([base, 'c', competition])
        file_form_url = '/'.join([base, 'blobs/inbox/submissions'])
        entry_form_url = '/'.join([competition_url, 'submission.json'])

        entry = parsed_args.entry
        message = parsed_args.message

        archive_name = Submit._make_archive_name(entry)

        # print(archive_name)
        # print(zip)
        #
        # return

        if zip:
            with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(entry)

        competition_page = browser.get(competition_url)

        if competition_page.status_code == 404:
            print('competition not found')
            return

        team_id = re.search(
            '"team":{"id":(?P<id>\d+)',
            str(competition_page.soup)
        ).group(1)

        if zip:
            target_name = archive_name
        else:
            target_name = entry

        form_submission = browser.post(
            file_form_url,
            data={
                'fileName': target_name,
                'contentLength': os.path.getsize(target_name),
                'lastModifiedDateUtc': int(os.path.getmtime(target_name) * 1000)
            }
        ).json()

        file_submit_url = base + form_submission['createUrl']

        with open(target_name, 'rb') as submission_file:
            token = browser.post(
                file_submit_url,
                files={
                    'file': submission_file
                }
            ).json()['token']

        entry_form_resp_message = browser.post(
            entry_form_url,
            data=json.dumps({
                'blobFileTokens': [token],
                'submissionDescription': message if message else ''
            }),
            headers={
                'Content-Type': 'application/json'
            }
        ).json()['pageMessages'][0]

        if entry_form_resp_message['type'] == 'error':
            print(entry_form_resp_message['dangerousHtmlMessage'])
            return

        status_url = (
            'https://www.kaggle.com/'
            'c/{}/submissions/status.json'
            '?apiVersion=1&teamId={}'.format(competition, team_id)
        )

        while True:
            time.sleep(1)
            status = browser.get(status_url).json()
            if status['submissionStatus'] == 'pending':
                continue
            elif status['submissionStatus'] == 'complete':
                print(status['publicScoreFormatted'])
                break
            else:
                print('something went wrong')
                break

        if zip:
            os.remove(target_name)

    @staticmethod
    def _make_archive_name(original_file_path):
        # if original name already has a suffix (csv,txt,etc), remove it
        extension_pattern = r'(^.+)\.(.+)$'

        # file may be in another directory
        original_basename = os.path.basename(original_file_path)

        if re.match(extension_pattern,original_basename):
            archive_name = re.sub(extension_pattern,r'\1.zip',original_basename)
        else:
            archive_name = original_basename+".zip"

        # this is used to prevent caching issues
        string_prefix = uuid.uuid4().hex[:4]

        prefixed_archive_name = string_prefix+"-"+archive_name

        original_directory_path = os.path.dirname(original_file_path)

        return os.path.join(original_directory_path,prefixed_archive_name)

    @staticmethod
    def _str2bool(v):
        """
        parse truthy/falsy strings into booleans
        https://stackoverflow.com/a/43357954/436721
        :param v: the string to be parsed
        :return: a boolean value
        """
        if v is True or v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v is False or v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise ArgumentTypeError('Boolean value expected.')
