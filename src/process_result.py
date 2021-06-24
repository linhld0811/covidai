# common
import os

# parser
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--gr", default="dataset/zalo-ai/testset/ground_truth.csv")
parser.add_argument("--hyp", default="result/submission.csv")
args = parser.parse_args()

# ground_truth
f1 = open(args.gr, "r")
fns1 = f1.readlines()
f1.close()

MAP_GT = {}
for line in fns1:
    if line.strip == "filename, ground_truth, hypothesis": continue
    fn = line.strip().split(",")[0]
    gr = line.strip().split(",")[1]
    MAP_GT[fn] = gr


# hypothesis
f2 = open(args.hyp, "r")
fns2 = f2.readlines()
f2.close()

MAP_HYP = {}
for line in fns2:
    if line.strip == "filename, ground_truth, hypothesis": continue
    fn = line.strip().split(",")[0]
    hyp = line.strip().split(",")[-1]
    MAP_HYP[fn] = hyp

assert len(MAP_HYP) == len(MAP_GT)
header = "filename, ground_truth, hypothesis" + "\n"
output = open(os.path.dirname(args.gr) + "/final.csv", "w")
output.write(header)
num = len(MAP_HYP)
r = 0
for fn in MAP_GT.keys():
    new_line = fn + "," + str(MAP_GT[fn]) + "," + str(MAP_HYP[fn]) + "\n"
    if MAP_GT[fn] == MAP_HYP[fn]:
        r += 1
    output.write(new_line)
output.close()

acc = open("accuracy.txt", "w")
acc.write("accuracy:" + str(r/num) + "\n")
acc.close()