"""M6: physics-aware virtual PWP sensor, blind transfer granite <-> sandstone.
Plan: m6_plan.md. Usage: python run_m6.py <dir containing extracted 01_Granite_slope/ and 02_Sandstone_Slope/>"""
import sys, json, numpy as np, pandas as pd
from scipy.optimize import least_squares
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
R = sys.argv[1]; OUT = sys.argv[2] if len(sys.argv) > 2 else '.'
DT = 10/60  # min

def load():
    g = R+'/01_Granite_slope/01_Data/0_Sensors/'
    vg = pd.read_csv(g+'VWC&EP_gr/Gr_medifilt_vwcdata10hz.csv', header=None)
    vg = vg.groupby(np.arange(len(vg))//100).mean().values
    pg = pd.read_csv(g+'PWP_gr/Gr_meanfilt_pwpdata_0.1hz.csv', header=None).values
    s = R+'/02_Sandstone_Slope/02_sanstone_Data/0_Sensors/'
    vs = pd.read_csv(s+'VWC&EP_Ss/Sandstone_data_vwc_mean(1hz).csv', header=None)
    vs = vs.groupby(np.arange(len(vs))//10).mean().values
    ps = pd.read_csv(s+'PWP_Ss/Ss_meanfilt_pwpdata_0.1hz.csv', header=None).values[:, [0, 2, 1, 3, 4]]
    n = min(len(vg), len(pg)); m = min(len(vs), len(ps))
    return {'T1': (vg[:n], pg[:n]), 'T2': (vs[:m], ps[:m])}

def prep(name, V, P):
    t = np.arange(len(V))*DT; sens = []
    for k in range(5):
        th, u = V[:, k], P[:, k]; th0, u0 = th[:12].mean(), u[:12].mean()
        run = np.maximum.accumulate(th)
        if name == 'T1': win = t <= 280
        else:
            bad = (t > 90) | (th < run - 5) | (th < 5)
            stop = np.argmax(bad) if bad.any() else len(t)
            win = np.arange(len(t)) < stop
        S = np.where(run - th0 >= 3, np.clip((th - th0)/np.maximum(run - th0, 1e-6), 0, 1), 0.0)
        sens.append(dict(k=k+1, t=t, d=th - th0, S=S, y=u - u0, win=win))
    return sens

def phys(p, s):
    a, n, tau = p; h = np.zeros(len(s['S']))
    for i in range(1, len(h)):
        h[i] = max(h[i-1] + DT*(a*s['S'][i-1]**n - h[i-1]/tau), 0)
    return h

def fit_phys(tr):
    f = lambda p: np.concatenate([(phys(p, s) - s['y'])[s['win']] for s in tr])
    best = None
    for x0 in ([0.05, 4, 30], [0.01, 2, 200], [0.2, 10, 10]):
        r = least_squares(f, x0, bounds=([0, 1, 1], [1, 20, 1000]))
        if best is None or r.cost < best.cost: best = r
    return best.x

def X(s): return np.c_[s['d'], s['S'], s['t']]

def run(train, test):
    p = fit_phys(train)
    Xtr = np.vstack([X(s)[s['win']] for s in train]); ytr = np.concatenate([s['y'][s['win']] for s in train])
    lr = LinearRegression().fit(Xtr[:, :1], ytr)
    gb = GradientBoostingRegressor(random_state=17).fit(Xtr, ytr)
    rows, err = [], {m: [] for m in ['M6', 'B0', 'B1', 'B2']}
    for s in test:
        w = s['win']; y = s['y'][w]
        pred = {'M6': phys(p, s)[w], 'B0': np.zeros_like(y), 'B1': lr.predict(X(s)[w][:, :1]), 'B2': gb.predict(X(s)[w])}
        r = {'sensor': f"{s['k']}#", 'n': int(w.sum()), 'window_min': round(w.sum()*DT, 1)}
        for m, z in pred.items():
            err[m].append(z - y); r[m] = float(np.sqrt(np.mean((z - y)**2)))
        rows.append(r)
    pooled = {m: float(np.sqrt(np.mean(np.concatenate(e)**2))) for m, e in err.items()}
    return p, pd.DataFrame(rows), pooled

D = load(); S = {k: prep(k, *v) for k, v in D.items()}
res = {}
for name, tr, te in [('A_fit_T1_predict_T2', 'T1', 'T2'), ('B_fit_T2_predict_T1', 'T2', 'T1')]:
    p, tab, pooled = run(S[tr], S[te])
    tab.round(3).to_csv(f'{OUT}/m6_{name}_per_sensor.csv', index=False, lineterminator='\n')
    win = pooled['M6'] < min(pooled['B0'], pooled['B1'], pooled['B2'])
    res[name] = dict(params_a_n_tau=[round(float(x), 4) for x in p], pooled_rmse=pooled, m6_wins=bool(win))
    print(name, 'a,n,tau =', np.round(p, 4)); print(tab.round(3).to_string(index=False)); print('pooled', {k: round(v, 3) for k, v in pooled.items()}, 'M6 wins:', win)
wins = sum(r['m6_wins'] for r in res.values())
res['gate'] = 'PASS' if wins == 2 else 'PARTIAL' if wins == 1 else 'FAIL'
print('GATE', res['gate'])
json.dump(res, open(f'{OUT}/m6_gate_result.json', 'w'), indent=2)
