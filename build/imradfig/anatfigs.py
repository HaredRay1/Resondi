"""D2 the seven evaluated sites, P1 the planned nine-site protocol."""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "fig"))
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from lung_fig import anterior, posterior
from theme import save

OUT = os.path.join(HERE, "..", "..", "figures") + os.sep


def d2_seven_sites():
    """The protocol as evaluated: tracheal reference, then six lung fields.

    lung_fig.anterior/posterior draw exactly this scheme (Tc, 1-4 front and side,
    5-6 back), the same one the concept note shows in Figure 5.
    """
    fig = plt.figure(figsize=(6.0, 3.6), dpi=300)
    gs = GridSpec(1, 2, wspace=0.02, left=0.01, right=0.99,
                  top=0.99, bottom=0.01)
    anterior(fig.add_subplot(gs[0, 0]))
    posterior(fig.add_subplot(gs[0, 1]))
    save(fig, OUT + "d2_seven_sites.png")


def p1_nine_sites():
    fig = plt.figure(figsize=(6.0, 3.6), dpi=300)
    gs = GridSpec(1, 2, wspace=0.02, left=0.01, right=0.99,
                  top=0.99, bottom=0.01)
    anterior(fig.add_subplot(gs[0, 0]))
    posterior(fig.add_subplot(gs[0, 1]), nine=True)
    save(fig, OUT + "p1_nine_sites.png")


def h1_heart_sites():
    from heart_fig import chest
    fig = plt.figure(figsize=(5.0, 5.2))
    chest(fig.add_axes([0.02, 0.02, 0.96, 0.96]), app=True)
    fig.savefig(OUT + "h1_heart_sites.png", dpi=300, bbox_inches="tight", pad_inches=0.10, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    d2_seven_sites()
    p1_nine_sites()
    h1_heart_sites()
