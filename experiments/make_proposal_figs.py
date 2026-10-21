"""Figures for the Mitou Advanced proposal (detail document v16).

fig-proposal-1-concept.png : where the method's section prices go, and why delay and cause sit in different places
fig-proposal-2-smat-fleet.png : prototype 1 (U-FAST, SMAT2022, 30,000 jobs/h, seed 0): replay screen at 800 vehicles,
                                and fleet size vs transports completed in 1 h
Data for figure 2 come from smat-combined-2026-09-22.txt and smat-dense-2026-09-22.txt; the screen is
replay-occ-static-800-frame45.png (render_occupancy.py).

Run (from experiments/):  .venv/Scripts/python.exe make_proposal_figs.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Rectangle

font_manager.fontManager.addfont(r"C:\Windows\Fonts\BIZ-UDGothicR.ttc")
plt.rcParams["font.family"] = "BIZ UDGothic"
plt.rcParams["font.size"] = 8

INK, BLUE, ORANGE, RED, GRAY = "#222222", "#1f5fa8", "#d9822b", "#c0392b", "#888888"


def box(ax, x, y, w, h, text, fc="white", ec=INK, lw=1.0, fs=7.8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.05",
                                fc=fc, ec=ec, lw=lw))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=INK, linespacing=1.25)


def arrow(ax, x0, y0, x1, y1, color=INK, ls="-", lw=1.0):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, linestyle=ls, shrinkA=0, shrinkB=0))


def fig_concept(path):
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.4, 2.3), gridspec_kw={"width_ratios": [1.0, 1.0]})
    for ax in (a, b):
        ax.set_xlim(-0.15, 10.15); ax.set_ylim(0, 6); ax.axis("off")

    # left: the three systems and where the prices go
    a.text(0.0, 5.6, "（左）本方式が値段を渡す先", fontsize=8.6, fontweight="bold")
    box(a, 0.0, 3.5, 2.9, 1.5, "生産管理\n（行き先）")
    box(a, 3.55, 3.5, 2.9, 1.5, "搬送管理\nシステム\n（時刻・経由地）")
    box(a, 7.1, 3.5, 2.9, 1.5, "車両制御\n（搬送装置\nメーカー）")
    arrow(a, 2.9, 4.25, 3.55, 4.25)
    arrow(a, 6.45, 4.25, 7.1, 4.25)
    box(a, 0.4, 0.3, 9.2, 1.3, "区画ごとのエージェント（MARL）\nほかの車に与えた遅れを費用に数え、値段を決める",
        fc="#e8f0fa", ec=BLUE, lw=1.3)
    arrow(a, 4.2, 1.6, 5.0, 3.5, color=BLUE, lw=1.4)
    a.text(3.4, 2.5, "期間中", color=BLUE, fontsize=7.6, ha="center")
    arrow(a, 6.4, 1.6, 8.5, 3.5, color=BLUE, ls="--", lw=1.2)
    a.text(8.95, 2.5, "将来", color=BLUE, fontsize=7.6, ha="center")

    # right: queue spills back; delay shows up upstream of the cause
    b.text(0.0, 5.6, "（右）遅れが出る区間と原因の区画のずれ", fontsize=8.6, fontweight="bold")
    y = 2.9
    b.plot([0.2, 8.4], [y, y], color=GRAY, lw=3, solid_capstyle="butt", zorder=1)
    b.plot([7.3, 8.4], [y + 1.3, y], color=GRAY, lw=3, zorder=1)
    b.annotate("", xy=(9.8, y), xytext=(8.4, y), arrowprops=dict(arrowstyle="-|>", color=GRAY, lw=2))
    for xs in (2.85, 5.55):
        b.plot([xs, xs], [y - 0.35, y + 0.35], color=INK, lw=0.8)
    for i, x in enumerate([0.7, 1.45, 2.2, 3.3, 4.05, 4.8, 6.0, 6.75, 7.5]):
        c = RED if i == 8 else INK
        b.add_patch(Rectangle((x - 0.25, y - 0.2), 0.5, 0.4, fc=c, ec=c, zorder=3))
    b.text(9.1, y + 1.2, "合流で\n先頭が\n止まる", color=RED, fontsize=7.2, ha="center", va="center")
    for x, lab in ((1.45, "区画A"), (4.05, "区画B"), (6.75, "区画C")):
        b.text(x, y - 0.5, lab, fontsize=7.6, ha="center", va="top")
    b.annotate("", xy=(0.3, 4.3), xytext=(5.45, 4.3), arrowprops=dict(arrowstyle="|-|", color=ORANGE, lw=1.1))
    b.text(2.9, 4.55, "遅れが出る区間（A・B）", color=ORANGE, fontsize=7.6, ha="center")
    b.annotate("", xy=(5.65, 1.35), xytext=(8.4, 1.35), arrowprops=dict(arrowstyle="|-|", color=RED, lw=1.1))
    b.text(7.0, 0.7, "原因の区画（C）", color=RED, fontsize=7.6, ha="center")
    b.text(0.0, 0.05, "追い越しできないため、\n詰まりが後ろへ伝わる", fontsize=7.2, ha="left", va="bottom", color=INK)

    fig.tight_layout(pad=0.3, w_pad=1.2)
    fig.savefig(path, dpi=300)
    plt.close(fig)


def fig_fleet(path):
    fleet = [400, 600, 800, 1000]
    static = [21679, 19033, 11238, 2837]
    dynamic = [15522, 18804, 15511, 9967]
    fig, (a, ax) = plt.subplots(1, 2, figsize=(6.4, 2.35), gridspec_kw={"width_ratios": [1.05, 1.0]})
    img = mpimg.imread("replay-occ-static-800-frame45.png")
    h = img.shape[0]
    a.imshow(img[int(h * 0.07):int(h * 0.895), :, :])
    a.axis("off")
    a.set_title("（左）静的な最短経路・800台の画面\n赤：同じ区間で30秒以上止まっている車", fontsize=7.6, loc="left")
    ax.set_title("（右）台数と1時間に運べた件数", fontsize=7.6, loc="left")
    ax.plot(fleet, static, "-o", color=BLUE, lw=1.6, ms=4, label="静的な最短経路")
    ax.plot(fleet, dynamic, "--s", color=ORANGE, lw=1.6, ms=4, label="U-FAST内蔵の渋滞回避")
    ax.set_xlabel("搬送車の台数", fontsize=8)
    ax.set_ylabel("運べた件数", fontsize=8)
    ax.set_xticks(fleet)
    ax.set_xlim(320, 1080)
    ax.set_ylim(0, 25000)
    ax.set_yticks([0, 5000, 10000, 15000, 20000])
    ax.set_yticklabels(["0", "5,000", "10,000", "15,000", "20,000"], fontsize=7.4)
    ax.tick_params(axis="x", labelsize=7.4)
    ax.grid(alpha=0.3)
    ax.legend(loc="lower left", frameon=False, fontsize=7.4)
    ax.text(0.99, 0.99, "要求3万件/時、試行は各1回", transform=ax.transAxes,
            ha="right", va="top", fontsize=7, color=GRAY)
    for x, s, d in zip(fleet, static, dynamic):
        up = 5 if s >= d else -12  # keep the higher line's label above and the lower one's below
        ax.annotate(f"{s:,}", (x, s), textcoords="offset points", xytext=(0, up), ha="center", fontsize=6.8, color=BLUE)
        ax.annotate(f"{d:,}", (x, d), textcoords="offset points", xytext=(0, -12 if up == 5 else 5), ha="center",
                    fontsize=6.8, color=ORANGE)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.tight_layout(pad=0.3, w_pad=1.0)
    fig.savefig(path, dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    fig_concept("fig-proposal-1-concept.png")
    fig_fleet("fig-proposal-2-smat-fleet.png")
    print("ok")
