import argparse
import jiwer
import jiwer.transforms as tr
from pathlib import Path
from prettytable import PrettyTable
from collections.abc import Mapping
from statistics import mean, median
from typing import Literal
import sys

WER_PRECISION = 10
"""Decimal places to display for word error rates."""

PATH_METAVAR = "<path>"

type ComparisonData = Mapping[str, jiwer.WordOutput]


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
        metavar=PATH_METAVAR,
    )
    parser.add_argument(
        "--actual",
        "-a",
        required=True,
        help="path to a file/folder of what the text actually was",
        metavar=PATH_METAVAR,
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
    parser.add_argument(
        "--visualize-output",
        "-v",
        help=(
            "compute word alignment visualizations. shows sentence-by-sentence "
            "comparisons of substitutions, deletions, insertions, and correct words. "
            "if folders are provided to --expected/--actual, a folder should be specified. "
            "it will be created if the folder doesn't exist. "
            "if files are provided to --expected/--actual, a filename should be specified. "
            "the file will be created, or overwritten if already exists. "
        ),
        metavar=PATH_METAVAR,
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


def process_words(
    expected_path: Path,
    actual_path: Path,
    enforce_file_length_check: bool,
    regex_to_ignore: str,
) -> jiwer.WordOutput:
    return jiwer.process_words(
        reference=lines_from_file(expected_path),
        hypothesis=lines_from_file(actual_path),
        reference_transform=custom_transform(
            enforce_file_length_check, regex_to_ignore
        ),
        hypothesis_transform=custom_transform(
            enforce_file_length_check, regex_to_ignore
        ),
    )


# Since `prettytable` doesn't export the type, we copy it here
type AlignType = Literal["l", "r", "c"]


def make_table(comparison_data: ComparisonData) -> PrettyTable:
    """Construct the output table from comparison data.

    :param Mapping[str, jiwer.WordOutput] comparison_data: Keys are filenames
        of corresponding files being compared; values are the comparison data
        for the files (e.g., WER, # insertions, # deletions, etc.).
    :return PrettyTable:
    """
    columns: dict[str, AlignType] = {
        "Filename": "r",
        "WER": "l",
        r"% Error": "r",
        r"% Success": "r",
        "Dels": "r",
        "Subs": "r",
        "Inserts": "r",
    }
    table = PrettyTable(list(columns))
    for filename, alignment in columns.items():
        table.align[filename] = alignment

    for idx, (filename, data) in enumerate(comparison_data.items()):
        table.add_row(
            [
                filename,
                round(data.wer, WER_PRECISION),
                f"{data.wer:.2%}",
                f"{1 - data.wer:.2%}",
                data.deletions,
                data.substitutions,
                data.insertions,
            ],
            divider=idx == len(comparison_data) - 1,
        )

    word_error_rates = [data.wer for data in comparison_data.values()]
    wer_mean = mean(word_error_rates)
    wer_median = median(word_error_rates)

    deletions = [data.deletions for data in comparison_data.values()]
    substitutions = [data.substitutions for data in comparison_data.values()]
    insertions = [data.insertions for data in comparison_data.values()]

    table.add_row(
        [
            "Mean:",
            round(wer_mean, WER_PRECISION),
            f"{wer_mean:.2%}",
            f"{1 - wer_mean:.2%}",
            round(mean(deletions), 2),
            round(mean(substitutions), 2),
            round(mean(insertions), 2),
        ]
    )
    table.add_row(
        [
            "Median:",
            round(wer_median, WER_PRECISION),
            f"{wer_median:.2%}",
            f"{1 - wer_median:.2%}",
            round(median(deletions), 2),
            round(median(substitutions), 2),
            round(median(insertions), 2),
        ]
    )

    return table


def write_word_alignments_to_files(output_dir: Path, comparison_data: ComparisonData):
    for filename, data in comparison_data.items():
        with open(output_dir / filename, "w") as f:
            f.write(jiwer.visualize_alignment(data, show_measures=False))


def main():
    args = get_args(sys.argv[1:])

    expected_path = Path(args.expected)
    actual_path = Path(args.actual)

    if not expected_path.exists() or not actual_path.exists():
        raise FileNotFoundError(
            f"One or both of \n\n- {expected_path}\n- {actual_path}\n\n does not exist; "
            "please ensure the files exist in the right location."
        )

    if expected_path.is_file() and actual_path.is_file():
        data = process_words(
            expected_path, actual_path, args.enforce_file_length_check, args.ignore
        )
        print()
        print(f"Word Error Rate (WER):  {data.wer:.{WER_PRECISION}f}")
        print(f"Percent Error:          {data.wer:.2%}")
        print(f"Percent Success:        {1 - data.wer:.2%}")
        print()
        print(f"Deletions:              {data.deletions}")
        print(f"Substitutions:          {data.substitutions}")
        print(f"Insertions:             {data.insertions}")
        print()

        if args.visualize_output:
            if Path(args.visualize_output).is_dir():
                raise ValueError(
                    f"{args.visualize_output} is a folder that already exists. "
                    "A filename is required."
                )

            with open(args.visualize_output, "w") as f:
                f.write(jiwer.visualize_alignment(data, show_measures=False))

    elif expected_path.is_dir() and actual_path.is_dir():
        expected_filenames = {filename.name for filename in expected_path.iterdir()}
        actual_filenames = {filename.name for filename in actual_path.iterdir()}

        if expected_filenames != actual_filenames:
            raise FileNotFoundError(
                "The expected folder and actual folder have differing file contents. "
                "Please ensure both folders have the same number of files with the same corresponding filenames."
            )

        comparison_data = {
            expected_file.name: process_words(
                expected_file,
                actual_file,
                args.enforce_file_length_check,
                args.ignore,
            )
            for expected_file, actual_file in zip(
                expected_path.iterdir(), actual_path.iterdir(), strict=True
            )
        }

        if args.visualize_output:
            output_path = Path(args.visualize_output)
            output_path.mkdir(mode=0o755, parents=True, exist_ok=True)
            write_word_alignments_to_files(output_path, comparison_data)

        table = make_table(comparison_data)
        print(f"\n{table}\n")

    else:
        raise ValueError(
            f"A {'file' if expected_path.is_file() else 'folder'} was provided to --expected, yet "
            f"a {'file' if actual_path.is_file() else 'folder'} was provided to --actual.\n"
            "Please provide a file to both arguments, or a folder to both arguments."
        )


if __name__ == "__main__":
    main()
