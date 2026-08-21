import pandas as pd
import glob

files = sorted(glob.glob("*.csv"))
del files[1] # participant 101 deleted due to chance-level accuracy

raw = []
for f in files:
    d = pd.read_csv(f)
    raw.append(d)
raw = pd.concat(raw, ignore_index=True)
raw.to_csv("final.csv", index=False)