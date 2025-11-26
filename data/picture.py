import matplotlib.pyplot as plt
import numpy as np

# === 全局字体设置 ===
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 18

# --- 数据 ---
levels = ["Level 0", "Level 1", "Level 2", "Level 3"]
avg_time = [0, 0.263, 3.845, 165.708]
cost = [0, 0.322, 0.527, 0.742]

time_std = [0, 0.129, 0.826, 117.628]
cost_std = [0, 0.026, 0.016, 0.059]

cumulative_block = [33.3, 72.2, 100, 100]
individual_block = [33.3, 38.9, 50, 27.8]

# --- Figure ---
fig, axes = plt.subplots(3, 1, figsize=(8, 9))
plt.subplots_adjust(hspace=0.8)

y_pos = np.arange(len(levels))
height = 0.6

# =====================================================
# (a) Average Time
# =====================================================
ax0 = axes[0]
ax0.barh(y_pos, avg_time, height=height, xerr=time_std, capsize=4,
         color="#4C72B0")

ax0.set_yticks(y_pos)
ax0.set_yticklabels(levels)
ax0.invert_yaxis()
ax0.grid(axis="x", linestyle="--", alpha=0.6)
ax0.set_xlim(left=0)

xmax = ax0.get_xlim()[1]
for i, v in enumerate(avg_time):
    text = f"{v:.3f} ± {time_std[i]:.3f}"
    
    text_x = v 
    print(i, v)
    if i == 0:
        ax0.text(text_x + 2.5, i, text, va="center", ha="left", fontsize=12)
    elif i == 1:
        ax0.text(text_x + 2.5, i, text, va="center", ha="left", fontsize=12)
    elif i == 2:
        ax0.text(text_x + 4, i, text, va="center", ha="left", fontsize=12)
    elif i == 3:
        ax0.text(xmax * 0.95 , i - 0.15 , text, va="center", ha="right", fontsize=12)

ax0.set_xlabel("(a) Average Time (milliseconds)", fontsize=20, labelpad=10)
### b
ax1 = axes[1]
ax1.barh(y_pos, cost, height=height, xerr=cost_std, capsize=4,
         color="#C0C0C0")

ax1.set_yticks(y_pos)
ax1.set_yticklabels(levels)
ax1.invert_yaxis()
ax1.grid(axis="x", linestyle="--", alpha=0.6)
ax1.set_xlim(left=0)

# --- 标注，防止越界 ---
xmax = ax1.get_xlim()[1]

for i, v in enumerate(cost):
    text = f"{v:.3f} ± {cost_std[i]:.3f}"
    x_offset = 0.05
    text_x = v + x_offset
    if i == 0:
        ax1.text(text_x - 0.04, i, text, va="center", ha="left", fontsize=12)
    elif i == 1:
        ax1.text(text_x - 0.01, i, text, va="center", ha="left", fontsize=12)
    elif i == 2:
        ax1.text(text_x - 0.02, i, text, va="center", ha="left", fontsize=12)
    elif i == 3:
        ax1.text(xmax * 0.95 + 0.03, i - 0.15 , text, va="center", ha="right", fontsize=12)

ax1.set_xlabel("(b) Average Cost (kB)", fontsize=20, labelpad=10)

# =====================================================
# (c) Detection Rate (improved layout)
# =====================================================
ax2 = axes[2]

# 柱子紧密排列：一个 Level 的绿色和红色上下紧贴
offset = 0.18   # 偏移量（越小柱子越紧密）

y_green = y_pos - offset
y_red   = y_pos + offset

# individual（绿）
bars_ind = ax2.barh(y_green, individual_block, height=0.35,
                    color="green", label="Individual")
for bar in bars_ind:
    bar.set_hatch("\\\\")

# cumulative（红）
bars_cum = ax2.barh(y_red, cumulative_block, height=0.35,
                    color="#E24A33", label="Cumulative")
for bar in bars_cum:
    bar.set_hatch("//")

# --- y轴标签放在两根柱子中间 ---
ax2.set_yticks(y_pos)
ax2.set_yticklabels(levels)

ax2.invert_yaxis()
ax2.grid(axis="x", linestyle="--", alpha=0.6)
ax2.set_xlim(0, 105)

# --- 数值标注 ---
for i, v in enumerate(individual_block):
    ax2.text(v + 0.5, y_green[i], f"{v:.1f}", fontsize=12, va="center")

for i, v in enumerate(cumulative_block):
    if i == 2 or i == 3:
        ax2.text(v , y_red[i], f"{v:}", fontsize=12, va="center")
    else:    
        ax2.text(v + 0.5, y_red[i], f"{v:.1f}", fontsize=12, va="center")

ax2.legend(loc="upper right", fontsize=10,frameon = False)
ax2.set_xlabel("(c) Detection Rate (%)", fontsize=20, labelpad=10)

# =====================================================
plt.tight_layout()
plt.savefig("fingerprint_levels_multipanel.png", dpi=800, bbox_inches="tight")
plt.show()
