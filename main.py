# main.py
from src.sort import sortLib

# output_lines = processor.process(input_lines)
input_file = "phrases.csv"
with open(input_file, "r") as f:
    title = f.readline().strip()
    input_lines = [l.strip() for l in f.readlines()]

categorized = [[] for _ in range(20)]
x = 0
d = True
p = sortLib(
    block_file="src/lists/blocked.txt",
    unblock_file="src/lists/unblocked.txt",
    ceec_file="src/lists/ceec.txt",
    debug=d,
)

input_lines = p.group(input_lines)

for l in input_lines:
    index = l.rsplit(",", 1)[-1] or 0
    categorized[int(index)].append(l)

if d:
    with open("debug/categorized.csv", "w") as f:
        f.write(title + "\n")
        for r in categorized:
            for e in r:
                f.write(e + "\n")

for r in categorized[:]:
    result, x = p.process(r, x)
    categorized.append(result)

with open("output.csv", "w") as f:
    f.write(title + "\n")
    for r in categorized:
        for e in r:
            f.write(e + "\n")
