"""Tkinter window listing devices on the local network."""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, ttk

from .router import PlaceholderRouter, RouterAdapter, RouterNotConfigured
from .scanner import Device, local_network, scan

COLUMNS = (("name", "اسم الجهاز", 240), ("ip", "عنوان IP", 140), ("mac", "عنوان MAC", 170))


class App(tk.Tk):
    def __init__(self, router: RouterAdapter | None = None) -> None:
        super().__init__()
        self.router = router or PlaceholderRouter()
        self.devices: dict[str, Device] = {}
        self.title("الأجهزة المتصلة بالشبكة")
        self.geometry("620x440")
        self.minsize(520, 300)

        bar = ttk.Frame(self, padding=8)
        bar.pack(fill="x")
        self.scan_btn = ttk.Button(bar, text="فحص الشبكة", command=self.start_scan)
        self.scan_btn.pack(side="right")
        self.block_btn = ttk.Button(bar, text="إيقاف الاتصال", command=lambda: self.router_action(True))
        self.block_btn.pack(side="right", padx=6)
        self.unblock_btn = ttk.Button(bar, text="إعادة الاتصال", command=lambda: self.router_action(False))
        self.unblock_btn.pack(side="right")
        self.status = tk.StringVar(value=f"الراوتر: {self.router.name}")
        ttk.Label(bar, textvariable=self.status, anchor="w").pack(side="left", fill="x", expand=True)

        self.tree = ttk.Treeview(self, columns=[c[0] for c in COLUMNS], show="headings", selectmode="browse")
        for key, label, width in COLUMNS:
            self.tree.heading(key, text=label)
            self.tree.column(key, width=width, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.tree.bind("<<TreeviewSelect>>", lambda _e: self._update_buttons())
        self._update_buttons()
        self.after(100, self.start_scan)

    def _selected(self) -> Device | None:
        sel = self.tree.selection()
        return self.devices.get(sel[0]) if sel else None

    def _update_buttons(self) -> None:
        dev = self._selected()
        state = "normal" if dev and dev.mac and not dev.is_this_pc else "disabled"
        self.block_btn.configure(state=state)
        self.unblock_btn.configure(state=state)

    def start_scan(self) -> None:
        self.scan_btn.configure(state="disabled")
        try:
            net = local_network()
        except OSError:
            self.status.set("تعذّر تحديد الشبكة المحلية. تأكد من الاتصال بالواي فاي.")
            self.scan_btn.configure(state="normal")
            return
        self.status.set(f"جارٍ فحص {net} ...")
        threading.Thread(target=self._scan_worker, args=(net,), daemon=True).start()

    def _scan_worker(self, net) -> None:
        try:
            devices = scan(net)
            self.after(0, self._show, devices, None)
        except Exception as exc:  # surface any OS/command failure in the window
            self.after(0, self._show, [], exc)

    def _show(self, devices: list[Device], error: Exception | None) -> None:
        self.scan_btn.configure(state="normal")
        if error:
            self.status.set(f"فشل الفحص: {error}")
            return
        self.tree.delete(*self.tree.get_children())
        self.devices.clear()
        for i, d in enumerate(devices):
            iid = str(i)
            self.devices[iid] = d
            name = d.name or "غير معروف"
            if d.is_this_pc:
                name += " (هذا الجهاز)"
            self.tree.insert("", "end", iid=iid, values=(name, d.ip, d.mac or "—"))
        self.status.set(f"عدد الأجهزة: {len(devices)}  ·  الراوتر: {self.router.name}")
        self._update_buttons()

    def router_action(self, block: bool) -> None:
        dev = self._selected()
        if not dev:
            return
        try:
            (self.router.block if block else self.router.unblock)(dev.mac)
        except RouterNotConfigured as exc:
            messagebox.showinfo("الراوتر غير مُعدّ", str(exc))
            return
        messagebox.showinfo("تم", "تم إيقاف الاتصال." if block else "تمت إعادة الاتصال.")


def main() -> None:
    App().mainloop()
