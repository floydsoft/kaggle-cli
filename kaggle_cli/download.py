import os
import re

from cliff.command import Command

from . import common
from .config import get_final_config

import progressbar
from contextlib import closing

class Download(Command):
    'Download data files from a specific competition.'

    def get_parser(self, prog_name):
        parser = super(Download, self).get_parser(prog_name)

        parser.add_argument('-c', '--competition', help='competition')
        parser.add_argument('-u', '--username', help='username')
        parser.add_argument('-p', '--password', help='password')
        parser.add_argument('-f', '--filename', help='filename')

        return parser

    def take_action(self, parsed_args):
        config = get_final_config(parsed_args)

        username = config['username']
        password = config['password']
        competition = config['competition']
        file_name = parsed_args.filename

        browser = common.login(username, password)
        base = 'https://www.kaggle.com'
        data_url = '/'.join([base, 'c', competition, 'data'])

        data_page = browser.get(data_url)

        data = str(data_page.soup)
        links = re.findall('"url":"(/c/'+competition+'/download/[^"]+)"', data)

        for link in links:
            url = base + link
            if file_name is None or url.endswith('/' + file_name):
                self.download_file(browser, url)

    def download_file(self, browser, url):
        self.app.stdout.write('downloading %s\n' % url)
        local_filename = url.split('/')[-1]
        headers = {}
        done = False
        file_size = 0
        total_size = 0

        bar = progressbar.ProgressBar()
        content_length = int(
            browser.request('head', url).headers.get('Content-Length')
        )

        if os.path.isfile(local_filename):
            file_size = os.path.getsize(local_filename)
            if file_size < content_length:
                headers['Range'] = 'bytes={}-'.format(file_size)
            else:
                done = True

        self.bytes = file_size
        widgets = [local_filename, ' ', progressbar.Percentage(), ' ',
                  progressbar.Bar(marker="#"), ' ',
                  progressbar.ETA(), ' ', progressbar.FileTransferSpeed()]

        if file_size == content_length:
            print('{} already downloaded !'.format(local_filename))
            return local_filename
        elif file_size > content_length :
            print("Something wrong here, Incorrect file !")
            return
        else :
            bar = progressbar.ProgressBar(widgets=widgets, 
                                          maxval=content_length).start()
            if not self.bytes:
                bar.update(self.bytes)

        if not done:
            stream = browser.get(url, stream=True, headers=headers)
            if not self.is_downloadable(stream):
                warning = ("Warning: download url for file %s resolves to an html document rather than a downloadable file. \n"
                            "See the downloaded file for details. Is it possible you have not accepted the competition's rules on the kaggle website?") % local_filename
                self.app.stdout.write(warning+"\n")
            with open(local_filename, 'ab') as f:
                for chunk in stream.iter_content(chunk_size=1024, decode_unicode=True):
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
                        self.bytes += len(chunk)
                        bar.update(self.bytes)
            bar.finish()

    def is_downloadable(self, response):
        """
        Checks whether the response object is a html page or a likely downloadable file.
        Intended to detect error pages or prompts such as kaggle's competition rules acceptance prompt.

        Returns True if the response is a html page. False otherwise.
        """
        content_type = response.headers.get('Content-Type', "")
        content_disp = response.headers.get('Content-Disposition', "")
        if "text/html" in content_type and not "attachment" in content_disp:
            # This response is a html file which is not marked as an attachment,
            # so we likely hit a rules acceptance prompt
            return False
        return True

class Dataset(Download):
    'Download dataset from a specific user.'

    def get_parser(self, prog_name):
        parser = super(Dataset, self).get_parser(prog_name)
        parser.add_argument('-d', '--dataset', help='dataset')
        parser.add_argument('-o', '--owner', help='owner')
        return parser

    def take_action(self, parsed_args):
            if not self.is_downloadable(stream):
                warning = ("Warning: download url for file %s resolves to an html document rather than a downloadable file. \n"
                            "See the downloaded file for details. Is it possible you have not accepted the competition's rules on the kaggle website?") % local_filename
                self.app.stdout.write(warning+"\n")
            with open(local_filename, 'ab') as f:
                for chunk in stream.iter_content(chunk_size=1024, decode_unicode=True):
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)

    def is_downloadable(self, response):
        """
        Checks whether the response object is a html page or a likely downloadable file.
        Intended to detect error pages or prompts such as kaggle's competition rules acceptance prompt.

        Returns True if the response is a html page. False otherwise.
        """
        content_type = response.headers.get('Content-Type', "")
        content_disp = response.headers.get('Content-Disposition', "")
        if "text/html" in content_type and not "attachment" in content_disp:
            # This response is a html file which is not marked as an attachment,
            # so we likely hit a rules acceptance prompt
            return False
        return True

class Dataset(Download):
    'Download dataset from a specific user.'

    def get_parser(self, prog_name):
        parser = super(Dataset, self).get_parser(prog_name)
        parser.add_argument('-d', '--dataset', help='dataset')
        parser.add_argument('-o', '--owner', help='owner')
        return parser

    def take_action(self, parsed_args):
        config = get_final_config(parsed_args)

        username = config['username']
        password = config['password']
        dataset = parsed_args.dataset
        owner = parsed_args.owner
        file_name = parsed_args.filename

        browser = common.login(username, password)
        base = 'https://www.kaggle.com'
        data_url = '/'.join([base, owner, dataset])

        data_page = browser.get(data_url)

        data = str(data_page.soup)
        links = re.findall('"url":"(/'+owner+'/'+dataset+'/downloads/[^"]+)"', data)

        for link in links:
            url = base + link
            if file_name is None or url.endswith('/' + file_name):
                self.download_file(browser, url)
