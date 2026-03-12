"""Utilities for reading RFID input from HID keyboard-wedge devices."""

from __future__ import annotations

import time
from typing import Callable


class HIDWedgeListener:
    """Capture keystrokes and emit completed tags when Enter is pressed."""

    def __init__(
        self,
        widget,
        on_tag: Callable[[str], None],
        idle_reset_seconds: float = 1.5,
        capture_all: bool = False,
    ):
        self.widget = widget
        self.on_tag = on_tag
        self.idle_reset_seconds = idle_reset_seconds
        self.capture_all = capture_all
        self.buffer = []
        self.last_key_time = 0.0
        self._binding_id = None
        self._active = False
        self._binding_target = widget

    def start(self):
        """Start listening for keypress events."""
        if self._active:
            return
        if self.capture_all:
            self._binding_target = self.widget.winfo_toplevel()
            self._binding_id = self._binding_target.bind("<KeyPress>", self._on_keypress, add="+")
        else:
            self._binding_target = self.widget
            self._binding_id = self._binding_target.bind("<KeyPress>", self._on_keypress, add="+")
        self._active = True

    def stop(self):
        """Stop listening for keypress events."""
        if not self._active:
            return
        if self._binding_id:
            self._binding_target.unbind("<KeyPress>", self._binding_id)
        self._binding_id = None
        self._active = False
        self.buffer = []

    def _on_keypress(self, event):
        now = time.monotonic()
        if self.last_key_time and (now - self.last_key_time) > self.idle_reset_seconds:
            self._flush_buffer()
        self.last_key_time = now

        if event.keysym in ("Return", "KP_Enter"):
            self._flush_buffer()
            return

        if event.keysym == "BackSpace":
            if self.buffer:
                self.buffer.pop()
            return

        if event.keysym in ("Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R"):
            return

        if event.char and len(event.char) == 1 and event.char.isprintable():
            self.buffer.append(event.char)

    def _flush_buffer(self):
        """Emit current buffered tag (if present) and clear it."""
        value = "".join(self.buffer).strip()
        self.buffer = []
        if value:
            self.on_tag(value)
