import matplotlib.pyplot as plt
import numpy as np

# 原始数据
# 注意：Level 0 的 Time 和 Cost 均为 0，但 Detection Rate 为 33.3%
levels = ["Level 0", "Level 1", "Level 2", "Level 3"]
avg_time = [0, 0.263, 3.845, 165.708] # ms
cost = [0, 0.322, 0.527, 0.742]     # kb
block = [33.3, 72.2, 100, 100]      # %

# 标准差数据
time_std = [0, 0.129, 0.826, 117.628]
cost_std = [0, 0.026, 0.016, 0.059]
# Detection Rate 仍然假设没有标准差

# 绘图设置
fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(8, 8), sharex=False) # 调整 figsize 使 Level 0 有足够空间
plt.subplots_adjust(hspace=0.5) # 调整子图之间的垂直间距

# 为 y 轴标签创建索引（用于 barh）
y_pos = np.arange(len(levels))
height = 0.6 # 条形图的厚度

# --- 1. Average Time (ms) ---
ax0 = axes[0]
# barh 函数会自动处理 Level 0 的 0 值，它将绘制一个长度为 0 的条形图
ax0.barh(y_pos, avg_time, height=height, xerr=time_std, capsize=4, color="#4C72B0", error_kw={'elinewidth':1, 'capthick':1})
ax0.set_yticks(y_pos)
ax0.set_yticklabels(levels, fontsize=10)
ax0.set_title("Average Time (ms) ± Std Dev", loc='right', fontsize=12)
ax0.tick_params(axis='y', length=0)
ax0.invert_yaxis()  # 让 Level 0 在最上面
ax0.grid(axis='x', linestyle='--', alpha=0.6)
ax0.set_xlim(left=0) # X轴从0开始

# 标注数值 (平均值 ± 标准差)
for i, v in enumerate(avg_time):
    # 调整标注逻辑：对于 Level 0 (v=0)，将文本放在一个固定的、靠近轴的位置
    if v == 0:
        text_x = 2.0  # 稍微偏右一点的位置
        text_label = f"{v:.3f} ± {time_std[i]:.3f}"
    else:
        text_x = v + time_std[i] + 5
        text_label = f"{v:.3f} ± {time_std[i]:.3f}"

    ax0.text(text_x, i, text_label, color='black', va='center', ha='left', fontsize=8)


# --- 2. Average Cost (kb) ---
ax1 = axes[1]
ax1.barh(y_pos, cost, height=height, xerr=cost_std, capsize=4, color="#C0C0C0", error_kw={'elinewidth':1, 'capthick':1})
ax1.set_yticks(y_pos)
ax1.set_yticklabels(levels, fontsize=10)
ax1.set_title("Average Cost (kb) ± Std Dev", loc='right', fontsize=12)
ax1.tick_params(axis='y', length=0)
ax1.invert_yaxis()
ax1.grid(axis='x', linestyle='--', alpha=0.6)
ax1.set_xlim(left=0)

# 标注数值 (平均值 ± 标准差)
for i, v in enumerate(cost):
    if v == 0:
        text_x = 0.05 # 稍微偏右一点的位置
        text_label = f"{v:.3f} ± {cost_std[i]:.3f}"
    else:
        text_x = v + cost_std[i] + 0.02
        text_label = f"{v:.3f} ± {cost_std[i]:.3f}"
        
    ax1.text(text_x, i, text_label, color='black', va='center', ha='left', fontsize=8)


# --- 3. Detection Rate (%) ---
ax2 = axes[2]
ax2.barh(y_pos, block, height=height, color="#E24A33")
ax2.set_yticks(y_pos)
ax2.set_yticklabels(levels, fontsize=10)
ax2.set_title("Detection Rate (%)", loc='right', fontsize=12)
ax2.tick_params(axis='y', length=0)
ax2.invert_yaxis()
ax2.grid(axis='x', linestyle='--', alpha=0.6)
ax2.set_xlim(0, 105) # 将 X 轴上限设为略大于 100%

# 标注数值
for i, v in enumerate(block):
    ax2.text(v + 1, i, f"{v:.1f}", color='black', va='center', ha='left', fontsize=9)


# 调整子图间的间距
plt.tight_layout(pad=1.5)

# 保存和显示图像
plt.savefig("fingerprint_levels_multipanel.png", dpi=400, bbox_inches="tight", transparent=True)
plt.show()