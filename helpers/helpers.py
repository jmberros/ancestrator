def percentage_fmt(ratio):
    return '{0:.1f}%'.format(100 * ratio)


def hide_spines_and_ticks(ax, spines=["top", "right", "left"]):
    if spines == "all":
        spines = ["top", "bottom", "right", "left"]

    for spine in spines:
        ax.spines[spine].set_visible(False)

    ax.set_xticks([])
    ax.set_yticks([])
