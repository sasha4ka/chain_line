# Chain Line Simulation

A small Pygame app that draws a hanging chain between two draggable endpoints. It finds the catenary curve whose arc length matches the selected chain length.

## Run

Requires Python 3.12 or newer. Install the project dependencies and start the app:

```bash
uv sync
uv run python main.py
```

Drag with the left mouse button to move an endpoint. Use the mouse wheel to change the chain length $L$ in 10-pixel steps. The information panel shows $L$, the endpoint distance, and the calculated curve parameters. If a curve cannot span the endpoints, it prompts you to increase $L$.

## How the solution is found

The solver models the chain as a catenary. Because Pygame's screen $y$-axis increases downward, the rendered curve is written as

$$
y(x)=-a\cosh\left(\frac{x+c}{a}\right)+\sigma,
$$

where $a>0$ controls the curve's shape, $c$ shifts it horizontally, and $\sigma$ shifts it vertically.

1. **Order the endpoints left to right.** Let their coordinates be $(x_L,y_L)$ and $(x_R,y_R)$. Define the horizontal span $H=x_R-x_L>0$, the signed height difference $v=y_R-y_L$, and the straight-line distance
   $$D=\sqrt{H^2+v^2}.$$

2. **Check whether the chain can span them.** A chain must be longer than the endpoint distance for a curved solution: $L>D$. If $H=0$ or $L\le D$, this solver leaves the curve undefined; the UI asks for a longer chain. At $L=D$, the limiting shape is a straight line rather than a finite catenary.

3. **Reduce the arc-length equation to one unknown.** Set $k=H/(2a)$. Integrating the catenary's arc length and combining it with the endpoint height difference gives
   $$\frac{\sinh k}{k}=\frac{\sqrt{L^2-v^2}}{H}=\frac{\sqrt{(L-|v|)(L+|v|)}}{H}.$$
   For a feasible curved chain, the right-hand side is greater than 1.

4. **Solve for $k$ numerically.** The function $\sinh(k)/k$ increases from 1 for $k>0$, so `solve_k` uses bisection: it expands an upper bound until it brackets the target, then repeatedly halves the interval. It evaluates the logarithm of the function (with a small-$k$ series) to avoid overflow and loss of precision.

5. **Recover the curve parameters.** Once $k$ is known, calculate
   $$a=\frac{H}{2k},\qquad t=\operatorname{asinh}\left(-\frac{v}{2a\sinh k}\right),$$
   $$c=at-\frac{x_L+x_R}{2},\qquad \sigma=y_L+a\cosh\left(\frac{x_L+c}{a}\right).$$
   These choices make the curve pass through both endpoints while using the selected arc length.

6. **Draw the result.** The app samples $y(x)$ at evenly spaced horizontal positions between the endpoints and draws the resulting points as a polyline.
