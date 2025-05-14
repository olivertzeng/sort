# main.py
from src.sort import sortPhrases

# input_lines = ["phrase1", "phrase2"]
# output_lines = processor.process(input_lines)

processor = sortPhrases(
    block_file="blocked.txt",
    unblock_file="unblocked.txt",
)
