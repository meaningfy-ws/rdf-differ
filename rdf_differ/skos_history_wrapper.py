"""
skos_history_wrapper.py
Date: 06/07/2020
Author: Mihai Coșleț
Email: coslet.mihai@gmail.com
"""
import os
from pathlib import Path
from shutil import copy
from urllib.parse import urljoin

from rdflib.util import guess_format

from rdf_differ import defaults
from rdf_differ.defaults import PUT_URI_BASE, QUERY_URI_BASE
from rdf_differ.utils import INPUT_MIME_TYPES, dir_exists, dir_is_empty


class SKOSHistoryFolderSetUp:
    def __init__(self, dataset: str, alpha_file: str, beta_file: str, root_path: str):
        self.dataset = dataset
        self.alpha_file = alpha_file
        self.beta_file = beta_file
        self.root_path = root_path

        self._check_root_path()

    def generate(self):
        v1 = Path(self.root_path) / self.dataset / 'data' / 'v1'
        v2 = Path(self.root_path) / self.dataset / 'data' / 'v2'
        v1.mkdir(parents=True)
        v2.mkdir(parents=True)

        copy(self.alpha_file, v1 / 'file.rdf')
        copy(self.beta_file, v2 / 'file.rdf')

    # TODO: decide if this functionality should remain in the class
    def _check_root_path(self):
        if dir_exists(self.root_path):
            if not dir_is_empty(self.root_path):
                raise Exception('Root path is not empty.')
        else:
            Path(self.root_path).mkdir()


class SKOSHistoryRunner:
    """

    """

    def __init__(self, dataset: str, scheme_uri: str, versions: list,
                 config_template_location: str = '../templates/template.config'):
        self.config_template = self._read_file(config_template_location)
        self.dataset = dataset
        self.scheme_uri = scheme_uri
        self.versions = versions

        self.basedir = None
        self.filename = None
        self.endpoint = None

        self._read_envs()

    @property
    def put_uri(self) -> str:
        """
        Build the PUT URI
        :return: str
            PUT URI
        """
        return urljoin(self.endpoint, '/'.join([self.dataset, PUT_URI_BASE]))

    @property
    def update_uri(self) -> str:
        """
        Build the update URI
        :return: str
            UPDATE URI
        """
        return urljoin(self.endpoint, self.dataset)

    @property
    def query_uri(self) -> str:
        """
        Build the query URI
        :return: str
            query URI
        """
        return urljoin(self.endpoint, '/'.join([self.dataset, QUERY_URI_BASE]))

    @property
    def input_file_mime(self) -> str:
        file_format = guess_format(self.filename, INPUT_MIME_TYPES)
        if file_format is None:
            raise Exception('File type not supported.')

        return file_format

    def generate(self):
        return self.config_template.format(
            dataset=self.dataset,
            scheme_uri=self.scheme_uri,
            versions='({} {})'.format(*self.versions),
            basedir=self.basedir,
            filename=self.filename,
            put_uri=self.put_uri,
            update_uri=self.update_uri,
            query_uri=self.query_uri,
            input_type=self.input_file_mime
        )

    def _read_envs(self):
        """
        Method for reading properties for the skos-history bash config file.
        :return:
        """
        self.basedir = os.environ.get('BASEDIR', defaults.BASEDIR)
        self.filename = os.environ.get('FILENAME', defaults.FILENAME)
        self.endpoint = os.environ['ENDPOINT']

    @staticmethod
    def _read_file(relative_location):
        location = Path(__file__).parent / relative_location
        with open(location, 'r') as file:
            content = file.read()
        return content
