"""Plotting functions for the multiple choice exam case study.
"""

import numpy as np
import matplotlib.pyplot as plt
from xarray import DataArray
import arviz.preview as az
from scipy.special import expit


def plot_logit(dt, title, xlab, var_y, var_x, guessprob=0):
    """Fit a logistic model to one item and plot posterior curves.

    Produces a two-panel figure: posterior (a, b) scatter (left) and
    logistic curves with observed data (right).

    Parameters
    ----------
    title : str
        Figure suptitle.
    xlab : str
        X-axis label for the curve panel.
    model : CmdStanModel
        Compiled Stan model expecting scalar parameters ``a``, ``b``
        (and optionally ``p0`` when *guessprob* is ``"estimated"``).
    var_y : array-like
        Observed data for one item.
    var_x : array-like
        X values (possibly jittered) for plotting observed data.
    guessprob : float or ``"estimated"``
        Guessing probability — 0, positive float, or ``"estimated"``.

    Returns
    -------
    datatree.DataTree
    """
    var_x = np.asarray(var_x, dtype=float)

    ab_sims = az.extract(dt, var_names=["a", "b"], num_samples=100)
    ab_sims_full = az.extract(dt, var_names=["a", "b"])
    if guessprob == "estimated":
        medians = az.median(dt, var_names=["a", "b", "p0"])
        p0_hat = medians["p0"].item() 
    else:
        medians = az.median(dt, var_names=["a", "b"])

    a_hat = medians["a"].item()
    b_hat = medians["b"].item()
  
    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    fig.suptitle(title)

    # ---- left panel: posterior (a, b) scatter ----------------------------
    ax = axes[0]
    ax.scatter(ab_sims_full["a"], ab_sims_full["b"], c="C1", s=1, alpha=0.3)
    ax.plot(a_hat, b_hat, "o", color="C0")
    ax.set(xlabel="a", ylabel="b")

    # ---- right panel: logistic curves ------------------------------------
    ax = axes[1]
    x_line = DataArray(np.linspace(var_x.min() - 1, var_x.max() + 1, 300), dims="x")

    if guessprob == "estimated":
        y_sims = p0_hat + (1 - p0_hat) * expit(ab_sims["a"] + ab_sims["b"] * x_line)
        ax.plot(
            x_line,
            y_sims.transpose("x", "sample"),
            color="C1", lw=0.5, alpha=0.3,
        )
        y_hat = p0_hat + (1 - p0_hat) * expit(a_hat + b_hat * x_line)
        ax.plot(
            x_line,
            y_hat,
            color="C0", lw=1.5,
        )
        label = (
            f"y = {f"{p0_hat:.2f}"} + {f"{1 - p0_hat:.2f}"} "
            f"invlogit({f"{a_hat:.2f}"} + {f"{b_hat:.2f}"} x)"
        )
        y_text = p0_hat + (1 - p0_hat) * expit(a_hat + b_hat * var_x.mean()) - 0.2
    else:
        gp = float(guessprob)
        y_sims = gp + (1 - gp) * expit(ab_sims["a"] + ab_sims["b"] * x_line)
        ax.plot(
                x_line,
                y_sims.transpose("x", "sample"),
                color="C1", lw=0.5, alpha=0.3,
            )
        y_hat = gp + (1 - gp) * expit(a_hat + b_hat * x_line)
        ax.plot(
            x_line,
            y_hat,
            color="C0", lw=1.5,
        )
        if gp == 0:
            label = f"y = invlogit({a_hat:.2f} + {b_hat:.2f} x)"
        else:
            label = (
                f"y = {gp} + {1 - gp} "
                f"invlogit({a_hat:.2f} + {b_hat:.2f} x)"
            )
        y_text = gp + (1 - gp) * expit(a_hat + b_hat * var_x.mean()) - 0.2

    ax.text(var_x.mean(), y_text, label, fontsize=8, color="C0")
    ax.scatter(var_x, 0.5 + 0.98 * (var_y - 0.5), s=15, c="black", zorder=5)
    ax.set(xlabel=xlab, ylabel="Pr (correct answer)", ylim=(0, 1))


def plot_logit_grid(title, xlab, model, data, var_x, item_id, guessprob):
    """Fit separate logistic regressions per item and show a 4×6 grid.

    Each item is fitted independently using *model*.  Items are ordered
    by ascending total-correct (easiest last).

    Parameters
    ----------
    title, xlab : str
    model : CmdStanModel
        Single-item model with scalar parameters ``a`` and ``b``.
    data : dict
        Must contain ``y`` as a 2-D array (J × K) — the *correct* matrix.
    var_x : array-like
    item_id : array-like
        Display labels for each item (length K).
    guessprob : float
    """
    var_x = np.asarray(var_x, dtype=float)
    correct_arr = np.asarray(data["y"])  # (J, K)
    item_order = np.argsort(correct_arr.sum(axis=0), kind="stable")

    fig, axes = plt.subplots(4, 6, figsize=(11, 6), sharex=True, sharey=True)
    fig.suptitle(title, fontsize=11, y=1.04)

    gp = float(guessprob)
    x_line = DataArray(np.linspace(var_x.min() - 1, var_x.max() + 1, 300), dims="x")

    for count, (k, ax) in enumerate(zip(item_order, axes.ravel())):

        data_k = {key: val for key, val in data.items() if key != "y"}
        data_k["y"] = correct_arr[:, k].tolist()

        fit_k = model.sample(data=data_k, show_progress=False)
        dt_k = az.from_cmdstanpy(fit_k)

        ab_sims = az.extract(dt_k, var_names=["a", "b"], num_samples=100)

        a_hat = float(np.median(ab_sims["a"]))
        b_hat = float(np.median(ab_sims["b"]))

        y_sims = gp + (1 - gp) * expit(ab_sims["a"] + ab_sims["b"] * x_line)
        ax.plot(
                x_line,
                y_sims.transpose("x", "sample"),
                color="C1", lw=0.5, alpha=0.3,
            )
        y_hat = gp + (1 - gp) * expit(a_hat + b_hat * x_line)
        ax.plot(
            x_line,
            y_hat,
            color="C0", lw=1.5,
        )

        y_k = correct_arr[:, k].astype(float)
        ax.scatter(var_x, 0.5 + 0.96 * (y_k - 0.5), s=15, c="black", zorder=5)

        ax.set_xlim(var_x.min(), var_x.max())
        ax.set_title(f"item {item_id[k]}", fontsize=8, pad=2)
        if count % 6 == 0:
            ax.set_yticks([])
        else:
            ax.set_yticks([0, 0.5, 1])

        if count < 18:
            ax.set_xticks([])
        else:
            ax.set_xticks([-2, -1, 0, 1, 2])
            ax.set_xlabel(xlab, fontsize=8)



def plot_logit_grid_2(dt, title, xlab, xvar, y_arr, item_arr, item_id, guessprob):
    """Plot per-item logistic curves from a multilevel model.

    Produces a 4×6 grid of per-item logistic curves (items ordered by
    ascending total-correct).

    Parameters
    ----------
    dt : datatree.DataTree
        Already-fitted ArviZ DataTree with vector parameters ``a[K]``
        and ``b[K]``.
    title, xlab : str
    xvar : array-like
        X values (one per student, possibly jittered) for scatter.
    y_arr : array-like
        Long-format binary responses (length N).
    item_arr : array-like
        Long-format item indices, 1-indexed (length N).
    item_id : array-like
        Display labels for each item (length K).
    guessprob : float

    Returns
    -------
    datatree.DataTree
    """
    xvar = np.asarray(xvar, dtype=float)
    y_arr = np.asarray(y_arr)
    item_arr = np.asarray(item_arr)

    K = int(item_arr.max())
    item_sums = np.array([y_arr[item_arr == k + 1].sum() for k in range(K)])
    item_order = np.argsort(item_sums, kind="stable")

    ab_sims = az.extract(dt, var_names=["a", "b"], num_samples=100)
    medians = az.median(dt, var_names=["a", "b"])
    a_sims = ab_sims["a"].values  # (K, 100)
    b_sims = ab_sims["b"].values  # (K, 100)
    a_hat = medians["a"].values   # (K,)
    b_hat = medians["b"].values   # (K,)

    # ---- grid of logistic curves ------------------------------------------
    fig, axes = plt.subplots(4, 6, figsize=(11, 6), sharex=True, sharey=True)
    fig.suptitle(title, fontsize=11, y=0.98)

    x_line = DataArray(np.linspace(xvar.min() - 1, xvar.max() + 1, 300), dims="x")
    gp = float(guessprob)

    for k, ax in zip(item_order, axes.ravel()):
        a_k = DataArray(a_sims[k], dims="sample")
        b_k = DataArray(b_sims[k], dims="sample")

        y_sims = gp + (1 - gp) * expit(a_k + b_k * x_line)
        ax.plot(
            x_line,
            y_sims.transpose("x", "sample"),
            color="C1", lw=0.5, alpha=0.3,
        )
        y_hat = gp + (1 - gp) * expit(a_hat[k] + b_hat[k] * x_line)
        ax.plot(
            x_line,
            y_hat,
            color="C0", lw=1.5,
        )

        mask = item_arr == (k + 1)
        y_k = y_arr[mask].astype(float)
        ax.scatter(xvar, 0.5 + 0.96 * (y_k - 0.5), s=15, c="black", zorder=5)

        ax.set_xlim(xvar.min(), xvar.max())
        ax.set_title(f"item {item_id[k]}", fontsize=8, pad=2)

    mad_ab = az.mad(dt, var_names=["a", "b"])
    se_a = mad_ab["a"].values
    se_b = mad_ab["b"].values

    _, ax = plt.subplots(figsize=(5, 4))
    ax.set_xlim(np.min(a_hat - se_a), np.max(a_hat + se_a))
    ax.set_ylim(np.min(b_hat - se_b), np.max(b_hat + se_b))
    ax.set_xlabel("a")
    ax.set_ylabel("b")
    ax.spines[["top", "right"]].set_visible(False)

    ax.errorbar(
        a_hat, b_hat, xerr=se_a, yerr=se_b,
        fmt="none", ecolor="C1", elinewidth=0.5, capsize=0,
    )
    for k in range(K):
        ax.text(
            a_hat[k], b_hat[k], str(item_id[k]),
            color="C0", fontsize=9, ha="center", va="center",
        )


    return dt


def plot_irt(dt, title, y_arr, item_arr, item_id, guessprob=0.25):
    """Plot per-item IRT response curves from a pre-fit model.

    Parameters
    ----------
    dt : datatree.DataTree
        Already-fitted ArviZ DataTree with parameters ``alpha[J]``,
        ``beta[K]``, and optionally ``gamma[K]`` (discrimination).
    title : str
    y_arr : array-like
        Long-format binary responses (length N).
    item_arr : array-like
        Long-format item indices, 1-indexed (length N).
    item_id : array-like
        Display labels for each item (length K).
    guessprob : float

    Returns
    -------
    datatree.DataTree
    """
    y_arr = np.asarray(y_arr)
    item_arr = np.asarray(item_arr)
    K = int(item_arr.max())
    gp = float(guessprob)

    item_sums = np.array([y_arr[item_arr == k + 1].sum() for k in range(K)])
    item_order = np.argsort(item_sums, kind="stable")

    var_names = ["alpha", "beta"]
    try:
        az.extract(dt, var_names=["gamma"], num_samples=1)
        has_gamma = True
    except (KeyError, ValueError):
        has_gamma = False

    extract_vars = ["alpha", "beta", "gamma"] if has_gamma else ["alpha", "beta"]
    sims = az.extract(dt, var_names=extract_vars, num_samples=100)
    medians = az.median(dt, var_names=extract_vars)

    alpha_hat = medians["alpha"].values  # (J,)
    beta_sims = sims["beta"].values      # (K, 100)
    beta_hat = medians["beta"].values    # (K,)

    if has_gamma:
        gamma_sims = sims["gamma"].values   # (K, 100)
        gamma_hat = medians["gamma"].values # (K,)
    else:
        gamma_sims = np.ones_like(beta_sims)
        gamma_hat = np.ones(K)

    x_range = (alpha_hat.min(), alpha_hat.max())

    # ---- grid of item-response curves ------------------------------------
    ncols = 6
    nrows = int(np.ceil(K / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(11, 1.5 * nrows),
                             sharex=True, sharey=True)
    fig.suptitle(title, fontsize=11, y=0.98)
    for idx in range(K, nrows * ncols):
        r, c = divmod(idx, ncols)
        axes[r, c].set_visible(False)

    x_line = DataArray(np.linspace(x_range[0] - 1, x_range[1] + 1, 300), dims="x")

    for count, k in enumerate(item_order):
        row, col = divmod(count, ncols)
        ax = axes[row, col]

        g_k = DataArray(gamma_sims[k], dims="sample")
        b_k = DataArray(beta_sims[k], dims="sample")

        y_sims = gp + (1 - gp) * expit(g_k * (x_line - b_k))
        ax.plot(
            x_line,
            y_sims.transpose("x", "sample"),
            color="C1", lw=0.5, alpha=0.3,
        )
        ax.plot(
            x_line,
            gp + (1 - gp) * expit(gamma_hat[k] * (x_line - beta_hat[k])),
            color="C0", lw=1.5,
        )

        mask = item_arr == (k + 1)
        y_k = y_arr[mask].astype(float)
        ax.scatter(
            alpha_hat, 0.5 + 0.96 * (y_k - 0.5),
            s=15, c="black", zorder=5,
        )

        ax.set_xlim(x_range)
        ax.set_title(f"item {item_id[k]}", fontsize=8, pad=2)

    return dt
