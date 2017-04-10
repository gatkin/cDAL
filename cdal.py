"""Top-level main entry point into the cDAL tool"""
import argparse
import json

from codegen.accessor import accessor_header_file_create, accessor_source_file_create
from codegen.ctypes import ctypes_header_file_create, ctypes_source_file_create
import datasetdef


def _accessor_files_create(dataset, output_dir):
    """Creates all accessor files"""
    accessor_header_file_create(dataset, output_dir)
    accessor_source_file_create(dataset, output_dir)


def _dataset_parse(definition_file_path):
    """Parses the dataset from the dataset definition file at the spcified path"""
    with open(definition_file_path) as definition_file:
        definition = json.load(definition_file)

    return datasetdef.dataset_from_definition(definition)


def _type_files_create(dataset, output_dir):
    """Creates all C type files for the provided dataset"""
    ctypes_header_file_create(dataset, output_dir)
    ctypes_source_file_create(dataset, output_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset_definition_file', help='Path to dataset definition file', type=str)
    parser.add_argument('output_dir', help='Path to directory')

    args = parser.parse_args()

    dataset = _dataset_parse(args.dataset_definition_file)

    _type_files_create(dataset, args.output_dir)
    _accessor_files_create(dataset, args.output_dir)

