# Word Error Rate Calculator

Calculate the word error rate (WER) from provided correct and actual text file(s), for measuring the accuracy of automated speech recognition systems.

```sh
$ wer --expected Expected --actual Actual  # usage comparing folders of corresponding files

+-----------------+--------------+---------+-----------+------+------+---------+
|        Filename | WER          | % Error | % Success | Dels | Subs | Inserts |
+-----------------+--------------+---------+-----------+------+------+---------+
| test_data_1.txt | 0.3157894737 |  31.58% |    68.42% |    0 |    6 |       0 |
| test_data_2.txt | 0.3684210526 |  36.84% |    63.16% |    1 |    6 |       0 |
| test_data_3.txt | 0.1428571429 |  14.29% |    85.71% |    0 |    1 |       0 |
+-----------------+--------------+---------+-----------+------+------+---------+
|           Mean: | 0.2756892231 |  27.57% |    72.43% | 0.33 | 4.33 |       0 |
|         Median: | 0.3157894737 |  31.58% |    68.42% |    0 |    6 |       0 |
+-----------------+--------------+---------+-----------+------+------+---------+

$ wer --expected expected.txt --actual actual.txt  # usage comparing single files

Word Error Rate (WER):  0.3157894737
Percent Error:          31.58%
Percent Success:        68.42%

Deletions:              0
Substitutions:          6
Insertions:             0
```

## Installation

```sh
# clone on your machine
git clone https://github.com/camball/word-error-rate-cli

# enter the install directory
cd word-error-rate-cli/

# install
pip3 install .

# use the program
wer --expected Expected --actual Actual
```

## Options

### `--ignore`/`-i`

The following demonstrates example usage of the `-i`/`--ignore` option. For example, if you are trying to calculate the WER on speech-to-text transcriptions, where each line begins with "Agent:" and "Customer:", denoting who is speaking in a conversation, that is metadata about the conversation (i.e., not the actual text we want to calculate on) and should be ignored when processing the WER.

```text
Agent: Good evening!
Customer: Hi, good evening.
```

To handle this, the program allows you to pass a custom regex matcher, where any matches will be ignored. In the below example, the first run shows the processing on the raw text files. You can see that the success rate is higher than the second run, as the "Agent:"/"Customer:" text at the start of each line is artificially inflating it. On the second run, we apply the regex `^(?:Agent|Customer):` which properly ignores the file metadata, giving us the correct WER.

```sh
$ wer -e Expected -a Actual

+-----------------+--------------+---------+-----------+------+------+---------+
|        Filename | WER          | % Error | % Success | Dels | Subs | Inserts |
+-----------------+--------------+---------+-----------+------+------+---------+
| test_data_1.txt | 0.2727272727 |  27.27% |    72.73% |    0 |    6 |       0 |
| test_data_2.txt | 0.3181818182 |  31.82% |    68.18% |    1 |    6 |       0 |
| test_data_3.txt | 0.125        |  12.50% |    87.50% |    0 |    1 |       0 |
+-----------------+--------------+---------+-----------+------+------+---------+
|           Mean: | 0.2386363636 |  23.86% |    76.14% | 0.33 | 4.33 |       0 |
|         Median: | 0.2727272727 |  27.27% |    72.73% |    0 |    6 |       0 |
+-----------------+--------------+---------+-----------+------+------+---------+

$ wer -e Expected -a Actual -i "^(?:Agent|Customer):"

+-----------------+--------------+---------+-----------+------+------+---------+
|        Filename | WER          | % Error | % Success | Dels | Subs | Inserts |
+-----------------+--------------+---------+-----------+------+------+---------+
| test_data_1.txt | 0.3157894737 |  31.58% |    68.42% |    0 |    6 |       0 |
| test_data_2.txt | 0.3684210526 |  36.84% |    63.16% |    1 |    6 |       0 |
| test_data_3.txt | 0.1428571429 |  14.29% |    85.71% |    0 |    1 |       0 |
+-----------------+--------------+---------+-----------+------+------+---------+
|           Mean: | 0.2756892231 |  27.57% |    72.43% | 0.33 | 4.33 |       0 |
|         Median: | 0.3157894737 |  31.58% |    68.42% |    0 |    6 |       0 |
+-----------------+--------------+---------+-----------+------+------+---------+
```

### `--visualize-output`/`-v`

Compute word alignment visualizations. Shows sentence-by-sentence comparisons of substitutions, deletions, insertions, and correct words.

- If folders are provided to `--expected`/`--actual`, a folder should be specified. It will be created if the folder doesn't already exist.
- If files are provided to `--expected`/`--actual`, a filename should be specified. The file will be created, or overwritten if already exists.

Output looks like the following:

```sh
wer -e expected.txt -a actual.txt -v output.txt
```

```text
sentence 1
REF: hello  this is a test great  thank you *** this is another  line
HYP: hello these is a **** great thanks you and this is another lines
               S         D            S       I                     S
```

or when `--enforce-file-length-check` is specified:

```sh
wer -e expected.txt -a actual.txt -c -v output.txt
```

```text
sentence 1
REF: hello  this is a test
HYP: hello these is a ****
               S         D

sentence 2
REF: great  thank you ***
HYP: great thanks you and
                S       I

sentence 3
REF: this is another  line
HYP: this is another lines
                         S
```

### `--enforce-file-length-check`/`-c`

When specified, enforces the rule that files being compared must have the same number of lines. Helpful for situations where you need to ensure your expected text file(s) have the same number of lines as your actual text file(s).

If specified and files are of different lengths, the program will raise an error like the following:

```text
ValueError: After applying the transforms on the reference and hypothesis sentences, their lengths must match. Instead got 13 reference and 15 hypothesis sentences.
```

On a technical level, it removes the [`jiwer.ReduceToSingleSentence`](https://jitsi.github.io/jiwer/reference/transforms/#transforms.ReduceToSingleSentence) text transform that is applied by default.

## Gotchas

- If `--visualize-output` is specified and `--enforce-file-length-check` is not specified, you will only get a single sentence in the output file(s), as output is reduced to a single sentence intentionally. To get separate comparison output for different sentences, ensure `--enforce-file-length-check` is specified and that your files are of the same length.
- When folders are provided to the `--expected` and `--actual` arguments, each folder must contain exactly the same file content. For example, if the program is run as:

    ```sh
    wer --expected Expected --actual Actual
    ```

    where `Expected` is a folder of transcript files that have been manually corrected by a human and `Actual` is a folder of the actual transcript files from a call transcription software, then `Expected` and `Actual` both need to have the same number of files, and the same filenames. So for example, if `Expected` contains the following files:

    ```text
    Expected
    ├── transcript_1.txt
    └── transcript_2.txt
    ```

    then `Actual` needs to have the exact same filenames:

    ```text
    Actual
    ├── transcript_1.txt
    └── transcript_2.txt
    ```

    This is necessary so that the program knows which corresponding files to compare with when calculating WERs.

## Development

```sh
uv run wer
```
