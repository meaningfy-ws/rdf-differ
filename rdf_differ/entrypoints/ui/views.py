#!/usr/bin/python3

# views.py
# Date:  17/09/2020
# Author: Mihai Coșleț
# Email: coslet.mihai@gmail.com

"""
UI pages
"""
import logging
import tempfile
from pathlib import Path

from flask import render_template, redirect, flash, url_for, send_from_directory

from rdf_differ.config import RDF_DIFFER_LOGGER
from rdf_differ.entrypoints.ui import app
from rdf_differ.entrypoints.ui.api_wrapper import get_datasets, create_diff as api_create_diff, get_dataset, get_report
from rdf_differ.entrypoints.ui.forms import CreateDiffForm
from rdf_differ.entrypoints.ui.helpers import get_error_message_from_response

logger = logging.getLogger(RDF_DIFFER_LOGGER)


@app.route('/')
def index():
    """
    Home page containing the list of available dataset diffs.
    """
    logger.debug('request index view')
    datasets, _ = get_datasets()

    logger.debug('render index view')
    return render_template('index.html', datasets=datasets)


@app.route('/create-diff', methods=['GET', 'POST'])
def create_diff():
    """
    Page for creating a new dataset diff.
    """
    logger.debug('request create diff view')

    form = CreateDiffForm()

    if form.validate_on_submit():
        response, status = api_create_diff(
            dataset_name=form.dataset_name.data,
            dataset_description=form.dataset_description.data,
            dataset_uri=form.dataset_uri.data,
            old_version_id=form.old_version_id.data,
            old_version_file=form.old_version_file_content.data,
            new_version_id=form.new_version_id.data,
            new_version_file=form.new_version_file_content.data
        )

        if status != 200:
            exception_text = get_error_message_from_response(response)
            logger.exception(exception_text)
            flash(exception_text, 'error')
        else:
            flash(response, 'success')
            logger.debug('render create diff view')
            return redirect(url_for('view_dataset', dataset_id=form.dataset_name.data))

    logger.debug('render create diff clean view')
    return render_template('dataset/create_diff.html', title='Create diff', form=form)


@app.route('/diffs/<dataset_id>')
def view_dataset(dataset_id: str):
    """
    Page for viewing a dataset diff.
    :param dataset_id: The dataset identifier. This should be short alphanumeric string uniquely identifying the dataset
    """
    logger.debug(f'request dataset view for: {dataset_id}')
    dataset, _ = get_dataset(dataset_id)

    logger.debug(f'render dataset view for: {dataset_id}')
    return render_template('dataset/view_dataset.html', title=f'{dataset_id} view', dataset=dataset)


@app.route('/diff-report/<dataset_id>')
def download_report(dataset_id: str):
    logger.debug(f'request diff report view for: {dataset_id}')
    try:
        with tempfile.TemporaryDirectory() as temp_folder:
            file_name = f"report-{dataset_id}.html"
            report_content, _ = get_report(dataset_id)
            report = Path(temp_folder) / file_name
            report.write_bytes(report_content)
            logger.debug(f'render diff report view for: {dataset_id}')
            return send_from_directory(Path(temp_folder), file_name, as_attachment=True)
    except Exception as e:
        logger.exception(str(e))

        flash(str(e), 'error')
        datasets, _ = get_datasets()

        logger.debug('redirect to index view')
        return render_template('index.html', datasets=datasets)
