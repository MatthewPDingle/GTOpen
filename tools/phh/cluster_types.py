"""How many player types does the data support? Unsupervised clustering of
per-player stats (PHH micro pool), compared with the hand-set VPIP/PFR bands.

Usage: python cluster_types.py stats_micro.json [--size fr] [--min-hands 1500]
"""
import sys, json, math, argparse, collections
import numpy as np
sys.path.insert(0, r"T:\Dev\GTOpen\tools\phh")
import report_phh as R
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

ap = argparse.ArgumentParser()
ap.add_argument('stats')
ap.add_argument('--size', default='fr')
ap.add_argument('--min-hands', type=int, default=1500)
args = ap.parse_args()

data = json.load(open(args.stats))
players = data['players']
rows, types, hands = [], [], []
PRE = ['vpip', 'pfr', 'open_limp', 'threebet', 'fold_vs_raise_cold', 'fold_to_3bet']
POST = ['cbet_flop', 'fold_vs_bet_flop', 'raise_vs_bet_flop', 'stab_flop', 'fold_vs_bet_turn']
FEATS = PRE + POST
for pid, p in players.items():
    meta = p.get(R.key('meta'), {})
    if meta.get(args.size, 0) < 0.6 * max(sum(meta.values()), 1):
        continue
    s = R.player_stats(p)
    if s['hands'] < args.min_hands:
        continue
    rows.append([s.get(f) if s.get(f) is not None else np.nan for f in FEATS])
    types.append(R.classify(s['vpip'], s['pfr']))
    hands.append(s['hands'])
X = np.array(rows, dtype=float)
types = np.array(types)
print(f"{len(X)} players with >= {args.min_hands} hands ({args.size}), {sum(hands):,} hands")
# impute column medians
med = np.nanmedian(X, axis=0)
nan_frac = np.isnan(X).mean(axis=0)
for j in range(X.shape[1]):
    X[np.isnan(X[:, j]), j] = med[j]
print("missing before imputation:", ", ".join(f"{f} {100*v:.0f}%" for f, v in zip(FEATS, nan_frac)))

def sweep(Xs, label, ks=range(2, 11)):
    print(f"\n== {label}: k-means / GMM sweep ==")
    print(" k   R2(kmeans)  silhouette   GMM-BIC(k)")
    best = None
    sample = np.random.RandomState(0).choice(len(Xs), min(3000, len(Xs)), replace=False)
    tot = ((Xs - Xs.mean(0)) ** 2).sum()
    for k in ks:
        km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(Xs)
        r2 = 1 - km.inertia_ / tot
        sil = silhouette_score(Xs[sample], km.labels_[sample])
        gm = GaussianMixture(n_components=k, covariance_type='full', n_init=3, random_state=0).fit(Xs)
        bic = gm.bic(Xs)
        print(f"{k:2d}   {r2:8.3f}    {sil:8.3f}   {bic:12.0f}")
    return

sc_all = StandardScaler().fit(X)
Xs = sc_all.transform(X)
sweep(Xs, "all 11 features (preflop + postflop)")
Xp = StandardScaler().fit_transform(X[:, :len(PRE)])
sweep(Xp, "preflop only (6 features)")
Xv = StandardScaler().fit_transform(X[:, :2])
sweep(Xv, "VPIP/PFR only")

# how much of the postflop variance do the hand-set VPIP/PFR types explain?
print("\n== variance of each stat explained by the 9 hand-set VPIP/PFR types (eta^2) ==")
for j, f in enumerate(FEATS):
    col = X[:, j]
    grand = col.mean()
    ss_tot = ((col - grand) ** 2).sum()
    ss_between = sum(((col[types == t].mean() - grand) ** 2) * (types == t).sum() for t in set(types))
    print(f"  {f:20s} eta2 {ss_between / ss_tot:.2f}")

# describe a k=6 and k=8 solution on all features: centroids in raw units + cross-tab with hand-set types
for k in (5, 6, 8):
    km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(Xs)
    cent = sc_all.inverse_transform(km.cluster_centers_)
    order = np.argsort(-cent[:, 0])  # by vpip desc
    print(f"\n== k={k} on all features: centroids (raw %) ==")
    print("  n     " + " ".join(f"{f[:9]:>9s}" for f in FEATS) + "   dominant hand-set types")
    for c in order:
        m = km.labels_ == c
        ct = collections.Counter(types[m]).most_common(3)
        print(f"  {m.sum():5d} " + " ".join(f"{v:9.1f}" for v in cent[c]) + "   " + ", ".join(f"{t.split(' (')[0]} {n}" for t, n in ct))
