# main.py
from src.sort import sortLib

# output_lines = processor.process(input_lines)
input_file = "phrases.csv"
with open(input_file, "r") as f:
    title = f.readline().strip()
    input_lines = [l.strip() for l in f.readlines()]

categorized = [[] for _ in range(21)]
uncategorized = []
d = True
perSection = False
x = 0
p = sortLib(
    blockFile="src/lists/blocked.txt",
    unblockFile="src/lists/unblocked.txt",
    ceecFile="src/lists/ceec.txt",
    perSection=perSection,
    debug=d,
)

input_lines = p.group(input_lines, "")

for l in input_lines:
    index = l.rsplit(",", 1)[-1] or 0
    categorized[int(index)].append(l)

if d:
    with open("debug/categorized.csv", "w") as f:
        f.write(title + "\n")
        for r in categorized:
            for e in r:
                f.write(e + "\n")

for cat, r in enumerate(categorized[:]):
    result, x = p.process(r, x, cat)
    categorized[cat] = result

if not perSection:
    for r in categorized:
        for e in r:
            uncategorized.append(e)
    uncategorized = p.labelLineNumbers(uncategorized)

with open("output.csv", "w") as f:
    f.write(title + "\n")
    if perSection:
        for r in categorized:
            for e in r:
                f.write(e + "\n")
    else:
        for e in uncategorized:
            f.write(e + "\n")
