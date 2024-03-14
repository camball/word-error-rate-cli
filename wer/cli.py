import argparse
from jiwer import wer
from pathlib import Path
from prettytable import PrettyTable
import sys

AGENT_LINE_PREFIX = "Agent:"
CUSTOMER_LINE_PREFIX = "Customer:"


def get_args(args: list[str]):
    parser = argparse.ArgumentParser(
        prog="wer",
        description="Calculate a word error rate (WER) from provided sets of correct and actual transcripts.",
    )

    parser.add_argument(
        "--expected",
        "-e",
        required=True,
        help="path to a file/folder of what the text is supposed to be",
        metavar="<path>",
    )
    parser.add_argument(
        "--actual",
        "-a",
        required=True,
        help="path to a file/folder of what the text actually was",
        metavar="<path>",
    )

    return parser.parse_args(args)


def cleaned_line_data(file: Path) -> list[str]:
    with open(file) as f:
        return [
            (
                line.removeprefix(AGENT_LINE_PREFIX).strip()
                if line.startswith(AGENT_LINE_PREFIX)
                else line.removeprefix(CUSTOMER_LINE_PREFIX).strip()
            )
            for line in f.readlines()
        ]


def main():
    args = get_args(sys.argv[1:])

    expected_path = Path(args.expected)
    actual_path = Path(args.actual)

    if expected_path.is_file() and actual_path.is_file():
        word_error_rate = wer(
            reference=cleaned_line_data(expected_path),
            hypothesis=cleaned_line_data(actual_path),
        )
        print()
        print(f"Word Error Rate (WER):  {word_error_rate}")
        print(f"Percent Error:  {word_error_rate:.2%}")
        print(f"Percent Success:  {1-word_error_rate:.2%}")
        print()

    elif expected_path.is_dir() and actual_path.is_dir():
        expected_filenames = {filename.name for filename in expected_path.iterdir()}
        actual_filenames = {filename.name for filename in actual_path.iterdir()}
        if expected_filenames != actual_filenames:
            raise FileNotFoundError(
                "The expected folder and actual folder have differing file contents. "
                "Please ensure both folders have the same number of files with the same corresponding filenames."
            )

        word_error_rates = {
            expected_file.name: wer(
                reference=cleaned_line_data(expected_file),
                hypothesis=cleaned_line_data(actual_file),
            )
            for expected_file, actual_file in zip(
                expected_path.iterdir(), actual_path.iterdir(), strict=True
            )
        }

        table = PrettyTable()
        table.field_names = [
            "Filename",
            "Word Error Rate (WER)",
            r"% Error",
            r"% Success",
        ]

        for filename, word_error_rate in word_error_rates.items():
            table.add_row(
                [
                    filename,
                    word_error_rate,
                    f"{word_error_rate:.2%}",
                    f"{1-word_error_rate:.2%}",
                ]
            )

        print()
        print(table)
        print()

    elif not expected_path.exists() or not actual_path.exists():
        raise FileNotFoundError(
            f"One or both of \n\n- {expected_path}\n- {actual_path}\n\n does not exist; "
            "please ensure the files exist in the right location."
        )

    else:
        raise ValueError(
            f"A {'file' if expected_path.is_file() else 'folder'} was provided to --expected, yet "
            f"a {'file' if actual_path.is_file() else 'folder'} was provided to --actual.\n"
            "Please provide a file to both arguments, or a folder to both arguments."
        )


if __name__ == "__main__":
    main()
