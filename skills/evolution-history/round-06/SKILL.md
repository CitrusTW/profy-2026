---
name: economic-dispatch
description: "Minimize generator operating costs with energy dispatch, DC network limits, spinning reserves and capacity coupling; report dispatch, costs and uncommitted operating margin."
---

# Economic Dispatch

## 1. Load once; classify before solving
Parse the input with `json.load`; print only dimensions, total demand, reserve requirement and cost coefficient ranges. Never dump a large network into context. Use the supplied network-model instructions for nodal balance, reference angles and branch limits; total balance alone is insufficient for DC-OPF. Map bus IDs to indices, never subtract one.

MATPOWER generator columns: bus=0, status=7, Pmax=8, Pmin=9. Offline units have zero energy/reserve bounds. `gencost` columns: model=0, coefficient count=3, coefficients=4 onward, highest degree first. Use the active-power cost rows, one per generator. Startup/shutdown are not hourly dispatch costs.

For polynomial model 2, NCOST=3 gives `(c2,c1,c0)`, 2 gives `(0,c1,c0)`, 1 gives `(0,0,c0)`. Do not treat higher-degree polynomials as quadratics. For piecewise-linear model 1 see `references/cost-functions.md` in supplied files, or the attached `cost-functions.md` reference in native execution; load only when needed.

## 2. Formulate once, in MW
With coefficient arrays and effective online bounds:
```python
P = cp.Variable(ng)
R = cp.Variable(ng)
constraints = [P >= pmin, P <= pmax, R >= 0,
               R <= reserve_capacity, P + R <= pmax,
               cp.sum(R) >= reserve_requirement]
objective = c1 @ P + c0.sum()
if np.any(c2 != 0):
    objective += cp.sum(cp.multiply(c2, cp.square(P)))
```
Add nodal constraints using `P/baseMVA` when the network matrices are per-unit. Reserve capacity and requirement are MW; no double conversion. If reserves have no cost or other minimum allocations, schedule exactly the requirement as a tie-break to avoid arbitrary excess reserves. Preserve the inequality when other reserve rules require it.

## 3. Route directly to the right solver
All `c2 == 0`: omit quadratic expressions and solve the LP directly:
```python
prob = cp.Problem(cp.Minimize(objective), constraints)
prob.solve(solver=cp.SCIPY, scipy_options={
    'method': 'highs-ds', 'primal_feasibility_tolerance': 1e-9,
    'dual_feasibility_tolerance': 1e-9})
```
Genuine convex quadratics (`c2 >= 0`): use CLARABEL. Negative quadratic coefficients need a nonconvex solver, not silent convexification.

Use available imports; install only missing dependencies. If installation is needed, use a session-local virtual environment rather than modifying protected system packages. A prior system install failed on permissions.

## 4. Validate and report once
A prior large LP returned CLARABEL `optimal_inaccurate` with MW-scale violations; HiGHS solved it accurately. Status alone is not validation. Check nodal residuals, bounds, line limits, reserve adequacy and `P+R<=Pmax` numerically before export. Reject material violations; do not clip them away. Do not routinely solve the same optimization twice.

Compute cost from coefficients and solved MW outputs. Keep enough dispatch precision for balance; round currency to cents. Generator IDs are original row index + 1. Report each unit's bus, output_MW, reserve_MW, pmax_MW; totals are cost_dollars_per_hour, load_MW, generation_MW, reserve_MW. Rank in-service finite-rated lines by `100*abs(flow_MW)/RATE_A`; return the top three endpoints and loading_pct. Operating margin is `sum(effective_online_Pmax - P - R)`, not headroom before reserves. Follow the requested output schema exactly.
