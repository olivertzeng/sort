# main.py
from src.sort import sortLib

# output_lines = processor.process(input_lines)
input_file = "phrases.csv"
with open(input_file, "r") as f:
    title = f.readline().strip()
    input_lines = [l.strip() for l in f.readlines()]

categorized = [[] for _ in range(20)]
processor = sortLib(
    block_file="src/lists/blocked.txt",
    unblock_file="src/lists/unblocked.txt",
    ceec_file="src/lists/ceec.txt",
    debug=False,
)

for l in input_lines:
    categorized[int(l.rsplit(",", 1)[-1])].append([l])
for r in categorized:
    r = processor.process(r)
categorized = processor.labelCeec(categorized)

with open("output.csv", "w") as f:
    f.write(title + "\n")
    for r in categorized:
        for e in r:
            f.write(e + "\n")
