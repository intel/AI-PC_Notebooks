import argparse
import os
import sys
import logging

import tree_sitter_python
from tree_sitter import Language, Parser

from aidocapp import model, utils


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file",
        nargs="?",
        default=os.getcwd(),
        help="File path to parse and generate documentation comments for.",
    )
    parser.add_argument(
        "--local_model",
        type=str,
        help="Path to the local model.",
    )

    if sys.argv.__len__() < 4:
        sys.exit("Please provide a file and path to the local model.")

    args = parser.parse_args()
    # print(args)

    logging.basicConfig(level=logging.INFO)

    path = args.file

    file_list = {}
    if os.path.isdir(path):
        file_list = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.py')]

    elif os.path.isfile(path) and path.endswith('.py'):
        file_list = {path}

    model_wrapper = model.Model(local_model=args.local_model)

    for file_name in file_list:
        generated_comments = {}

        logging.info("Processing \'{}\' file".format(file_name))

        with open(file_name, "r") as file:
            # Read the entire content of the file into a string
            file_bytes = file.read().encode()
            PY_LANGUAGE = Language(tree_sitter_python.language())

            # Create a parser and set its language
            parser = Parser(PY_LANGUAGE)

            tree = parser.parse(file_bytes)
            root_node = tree.root_node
            extracted_elements = utils.extract_elements(root_node, file_bytes)

            for element in extracted_elements:
                method_source_code = ""
                if element['type'] == 'function_definition':
                    method_source_code = element['text']

                # Add comment to the code
                logging.info("Generating comments for \'{}\' method".format(method_source_code.partition('\n')[0]))
                documented_method_source_code = model_wrapper.generate_comments(code=method_source_code, language="python")

                generated_comments[method_source_code] = documented_method_source_code

            file.close()

        for original_code, generated_doc_comment in generated_comments.items():
            utils.write_code_comments_to_file(file_name, original_code, generated_doc_comment)
