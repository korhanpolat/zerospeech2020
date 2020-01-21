"""Utility functions for ZRC2020 validation"""

import os
import yaml


def validate_yaml(filename, name, entries, optional_entries={}):
    """Checks if a YAML metadata file have the expected format

    Parameters
    ----------
    filename (str): the YAML file to check

    name (str): nickname of the file to print error messages

    entries (dict): a dictionary of excepted entries to match in the YAML file.
        Each entry is in the form (name, type), where type can be None if no
        constraint on the expected type.

    optional_entries (dict): as the parameter `entries` but for optional
        entries. Can be present but not mandatory.

    Returns
    -------
    metadata (dict) : the entries parsed from the YAML file

    Raises
    ------
    ValueError if anything goes wrong

    """
    if not os.path.isfile(filename):
        raise ValueError(f'{name} file not found: {filename}')

    try:
        metadata = yaml.safe_load(open(filename, 'r'))
    except yaml.YAMLError:
        raise ValueError(f'failed to parse {name}')

    if not metadata:
        raise ValueError(f'{name} file is empty')

    # ensure the mandatory entries are here
    mandatory = sorted(entries.keys())
    try:
        existing = sorted(metadata.keys())
    except AttributeError:  # yaml can load string only
        raise ValueError(f'failed to parse {name}')

    missing = [e for e in mandatory if e not in mandatory]
    if missing:
        raise ValueError(
            f'the following {name} entries are missing: {", ".join(missing)}')

    optional = sorted(optional_entries.keys())
    extra = [e for e in existing if e not in mandatory + optional]
    if extra:
        raise ValueError(
            f'the following {name} entries are forbidden: {", ".join(extra)}')

    # ensure all the entries are valid
    entries.update(optional_entries)
    for k, v in metadata.items():
        if v is None:
            raise ValueError(f'entry "{k}" is empty in {name}')
        if entries[k] and not isinstance(v, entries[k]):
            raise ValueError(
                f'entry "{k}" in {name} must be of type {entries[k]}')

    return metadata


def validate_code(directory, name, is_open_source, log):
    """Checks if a code directory is valid

    Parameters
    ----------
    directory (str): code directory to check

    name (str) : nickname of the dircetory for error message printing

    is_open_source (bool) : True if the flag "open source" is set in the
        submission, False otherwise

    log (logging.Logger) : where to send log messages

    Raises
    ------
    ValueError if anything goes wrong

    """
    log.info('validating %s directory ...', name)

    # if closed source, do not expect the directory to be present, but tolerate
    # an empty directory
    if not is_open_source and os.path.isdir(directory):
        if os.listdir(directory):
            raise ValueError(
                f'submission declared closed source but {name} directory '
                f'is not empty')

    # when declared opens source make sure the directory is not empty
    if is_open_source:
        if not os.path.isdir(directory):
            raise ValueError(
                f'submission declared open source but missing folder {name}')
        elif not os.listdir(directory):
            raise ValueError(
                f'submission declared open source but empty folder {name}')

        log.info(
            f'    found a non-empty "{name}" directory, it will be manually '
            f'inspected to confirm the submission is open source')


def validate_directory(directory, name, entries, log, all_exist=False):
    log.info('validating %s directory ...', name)

    if not os.path.isdir(directory):
        raise ValueError(f'{name} directory not found')

    existing = set(os.listdir(directory))
    extra = existing - set(entries)
    if extra:
        raise ValueError(
            f'{name} directory contains extra files or directories: '
            f'{", ".join(extra)}')

    if all_exist:
        missing = set(entries) - existing
        if missing:
            raise ValueError(
                f'{name} directory has missing files or directories: '
                f'{", ".join(missing)}')

    return existing
