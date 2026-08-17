from pathlib import Path
 
import numpy as np
import matplotlib
 
matplotlib.use("Agg")  # write figures to disk without opening a window
import matplotlib.pyplot as plt


P0 = 0.5           # starting frequency of allele A
GENERATIONS = 100  # generations to simulate
N_POP = 20         # number of independent populations
N_SINGLE = 50      # population size for figure 1
SIZES = [10, 500]  # small vs large population size for figure 2
FIGURES_DIR = Path("figures")



def simulate_one(N, p0, generations, seed=0): # Simulate allele-frequency drift in a single population
    rng = np.random.default_rng(seed)
    freq = p0
    history = [freq]
    for _ in range(generations):
        copies = rng.binomial(2 * N, freq)  # next generation's count of allele A
        freq = copies / (2 * N)             # convert count back to a frequency
        history.append(freq)
    return history


def simulate_many(N, p0, generations, n_pop): # Run the single-population model n_pop times   
    return [simulate_one(N, p0, generations, seed=i) for i in range(n_pop)]


def summarize(trajectories): # Count how many populations fixed (=1), were lost (=0), or still vary  
    ends = [t[-1] for t in trajectories]
    return {
        "fixed": sum(1 for e in ends if e == 1.0),
        "lost": sum(1 for e in ends if e == 0.0),
        "segregating": sum(1 for e in ends if 0.0 < e < 1.0),
    }

# Figures

def plot_trajectories(trajectories, p0, title, out_path):    
    plt.figure(figsize=(9, 5))
    for traj in trajectories:
        plt.plot(traj, linewidth=1, alpha=0.7)
    plt.axhline(p0, color="black", linestyle="--", linewidth=0.8)  # starting freq
    plt.ylim(0, 1)
    plt.xlabel("generation")
    plt.ylabel("frequency of allele A")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_by_size(sizes, p0, generations, n_pop, out_path):    
    fig, axes = plt.subplots(1, len(sizes), figsize=(6 * len(sizes), 5), sharey=True)
    for ax, N in zip(axes, sizes):
        for traj in simulate_many(N, p0, generations, n_pop):
            ax.plot(traj, linewidth=1, alpha=0.7)
        ax.axhline(p0, color="black", linestyle="--", linewidth=0.8)
        ax.set_ylim(0, 1)
        ax.set_xlabel("generation")
        ax.set_title(f"N = {N}")
    axes[0].set_ylabel("frequency of allele A")
    fig.suptitle("Genetic drift in small vs big populations")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def main():
    FIGURES_DIR.mkdir(exist_ok=True)
 
    # Figure 1: divergence of many populations from the same starting point
    trajectories = simulate_many(N_SINGLE, P0, GENERATIONS, N_POP)
    plot_trajectories(
        trajectories, P0,
        f"Genetic drift on {N_POP} populations (N={N_SINGLE}, p0={P0})",
        FIGURES_DIR / "drift.png",
    )
    counts = summarize(trajectories)
    print(f"N={N_SINGLE}: {counts['fixed']} fixed, {counts['lost']} lost, "
          f"{counts['segregating']} still segregating "
          f"(after {GENERATIONS} generations)")
 
    # Figure 2: the effect of population size on the strength of drift
    plot_by_size(SIZES, P0, GENERATIONS, N_POP, FIGURES_DIR / "drift_by_N.png")
    for N in SIZES:
        counts = summarize(simulate_many(N, P0, GENERATIONS, N_POP))
        done = counts["fixed"] + counts["lost"]
        print(f"N={N}: {done}/{N_POP} populations fixed or lost")
 
    print(f"Figures written to {FIGURES_DIR}/")
 
 
if __name__ == "__main__":
    main()