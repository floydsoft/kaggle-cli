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
        parser.add_argument('-z', '--zip', type=self._str2bool, nargs='?', const=True, default=False,
                            help='zip the submission file before uploading')

        return parser

    def take_action(self, parsed_args):
        config = get_final_config(parsed_args)

        username = config.get('username', '')
        password = config.get('password', '')
        competition = config.get('competition', '')
        zip = config.get('zip', False)

        browser = common.login(username, password)
        base = 'https://www.kaggle.com'
        competition_url = '/'.join([base, 'c', competition])
        file_form_submit_url = '/'.join([base, 'blobs/inbox/submissions'])
        entry_form_submit_url = '/'.join([competition_url, 'submission.json'])

        entry = parsed_args.entry
        message = parsed_args.message

        archive_name = Submit._rand_str(10)+'.zip'

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
            file_form_submit_url,
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

        browser.post(
            entry_form_submit_url,
            data=json.dumps({
                'blobFileTokens': [token],
                'submissionDescription': message if message else ''
            }),
            headers={
                'Content-Type': 'application/json'
            }
        )

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
    def _str2bool(v):
        """
        parse boolean values

        https://stackoverflow.com/a/43357954/436721
        :return:
        """
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise ArgumentTypeError('Boolean value expected.')

    @staticmethod
    def _rand_str(length):
        return uuid.uuid4().hex[:length-1]
