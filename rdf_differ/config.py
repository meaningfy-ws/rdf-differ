"""
config.py
Date: 20/07/2020
Author: Mihai Coșleț
Email: coslet.mihai@gmail.com
"""
import os


def get_envs() -> dict:
    return {
        'basedir': os.environ.get('BASEDIR', './basedir'),
        'filename': os.environ.get('FILENAME', 'file'),
        'endpoint': os.environ['ENDPOINT']
    }