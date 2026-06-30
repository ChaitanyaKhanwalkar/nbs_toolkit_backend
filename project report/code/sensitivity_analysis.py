#!/usr/bin/env python3
"""
sensitivity_analysis.py  --  AHP-TOPSIS weight sensitivity battery for the NbS Toolkit paper.

WHAT THIS PRODUCES (the paper's "is the ranking robust?" evidence):
  1. baseline_ranking.csv      -- the ranking under your real weights
  2. oat_results.csv           -- One-At-a-Time: scale each weight, see if the ranking moves
  3. extreme_cases.csv         -- equal-weights and one-criterion-removed rankings
  4. monte_carlo_stability.csv -- random weight draws: how often each train stays top-3

WHY THESE: author-derived AHP weights survive peer review when you can show the
top recommendations DON'T flip under reasonable weight perturbation. That is the
single highest-value figure/table for defending your weighting choice.

INPUTS (export these two CSVs from the canonical engine / DB):
  weights.csv         columns: criterion,weight,direction
                      direction = "benefit" (higher is better) or "cost" (lower is better)
                      weights need not sum to 1; the script renormalises.
  decision_matrix.csv first column = option name (train/NbS); other columns = criterion
                      names matching weights.csv exactly; cells = raw criterion scores.

RUN:
  python sensitivity_analysis.py                 # uses weights.csv + decision_matrix.csv
  python sensitivity_analysis.py --demo          # synthetic smoke-test (NOT real data)

Only dependency: numpy (pip install numpy). scipy used if present for Spearman;
falls back to a built-in rank correlation otherwise.
"""

import csv, sys, itertools, random
import numpy as np

# ---------- TOPSIS core ----------
def topsis(matrix, weights, directions):
    """matrix: (n_options, n_criteria) raw scores. weights: (n_criteria,) sum=1.
       directions: list of 'benefit'/'cost'. Returns closeness Ci (n_options,)."""
    M = matrix.astype(float).copy()
    # vector normalisation
    norms = np.sqrt((M**2).sum(axis=0))
    norms[norms == 0] = 1.0
    N = M / norms
    V = N * weights  # weighted normalised
    # ideal best / worst per criterion, respecting benefit vs cost
    ideal_best, ideal_worst = np.zeros(V.shape[1]), np.zeros(V.shape[1])
    for j, d in enumerate(directions):
        col = V[:, j]
        if d == "benefit":
            ideal_best[j], ideal_worst[j] = col.max(), col.min()
        else:  # cost
            ideal_best[j], ideal_worst[j] = col.min(), col.max()
    d_best = np.sqrt(((V - ideal_best)**2).sum(axis=1))
    d_worst = np.sqrt(((V - ideal_worst)**2).sum(axis=1))
    denom = d_best + d_worst
    denom[denom == 0] = 1e-12
    return d_worst / denom  # Ci in [0,1], higher = better

def ranking_from_scores(scores):
    """Return ranks (1 = best). Higher score = better."""
    order = np.argsort(-scores)
    ranks = np.empty_like(order)
    ranks[order] = np.arange(1, len(scores) + 1)
    return ranks

def spearman(a, b):
    try:
        from scipy.stats import spearmanr
        return float(spearmanr(a, b).correlation)
    except Exception:
        a = np.asarray(a, float); b = np.asarray(b, float)
        ar = a.argsort().argsort(); br = b.argsort().argsort()
        ar = ar - ar.mean(); br = br - br.mean()
        d = np.sqrt((ar**2).sum() * (br**2).sum())
        return float((ar*br).sum()/d) if d else 1.0

def renorm(w):
    w = np.clip(np.asarray(w, float), 0, None)
    s = w.sum()
    return w/s if s else w

# ---------- I/O ----------
def load_inputs():
    crit, w, direc = [], [], []
    for r in csv.DictReader(open("weights.csv")):
        crit.append(r["criterion"].strip())
        w.append(float(r["weight"]))
        direc.append(r["direction"].strip().lower())
    opts, rows = [], []
    rdr = csv.reader(open("decision_matrix.csv"))
    header = next(rdr)
    col_idx = {h.strip(): k for k, h in enumerate(header)}
    for c in crit:
        if c not in col_idx:
            sys.exit(f"ERROR: criterion '{c}' in weights.csv missing from decision_matrix.csv header.")
    for row in rdr:
        if not row or not row[0].strip():
            continue
        opts.append(row[0].strip())
        rows.append([float(row[col_idx[c]]) for c in crit])
    return crit, renorm(w), direc, opts, np.array(rows, float)

def demo_inputs():
    print(">>> DEMO MODE: synthetic numbers, NOT real project data. Pipeline smoke-test only.\n")
    crit = ["C1_gap_closure","C2_usecase_fit","C3_site_fit","C4_hydro_fit",
            "C6_footprint","C7_om_energy","C8_robustness"]
    direc = ["benefit","benefit","benefit","benefit","cost","cost","benefit"]
    w = renorm([0.26,0.20,0.12,0.10,0.12,0.12,0.08])
    opts = ["WSP train","UASB-STP","DEWATS","Septic+HSSF","VF hybrid",
            "French VF","On-site","Pond+aquaculture"]
    rng = np.random.default_rng(7)
    mat = rng.uniform(0.2, 0.95, size=(len(opts), len(crit)))
    return crit, w, direc, opts, mat

# ---------- sensitivity battery ----------
def run(crit, w, direc, opts, mat):
    base = topsis(mat, w, direc)
    base_rank = ranking_from_scores(base)
    order = np.argsort(base_rank)

    with open("baseline_ranking.csv","w",newline="") as f:
        wr = csv.writer(f); wr.writerow(["rank","option","Ci"])
        for k in order:
            wr.writerow([int(base_rank[k]), opts[k], round(float(base[k]),4)])
    top1 = opts[order[0]]; top3 = [opts[i] for i in order[:3]]
    print("BASELINE ranking (your weights):")
    for k in order:
        print(f"  {base_rank[k]:>2}. {opts[k]:22} Ci={base[k]:.4f}")
    print()

    # (1) OAT
    factors = [0.5,0.8,0.9,1.1,1.2,1.5,2.0]
    with open("oat_results.csv","w",newline="") as f:
        wr=csv.writer(f); wr.writerow(["criterion","factor","new_top1","top1_changed","spearman_vs_base"])
        oat_flip=0; oat_total=0
        for j,c in enumerate(crit):
            for fac in factors:
                w2=w.copy(); w2[j]=w[j]*fac; w2=renorm(w2)
                s2=topsis(mat,w2,direc); r2=ranking_from_scores(s2)
                nt1=opts[int(np.argmin(r2))]
                changed = nt1!=top1
                oat_flip+=int(changed); oat_total+=1
                wr.writerow([c,fac,nt1,changed,round(spearman(base,s2),4)])
    print(f"OAT: top-1 changed in {oat_flip}/{oat_total} single-weight perturbations "
          f"({100*oat_flip/oat_total:.0f}%).")

    # (2) extreme cases
    with open("extreme_cases.csv","w",newline="") as f:
        wr=csv.writer(f); wr.writerow(["case","new_top1","top3","spearman_vs_base"])
        weq=renorm(np.ones(len(crit)))
        seq=topsis(mat,weq,direc)
        oeq=np.argsort(ranking_from_scores(seq))
        wr.writerow(["equal_weights",opts[oeq[0]],"|".join(opts[i] for i in oeq[:3]),round(spearman(base,seq),4)])
        for j,c in enumerate(crit):
            w0=w.copy(); w0[j]=0; w0=renorm(w0)
            s0=topsis(mat,w0,direc); o0=np.argsort(ranking_from_scores(s0))
            wr.writerow([f"drop_{c}",opts[o0[0]],"|".join(opts[i] for i in o0[:3]),round(spearman(base,s0),4)])
    print("Extreme cases (equal-weights, one-criterion-dropped) written to extreme_cases.csv.")

    # (3) Monte Carlo
    N=5000; delta=0.30; rng=np.random.default_rng(42)
    top3_count=np.zeros(len(opts)); sp=[]; reversal=0
    for _ in range(N):
        w2=renorm(w*(1+rng.uniform(-delta,delta,size=len(w))))
        s2=topsis(mat,w2,direc); r2=ranking_from_scores(s2)
        o2=np.argsort(r2)
        for i in o2[:3]: top3_count[i]+=1
        sp.append(spearman(base,s2))
        if opts[int(o2[0])]!=top1: reversal+=1
    with open("monte_carlo_stability.csv","w",newline="") as f:
        wr=csv.writer(f); wr.writerow(["option","baseline_rank","P_top3_percent"])
        for k in order:
            wr.writerow([opts[k],int(base_rank[k]),round(100*top3_count[k]/N,1)])
    print(f"\nMonte Carlo ({N} draws, +/-{int(delta*100)}% per weight):")
    print(f"  top-1 ('{top1}') held in {100*(1-reversal/N):.1f}% of draws.")
    print(f"  mean Spearman vs baseline = {np.mean(sp):.3f} (1.0 = identical ranking).")
    print("  per-option P(top-3) -> monte_carlo_stability.csv")
    print("\nDONE. 4 CSVs written. The headline sentence for the paper is the")
    print("Monte-Carlo top-1 retention % + mean Spearman.")

if __name__=="__main__":
    if "--demo" in sys.argv:
        run(*demo_inputs())
    else:
        try:
            run(*load_inputs())
        except FileNotFoundError as e:
            sys.exit(f"Missing input: {e.filename}. See header for CSV format, or run --demo.")
