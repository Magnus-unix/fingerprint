import matplotlib.pyplot as plt
import numpy as np

levels = ["Level 1", "Level 2", "Level 3"]
avg_time = [0.415, 3.925, 313.645]
cost = [0.318, 0.502, 0.658]
block = [35, 68, 92]

# 归一化
time_pct = [t / max(avg_time) * 100 for t in avg_time]
cost_pct = [c / max(cost) * 100 for c in cost]
block_pct = block  # 已经是 %

x = np.arange(len(levels))
width = 0.25

fig, ax = plt.subplots(figsize=(8,5))

b1 = ax.bar(x - width, time_pct, width, color="#4C72B0", label="Time (ms)")
b2 = ax.bar(x, cost_pct, width, color="#C0C0C0", label="Cost (kb)")
b3 = ax.bar(x + width, block_pct, width, color="#E24A33", label="Bot Defense (%)")

# X轴
ax.set_xticks(x)
ax.set_xticklabels(levels)
ax.set_ylabel("Normalized Value (%)")
ax.set_ylim(0, 110)
ax.grid(axis='y', linestyle='--', alpha=0.5)

# 在柱子上标真实数值
for rects, values in zip([b1,b2,b3],[avg_time,cost,block]):
    for rect, val in zip(rects, values):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2, height + 2, f"{val}", ha="center", va="bottom", fontsize=9)

ax.legend(frameon=False)
plt.title("Fingerprint Levels: Performance and Defense Efficiency", fontsize=12, fontweight="bold")
plt.tight_layout()
plt.savefig("fingerprint_levels_normalized.png", dpi=400, bbox_inches="tight", transparent=True)
plt.show()
