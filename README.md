# Word Error Rate Calculator

## Installation

```sh
git clone https://github.com/camball/word-error-rate-cli
cd word-error-rate-cli/
pip3 install .
wer --expected Expected --actual Actual
```

## Usage

```sh
$ wer --expected Expected --actual Actual

+-----------------+-----------------------+---------+-----------+
|     Filename    | Word Error Rate (WER) | % Error | % Success |
+-----------------+-----------------------+---------+-----------+
| test_data_1.txt |   0.3157894736842105  |  31.58% |   68.42%  |
| test_data_2.txt |   0.3684210526315789  |  36.84% |   63.16%  |
+-----------------+-----------------------+---------+-----------+

$ wer --expected expected.txt --actual actual.txt

Word Error Rate (WER):  0.3157894736842105
Percent Error:  31.58%
Percent Success:  68.42%
```

## Gotchas

- Any two files being compared have to have the same number of sentences (lines), as this is a requirement for calculating the WER. For example, one file can't be 13 lines long and the other 15; they both have to be either 13 or 15 in that case. You will get an error if this condition is not met, that looks like

    ```txt
    ValueError: After applying the transforms on the reference and hypothesis sentences, their lengths must match. Instead got 13 reference and 15 hypothesis sentences.
    ```

- When folders are provided to the `--expected` and `--actual` arguments, each folder must contain exactly the same file content. For example, if the program is run as:

    ```sh
    wer --expected Expected --actual Actual
    ```

    where `Expected` is a folder of transcript files that have been manually corrected by a human and `Actual` is a folder of the actual transcript files from a call transcription software, then `Expected` and `Actual` both need to have the same number of files, and the same filenames. So for example, if `Expected` contains the following files:

    ```txt
    Expected
    ├── transcript_1.txt
    └── transcript_2.txt
    ```

    then `Actual` needs to have the exact same filenames:

    ```txt
    Actual
    ├── transcript_1.txt
    └── transcript_2.txt
    ```
