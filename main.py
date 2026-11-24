# -*- coding: utf-8 -*-
"""
程序入口 · 窗口装配 · 执行状态机

作者：刘硕（@favor177，组长）
分支：main（通过 PR 合并）
职责：把 ui_layout、algo_binary、algo_hash、render 四块拼起来，
      并管理「单步 / 自动播放 / 重置」三个状态的切换。

这一份骨架的目标：python src/main.py 能弹出窗口，并画出初始画面。
算法还没实现时，页面显示空数组和空桶，这是正常的。
"""

from __future__ import annotations

import os
import sys
import tkinter as tk

# 让 `python src/main.py` 和 `python -m src.main` 都能找到同级模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ui_layout
import render
from algo_binary import binary_search_steps
from algo_hash import hash_search_steps

DEMO_ARRAY = [3, 8, 12, 19, 25, 31, 40, 47, 52, 60]
DEMO_KEYS = [34, 46, 25, 61, 72, 7, 18, 53]
HASH_SIZE = 11


class App:
    """把四块拼起来的胶水层。"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.widgets = ui_layout.build_layout(root)

        # 当前状态
        self.b_steps: list[dict] = []
        self.h_steps: list[dict] = []
        self.cursor = 0            # 当前播到第几步
        self.playing = False
        self.after_id = None

        self.btn_step.configure(command=self.on_step)
        self.btn_auto.configure(command=self.on_auto)
        self.btn_reset.configure(command=self.on_reset)

        self.reset()

    # ---------- 数据准备 ----------
    def _prepare(self):
        """调用两个算法模块，拿到完整步骤序列。"""
        target = self._read_target()

        b = binary_search_steps(DEMO_ARRAY, target)
        h = hash_search_steps(DEMO_KEYS, target, HASH_SIZE)

        self.b_steps = b["steps"]
        self.h_steps = h["steps"]
        self.result_b = b
        self.result_h = h

        # TODO 1：用 h 的结果反推 buckets（每个桶里有哪些 key），
        #         或者让 algo_hash 额外返回 buckets，和组长商量后改接口

    def _read_target(self) -> int:
        try:
            return int(self.widgets["entry_target"].get())
        except ValueError:
            return 40

    # ---------- 三个按钮 ----------
    def on_step(self):
        """单步：前进一步，刷新画面。"""
        self.playing = False
        self._cancel_timer()
        if self.cursor < max(len(self.b_steps), len(self.h_steps)):
            self.cursor += 1
        self._render()

    def on_auto(self):
        """自动播放：每 500ms 走一步。"""
        self.playing = True
        self._tick()

    def on_reset(self):
        """重置：重新算一遍，回到第 0 步。"""
        self.playing = False
        self._cancel_timer()
        self.cursor = 0
        self.reset()

    # ---------- 内部 ----------
    def reset(self):
        self._prepare()
        self.widgets["log_text"].delete("1.0", "end")
        self._render()

        if not self.b_steps and not self.h_steps:
            self.widgets["log_text"].insert(
                "end", "提示：算法模块尚未实现，步骤序列为空。\n")

    def _tick(self):
        if not self.playing:
            return
        if self.cursor >= max(len(self.b_steps), len(self.h_steps)):
            self.playing = False
            return
        self.cursor += 1
        self._render()
        self.after_id = self.root.after(500, self._tick)

    def _cancel_timer(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

    def _render(self):
        """把第 cursor 步画出来。"""
        b_step = self.b_steps[self.cursor - 1] if 0 < self.cursor <= len(self.b_steps) else None
        h_step = self.h_steps[self.cursor - 1] if 0 < self.cursor <= len(self.h_steps) else None

        render.draw_array(self.widgets["canvas_binary"], DEMO_ARRAY, b_step)
        # TODO 2：这里需要 buckets，等 algo_hash 提供后替换下面这行
        render.draw_buckets(self.widgets["canvas_hash"], [[] for _ in range(HASH_SIZE)], h_step)

        # 日志
        if b_step:
            self.widgets["log_text"].insert("end", "[二分] " + b_step["message"] + "\n")
        if h_step:
            self.widgets["log_text"].insert("end", "[哈希] " + h_step["message"] + "\n")
        self.widgets["log_text"].see("end")


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()