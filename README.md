# Word Error Rate Calculator

## Installation

```sh
git clone https://github.com/camball/word-error-rate-cli
cd word-error-rate-cli/
pip3 install .
wer --expected Expected --actual Actual
```

## Usage

### Basic

```sh
$ wer --expected Expected --actual Actual  # usage with folders

+-----------------+-----------------------+---------+-----------+
|     Filename    | Word Error Rate (WER) | % Error | % Success |
+-----------------+-----------------------+---------+-----------+
| test_data_1.txt |   0.3157894736842105  |  31.58% |   68.42%  |
| test_data_2.txt |   0.3684210526315789  |  36.84% |   63.16%  |
+-----------------+-----------------------+---------+-----------+

$ wer --expected expected.txt --actual actual.txt  # usage with single files

Word Error Rate (WER):  0.3157894736842105
Percent Error:  31.58%
Percent Success:  68.42%
```

### `--ignore`/`-i`

The following demonstrates example usage of the `-i`/`--ignore` option. For example, if you are trying to calculate the WER on speech-to-text transcriptions, where each line begins with "Agent:" and "Customer:", denoting who is speaking in a conversation, that is metadata about the conversation (i.e., not the actual text we want to calculate on) and should be ignored when processing the WER.

```txt
Agent: Good evening!
Customer: Hi, good evening.
```

To handle this, the program allows you to pass a custom regex matcher, where any matches will be ignored. In the below example, the first run shows the processing on the raw text files. You can see that the success rate is higher than the second run, as the "Agent:"/"Customer:" text at the start of each line is artificially inflating it. On the second run, we apply the regex `^(?:Agent|Customer):` which properly ignores the file metadata, giving us the correct WER.

```sh
$ wer -e Expected -a Actual

+-----------------+-----------------------+---------+-----------+
|     Filename    | Word Error Rate (WER) | % Error | % Success |
+-----------------+-----------------------+---------+-----------+
| test_data_1.txt |   0.2727272727272727  |  27.27% |   72.73%  |
| test_data_2.txt |   0.3181818181818182  |  31.82% |   68.18%  |
+-----------------+-----------------------+---------+-----------+

$ wer -e Expected -a Actual -i "^(?:Agent|Customer):"

+-----------------+-----------------------+---------+-----------+
|     Filename    | Word Error Rate (WER) | % Error | % Success |
+-----------------+-----------------------+---------+-----------+
| test_data_1.txt |   0.3157894736842105  |  31.58% |   68.42%  |
| test_data_2.txt |   0.3684210526315789  |  36.84% |   63.16%  |
+-----------------+-----------------------+---------+-----------+
```

### `--enforce-file-length-check`/`-c`

When specified, enforces the rule that files being compared must have the same number of lines. Helpful for situations where you need to ensure your expected text file(s) have the same number of lines as your actual text file(s).

If specified and files are of different lengths, the program will raise an error like the following:

```txt
ValueError: After applying the transforms on the reference and hypothesis sentences, their lengths must match. Instead got 13 reference and 15 hypothesis sentences.
```

On a technical level, it removes the [`jiwer.ReduceToSingleSentence`](https://jitsi.github.io/jiwer/reference/transforms/#transforms.ReduceToSingleSentence) text transform that is applied by default.

## Gotchas

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
