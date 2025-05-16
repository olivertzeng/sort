# main.py
from src.sort import sortLib

# output_lines = processor.process(input_lines)
input_file = "input.csv"
with open(input_file, "r") as f:
    input_lines = [l.strip() for l in f.readlines()]
processor = sortLib(block_file="blocked.txt", unblock_file="unblocked.txt", debug=False)
categorized = [[] for _ in range(20)]
for l in input_lines:
    categorized[int(l.rsplit(",", 1)[1])].append([l])
for r in categorized:
    r = processor.process(r)
