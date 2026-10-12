"""Tkinter window listing devices on the local network."""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, ttk

from .router import ViewOnlyRouter, default_router
from .scanner import Device, local_network, scan

COLUMNS = (("name", "اسم الجهاز", 240), ("ip", "عنوان IP", 140), ("mac", "عنوان MAC", 170))


class App(tk.Tk):
    def __init__(self, router: ViewOnlyRouter | None = None) -> None:
        super().__init__()
        self.router = router or default_router()
        self.devices: dict[str, Device] = {}
        self.title("الأجهزة المتصلة بالشبكة")
        self.geometry("620x440")
        self.minsize(520, 300)

        bar = ttk.Frame(self, padding=8)
        bar.pack(fill="x")
        self.scan_btn = ttk.Button(bar, text="فحص الشبكة", command=self.start_scan)
        self.scan_btn.pack(side="right")
        self.router_btn = ttk.Button(bar, text="فتح صفحة الحظر في الراوتر", command=self.open_router_page)
        self.router_btn.pack(side="right", padx=6)
        self.status = tk.StringVar(value=f"الراوتر: {self.router.name}")
        ttk.Label(bar, textvariable=self.status, anchor="w").pack(side="left", fill="x", expand=True)

        self.tree = ttk.Treeview(self, columns=[c[0] for c in COLUMNS], show="headings", selectmode="browse")
        for key, label, width in COLUMNS:
            self.tree.heading(key, text=label)
            self.tree.column(key, width=width, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.after(100, self.start_scan)

    def _selected(self) -> Device | None:
        sel = self.tree.selection()
        return self.devices.get(sel[0]) if sel else None

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

    def open_router_page(self) -> None:
        """Copy the selected device's MAC, then open the router's admin page to block it there."""
        dev = self._selected()
        if dev and dev.mac and not dev.is_this_pc:
            self.clipboard_clear()
            self.clipboard_append(dev.mac)
            messagebox.showinfo(
                "الحظر من صفحة الراوتر",
                f"نُسخ عنوان MAC للجهاز ({dev.mac}).\n"
                "سجّل الدخول إلى صفحة الراوتر، ثم الصقه في قائمة تصفية MAC (القائمة السوداء) "
                "لإيقاف اتصاله، واحذفه منها لإعادة الاتصال.",
            )
        self.router.open_admin_page()


def main() -> None:
    App().mainloop()
