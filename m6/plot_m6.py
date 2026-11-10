"""M6 figures. Usage: python m6/plot_m6.py data_external/guangdong m6/results
Re-runs run_m6.py (deterministic, rewrites identical results) to reuse its loaders and model."""
import sys, os, runpy, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression

OUT = sys.argv[2]
sys.argv = [os.path.join(os.path.dirname(__file__), 'run_m6.py')] + sys.argv[1:]
ns = runpy.run_path(sys.argv[0])
S, D, res, phys, X = ns['S'], ns['D'], ns['res'], ns['phys'], ns['X']

def pred_fig(name, tr, te, fname, title):
    p = res[name]['params_a_n_tau']  # rounded to 4 dp; fine for plotting
    Xtr = np.vstack([X(s)[s['win']] for s in S[tr]]); ytr = np.concatenate([s['y'][s['win']] for s in S[tr]])
    lr = LinearRegression().fit(Xtr[:, :1], ytr)
    gb = GradientBoostingRegressor(random_state=17).fit(Xtr, ytr)
    fig, ax = plt.subplots(5, 1, figsize=(9, 12), sharex=False)
    for a, s in zip(ax, S[te]):
        w = s['win']; t = s['t'][w]
        a.plot(t, s['y'][w], 'k', lw=2, label='measured ΔPWP')
        a.plot(t, phys(p, s)[w], label='M6')
        a.plot(t, lr.predict(X(s)[w][:, :1]), label='B1 linear')
        a.plot(t, gb.predict(X(s)[w]), label='B2 GBR')
        a.set_ylabel(f"{s['k']}# ΔPWP (kPa)")
    ax[0].legend(fontsize=8, ncol=4); ax[0].set_title(title); ax[-1].set_xlabel('time since rain start (min)')
    fig.tight_layout(); fig.savefig(f'{OUT}/{fname}', dpi=110); plt.close(fig)

pred_fig('A_fit_T1_predict_T2', 'T1', 'T2', 'm6_fig1_T2_pred.png', 'Sandstone (T2), models fit on granite (T1)')
pred_fig('B_fit_T2_predict_T1', 'T2', 'T1', 'm6_fig2_T1_pred.png', 'Granite (T1), models fit on sandstone (T2)')

fig, ax = plt.subplots(2, 2, figsize=(12, 7))
for j, (key, lab) in enumerate([('T1', 'Granite (T1)'), ('T2', 'Sandstone (T2)')]):
    V, P = D[key]; t = np.arange(len(V))*ns['DT']
    for k in range(5):
        ax[0, j].plot(t, V[:, k], label=f'{k+1}#'); ax[1, j].plot(t, P[:, k], label=f'{k+1}#')
    for a in ax[:, j]:
        if key == 'T1': a.axvline(282, color='r', ls='--')
        else:
            for f in (19, 41, 47, 64): a.axvline(f, color='r', ls='--')
            a.axvspan(85, 90, color='r', alpha=0.2)
    ax[0, j].set_title(lab + ', red = failure'); ax[0, j].set_ylabel('VWC (%)'); ax[1, j].set_ylabel('PWP (kPa)')
    ax[1, j].set_xlabel('time since rain start (min)'); ax[0, j].legend(fontsize=8)
fig.tight_layout(); fig.savefig(f'{OUT}/m6_fig3_vwc_pwp.png', dpi=110); plt.close(fig)
print('figures written to', OUT)
