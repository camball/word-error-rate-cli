import argparse
from jiwer import wer as _real_wer, transforms as tr
from pathlib import Path
from prettytable import PrettyTable
import sys


def get_args(args: list[str]):
    parser = argparse.ArgumentParser(
        prog="wer",
        description="Calculate the word error rate (WER) from provided correct and actual text file(s).",
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
    parser.add_argument(
        "--enforce-file-length-check",
        "-c",
        help="if specified, enforces the rule that files being compared must have the same number of lines",
        action="store_true",
    )
    parser.add_argument(
        "--ignore",
        "-i",
        help="any matches to this regex pattern will be ignored from processing",
        metavar="<regex>",
    )

    return parser.parse_args(args)


def lines_from_file(file: Path) -> list[str]:
    with open(file) as f:
        return f.readlines()


class DoNothingTransform(tr.AbstractTransform):
    """A transform for an idempotent operation; enables conditionally applying a transform."""

    def process_string(self, s: str):
        return s


def custom_transform(
    enforce_file_length_check: bool | None = False,
    regex_to_ignore: str | None = None,
):
    return tr.Compose(
        [
            (
                tr.SubstituteRegexes({regex_to_ignore: r" "})
                if regex_to_ignore
                else DoNothingTransform()
            ),
            tr.ToLowerCase(),
            tr.ExpandCommonEnglishContractions(),
            tr.RemovePunctuation(),
            tr.RemoveWhiteSpace(replace_by_space=True),
            tr.RemoveMultipleSpaces(),
            tr.Strip(),
            (
                DoNothingTransform()
                if enforce_file_length_check
                else tr.ReduceToSingleSentence()
            ),
            tr.ReduceToListOfListOfWords(),
        ]
    )


def wer(
    expected_path: Path,
    actual_path: Path,
    enforce_file_length_check: bool,
    regex_to_ignore: str,
):
    return _real_wer(
        reference=lines_from_file(expected_path),
        hypothesis=lines_from_file(actual_path),
        reference_transform=custom_transform(
            enforce_file_length_check, regex_to_ignore
        ),
        hypothesis_transform=custom_transform(
            enforce_file_length_check, regex_to_ignore
        ),
    )


def main():
    args = get_args(sys.argv[1:])

    expected_path = Path(args.expected)
    actual_path = Path(args.actual)

    if expected_path.is_file() and actual_path.is_file():
        word_error_rate = wer(
            expected_path, actual_path, args.enforce_file_length_check, args.ignore
        )
        print()
        print(f"Word Error Rate (WER):  {word_error_rate}")
        print(f"Percent Error:          {word_error_rate:.2%}")
        print(f"Percent Success:        {1-word_error_rate:.2%}")
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
                expected_file,
                actual_file,
                args.enforce_file_length_check,
                args.ignore,
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
