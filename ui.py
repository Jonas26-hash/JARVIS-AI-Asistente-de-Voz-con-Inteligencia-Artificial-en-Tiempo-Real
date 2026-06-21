from __future__ import annotations
import importlib.util
import json
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent
_ORIG_PYC = _BASE_DIR / "ui.pyc"

# ── Load original compiled module ──
_orig_spec = importlib.util.spec_from_file_location("ui_orig", str(_ORIG_PYC))
_orig_mod  = importlib.util.module_from_spec(_orig_spec)
_orig_spec.loader.exec_module(_orig_mod)

# ── Kill the beta banner by replacing the method with a no-op ──
def _noop(self):
    pass

_orig_mod.MainWindow._build_beta_banner = _noop


def _install_futuristic_dashboard():
    """Attach lightweight dashboard docks without replacing the compiled UI."""
    try:
        from PyQt6.QtCore import Qt, QTimer
        from PyQt6.QtWidgets import (
            QDockWidget,
            QFrame,
            QGridLayout,
            QHBoxLayout,
            QLabel,
            QProgressBar,
            QPushButton,
            QScrollArea,
            QVBoxLayout,
            QWidget,
        )
    except Exception:
        return

    root = Path(__file__).resolve().parent
    memory_file = root / "memory" / "long_term.json"

    def _read_json(path, default):
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default

    def _panel(title, subtitle=""):
        frame = QFrame()
        frame.setObjectName("JarvisHudPanel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        head = QLabel(title)
        head.setObjectName("JarvisHudTitle")
        layout.addWidget(head)
        if subtitle:
            sub = QLabel(subtitle)
            sub.setObjectName("JarvisHudSubtitle")
            sub.setWordWrap(True)
            layout.addWidget(sub)
        return frame, layout

    def _metric(title, object_name, unit=""):
        frame = QFrame()
        frame.setObjectName(object_name)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        label = QLabel(title)
        label.setObjectName("JarvisMetricLabel")
        value = QLabel("--")
        value.setObjectName("JarvisMetricValue")
        bar = QProgressBar()
        bar.setObjectName(f"{object_name}Bar")
        bar.setRange(0, 100)
        bar.setTextVisible(False)
        layout.addWidget(label)
        layout.addWidget(value)
        layout.addWidget(bar)
        if unit:
            unit_label = QLabel(unit)
            unit_label.setObjectName("JarvisMetricUnit")
            layout.addWidget(unit_label)
        return frame, value, bar

    def _small_row(title, value="", object_name="JarvisInfoRow"):
        row = QFrame()
        row.setObjectName(object_name)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 9, 12, 9)
        left = QLabel(title)
        left.setObjectName("JarvisRowTitle")
        right = QLabel(value)
        right.setObjectName("JarvisRowValue")
        layout.addWidget(left, 1)
        layout.addWidget(right)
        return row

    def _command_button(text, route):
        button = QPushButton(text)
        button.setObjectName("JarvisHudButton")
        button.clicked.connect(lambda: getattr(button.window(), "_route_log", lambda _x: None)(route))
        return button

    def _build_dashboard(self):
        try:
            self.setDockOptions(self.dockOptions() | QDockWidget.DockOption.AllowTabbedDocks | QDockWidget.DockOption.AnimatedDocks)
        except Exception:
            pass

        style = """
        QDockWidget {
            color: #67e8f9;
            titlebar-close-icon: none;
            titlebar-normal-icon: none;
        }
        QDockWidget::title {
            text-align: left;
            padding: 8px 12px;
            color: #67e8f9;
            background: rgba(3, 12, 24, 0.94);
            border: 1px solid rgba(34, 211, 238, 0.28);
            letter-spacing: 2px;
        }
        #JarvisHudPanel {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(0, 20, 28, 0.90),
                stop:0.55 rgba(1, 8, 16, 0.92),
                stop:1 rgba(0, 28, 34, 0.78));
            border: 1px solid rgba(34, 211, 238, 0.38);
            border-radius: 20px;
        }
        #JarvisHudTitle {
            color: #e6fbff;
            font-size: 18px;
            font-weight: 700;
            letter-spacing: 4px;
        }
        #JarvisHudSubtitle, #JarvisMetricLabel {
            color: rgba(103, 232, 249, 0.75);
            font-size: 11px;
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        #JarvisMetricCpu, #JarvisMetricRam, #JarvisMetricDisk, #JarvisMetricTools {
            border-radius: 18px;
            min-height: 96px;
        }
        #JarvisMetricCpu {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(0, 20, 24, 0.92),
                stop:0.75 rgba(0, 8, 12, 0.90),
                stop:1 rgba(0, 188, 212, 0.24));
            border: 1px solid rgba(6, 182, 212, 0.55);
        }
        #JarvisMetricRam {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(0, 14, 25, 0.92),
                stop:0.75 rgba(0, 8, 16, 0.90),
                stop:1 rgba(59, 130, 246, 0.24));
            border: 1px solid rgba(59, 130, 246, 0.58);
        }
        #JarvisMetricDisk {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(25, 10, 0, 0.92),
                stop:0.75 rgba(10, 8, 6, 0.90),
                stop:1 rgba(249, 115, 22, 0.28));
            border: 1px solid rgba(249, 115, 22, 0.62);
        }
        #JarvisMetricTools {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(0, 22, 14, 0.92),
                stop:0.75 rgba(0, 10, 10, 0.90),
                stop:1 rgba(34, 197, 94, 0.25));
            border: 1px solid rgba(34, 197, 94, 0.58);
        }
        #JarvisMetricValue {
            color: #ffffff;
            font-size: 28px;
            font-weight: 700;
        }
        #JarvisMetricUnit {
            color: rgba(223, 251, 255, 0.70);
            font-size: 10px;
        }
        #JarvisMetricCpuBar::chunk { background: #06b6d4; border-radius: 4px; }
        #JarvisMetricRamBar::chunk { background: #3b82f6; border-radius: 4px; }
        #JarvisMetricDiskBar::chunk { background: #f97316; border-radius: 4px; }
        #JarvisMetricToolsBar::chunk { background: #22c55e; border-radius: 4px; }
        #JarvisHudButton {
            background: rgba(34, 211, 238, 0.08);
            color: #dffbff;
            border: 1px solid rgba(34, 211, 238, 0.38);
            border-radius: 14px;
            padding: 9px 12px;
            letter-spacing: 1px;
        }
        #JarvisHudButton:hover {
            background: rgba(34, 211, 238, 0.18);
            border-color: #67e8f9;
        }
        #JarvisMemoryRow, #JarvisInfoRow, #JarvisProcessRow, #JarvisSecurityRow {
            background: rgba(0, 0, 0, 0.26);
            border: 1px solid rgba(34, 211, 238, 0.16);
            border-radius: 12px;
            padding: 8px;
            color: #dffbff;
        }
        #JarvisMemoryRow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(34, 211, 238, 0.12),
                stop:1 rgba(0, 0, 0, 0.22));
        }
        #JarvisRowTitle {
            color: #e6fbff;
            font-weight: 700;
        }
        #JarvisRowValue {
            color: #22d3ee;
        }
        #JarvisSectionTitle {
            color: #ffffff;
            font-size: 15px;
            font-weight: 700;
            letter-spacing: 3px;
        }
        #JarvisProcessStatusOnline { color: #22d3ee; }
        #JarvisSecurityOk { color: #22c55e; }
        """
        self.setStyleSheet((self.styleSheet() or "") + style)

        # System analytics dock
        system_panel, system_layout = _panel("SYSTEM GRID", "REAL-TIME ANALYTICS")
        status_row = _small_row("SYSTEM STATUS", "ONLINE", "JarvisSecurityRow")
        system_layout.addWidget(status_row)
        metrics = QGridLayout()
        metrics.setSpacing(10)
        cpu_card, self._hud_cpu_value, self._hud_cpu_bar = _metric("CPU USAGE", "JarvisMetricCpu")
        ram_card, self._hud_ram_value, self._hud_ram_bar = _metric("RAM MEMORY", "JarvisMetricRam")
        disk_card, self._hud_disk_value, self._hud_disk_bar = _metric("STORAGE", "JarvisMetricDisk")
        tools_card, self._hud_tools_value, self._hud_tools_bar = _metric("TOOLS", "JarvisMetricTools")
        self._hud_metric_cards = [
            (cpu_card, self._hud_cpu_bar),
            (ram_card, self._hud_ram_bar),
            (disk_card, self._hud_disk_bar),
            (tools_card, self._hud_tools_bar),
        ]
        self._hud_palette_tick = 0
        metrics.addWidget(cpu_card, 0, 0)
        metrics.addWidget(ram_card, 0, 1)
        metrics.addWidget(disk_card, 1, 0)
        metrics.addWidget(tools_card, 1, 1)
        system_layout.addLayout(metrics)

        processes_title = QLabel("ACTIVE PROCESSES")
        processes_title.setObjectName("JarvisSectionTitle")
        system_layout.addWidget(processes_title)
        self._hud_process_list = QVBoxLayout()
        system_layout.addLayout(self._hud_process_list)

        net_title = QLabel("NETWORK")
        net_title.setObjectName("JarvisSectionTitle")
        system_layout.addWidget(net_title)
        self._hud_network_list = QVBoxLayout()
        system_layout.addLayout(self._hud_network_list)

        sec_title = QLabel("SECURITY")
        sec_title.setObjectName("JarvisSectionTitle")
        system_layout.addWidget(sec_title)
        self._hud_security_list = QVBoxLayout()
        system_layout.addLayout(self._hud_security_list)

        quick = QHBoxLayout()
        quick.addWidget(_command_button("SYSTEM", "__widget_show__:system"))
        quick.addWidget(_command_button("NOTES", "__widget_show__:notes"))
        quick.addWidget(_command_button("TODO", "__widget_show__:todo"))
        system_layout.addLayout(quick)
        self._hud_system_dock = QDockWidget("JARVIS SYSTEM DASHBOARD", self)
        self._hud_system_dock.setObjectName("JarvisSystemDashboardDock")
        self._hud_system_dock.setWidget(system_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._hud_system_dock)

        # Memory dock
        memory_panel, memory_layout = _panel("USER MEMORY")
        self._hud_memory_list = QVBoxLayout()
        memory_scroll_inner = QWidget()
        memory_scroll_inner.setLayout(self._hud_memory_list)
        memory_scroll = QScrollArea()
        memory_scroll.setWidgetResizable(True)
        memory_scroll.setFrameShape(QFrame.Shape.NoFrame)
        memory_scroll.setWidget(memory_scroll_inner)
        memory_layout.addWidget(memory_scroll)
        mem_buttons = QHBoxLayout()
        mem_buttons.addWidget(_command_button("ACTUALIZAR", "__hud_refresh__"))
        mem_buttons.addWidget(_command_button("NOTAS", "__widget_show__:notes"))
        memory_layout.addLayout(mem_buttons)
        self._hud_memory_dock = QDockWidget("JARVIS MEMORY", self)
        self._hud_memory_dock.setObjectName("JarvisMemoryDock")
        self._hud_memory_dock.setWidget(memory_panel)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._hud_memory_dock)

        self._hud_data = {}
        import threading as _th
        def _data_worker():
            import psutil as _ps
            while True:
                try:
                    self._hud_data["cpu"] = int(_ps.cpu_percent(interval=0))
                    self._hud_data["ram"] = int(_ps.virtual_memory().percent)
                    self._hud_data["disk"] = int(_ps.disk_usage(str(Path.home().anchor or Path.home())).percent)
                    procs = sorted(
                        [p.info for p in _ps.process_iter(["name", "memory_info", "status"]) if p.info.get("name")],
                        key=lambda item: getattr(item.get("memory_info"), "rss", 0),
                        reverse=True,
                    )[:4]
                    self._hud_data["processes"] = procs
                    net = _ps.net_io_counters()
                    self._hud_data["net_sent"] = f"{net.bytes_sent / (1024 ** 2):.0f} MB"
                    self._hud_data["net_recv"] = f"{net.bytes_recv / (1024 ** 2):.0f} MB"
                except Exception:
                    pass
                import time as _t
                _t.sleep(5)
        _th.Thread(target=_data_worker, daemon=True).start()

        self._hud_timer = QTimer(self)
        self._hud_timer.timeout.connect(lambda: _refresh_dashboard(self))
        self._hud_timer.start(1500)
        _refresh_dashboard(self)

    def _clear_layout(layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _init_dashboard_cache(win):
        if hasattr(win, "_hud_cache_ready"):
            return
        win._hud_memory_rows = []
        for cat, (title, desc) in {
            "identity": ("PERFIL", "Nombre, ciudad y datos basicos"),
            "preferences": ("GUSTOS", "Musica, colores, apps y preferencias"),
            "projects": ("PROYECTOS", "Cosas que estas creando"),
            "relationships": ("CONTACTOS", "Personas importantes"),
            "wishes": ("PLANES", "Ideas, compras y metas futuras"),
            "notes": ("NOTAS", "Detalles sueltos que conviene recordar"),
        }.items():
            row = QLabel(f"{title}  /  0\n{desc}")
            row.setWordWrap(True)
            row.setObjectName("JarvisMemoryRow")
            win._hud_memory_list.addWidget(row)
            win._hud_memory_rows.append(row)
        win._hud_memory_list.addStretch(1)

        win._hud_process_rows = []
        for _ in range(4):
            row = _small_row("", "", "JarvisProcessRow")
            win._hud_process_list.addWidget(row)
            win._hud_process_rows.append(row)

        win._hud_network_rows = []
        for label in ("Download", "Upload"):
            row = _small_row(label, "--", "JarvisInfoRow")
            win._hud_network_list.addWidget(row)
            win._hud_network_rows.append(row)

        win._hud_security_rows = []
        for label in ("Firewall", "Threat Detection", "System Integrity"):
            row = _small_row(label, "", "JarvisSecurityRow")
            win._hud_security_list.addWidget(row)
            win._hud_security_rows.append(row)

        win._hud_cache_ready = True

    def _refresh_dashboard(self):
        data = getattr(self, "_hud_data", {})
        cpu = data.get("cpu", 0)
        ram = data.get("ram", 0)
        disk = data.get("disk", 0)
        processes = data.get("processes", [])
        net_sent = data.get("net_sent", "--")
        net_recv = data.get("net_recv", "--")

        actions_count = len([p for p in (Path(__file__).resolve().parent / "actions").glob("*.py") if not p.name.startswith("_")])
        self._hud_cpu_value.setText(f"{cpu}%")
        self._hud_ram_value.setText(f"{ram}%")
        self._hud_disk_value.setText(f"{disk}%")
        self._hud_tools_value.setText(str(actions_count))
        self._hud_cpu_bar.setValue(cpu)
        self._hud_ram_bar.setValue(ram)
        self._hud_disk_bar.setValue(disk)
        self._hud_tools_bar.setValue(min(100, actions_count * 3))

        try:
            palettes = [
                ("#06b6d4", "rgba(0, 188, 212, 0.24)"),
                ("#3b82f6", "rgba(59, 130, 246, 0.24)"),
                ("#f97316", "rgba(249, 115, 22, 0.28)"),
                ("#22c55e", "rgba(34, 197, 94, 0.25)"),
            ]
            self._hud_palette_tick = (getattr(self, "_hud_palette_tick", 0) + 1) % len(palettes)
            for index, (card, bar) in enumerate(getattr(self, "_hud_metric_cards", [])):
                color, glow = palettes[(self._hud_palette_tick + index) % len(palettes)]
                card.setStyleSheet(
                    "#" + card.objectName() + " {"
                    "background: qlineargradient(x1:0, y1:0, x2:0, y2:1,"
                    "stop:0 rgba(0, 15, 20, 0.94),"
                    "stop:0.72 rgba(0, 7, 12, 0.92),"
                    f"stop:1 {glow});"
                    f"border: 1px solid {color};"
                    "border-radius: 18px;"
                    "}"
                )
                bar.setStyleSheet(
                    "QProgressBar {"
                    "background: rgba(4, 38, 48, 0.72);"
                    "border: none;"
                    "border-radius: 4px;"
                    "height: 8px;"
                    "}"
                    f"QProgressBar::chunk {{ background: {color}; border-radius: 4px; }}"
                )
        except Exception:
            pass

        _init_dashboard_cache(self)
        memory = _read_json(memory_file, {})
        labels = {
            "identity": ("PERFIL", "Nombre, ciudad y datos basicos"),
            "preferences": ("GUSTOS", "Musica, colores, apps y preferencias"),
            "projects": ("PROYECTOS", "Cosas que estas creando"),
            "relationships": ("CONTACTOS", "Personas importantes"),
            "wishes": ("PLANES", "Ideas, compras y metas futuras"),
            "notes": ("NOTAS", "Detalles sueltos que conviene recordar"),
        }
        for i, (category, (title, description)) in enumerate(labels.items()):
            values = memory.get(category, {})
            count = len(values) if isinstance(values, dict) else 0
            preview = ""
            if isinstance(values, dict) and values:
                first_key = next(iter(values))
                first_val = values[first_key]
                if isinstance(first_val, dict):
                    first_val = first_val.get("value", "")
                preview = f"\n{first_key}: {str(first_val)[:34]}"
            if i < len(self._hud_memory_rows):
                self._hud_memory_rows[i].setText(f"{title}  /  {count}\n{description}{preview}")

        for i, proc in enumerate(processes):
            if i >= len(self._hud_process_rows):
                break
            rss = getattr(proc.get("memory_info"), "rss", 0)
            mem = f"{rss / (1024 ** 2):.0f} MB" if rss else "--"
            row = self._hud_process_rows[i]
            labels_in_row = row.findChildren(QLabel) or []
            if len(labels_in_row) >= 2:
                labels_in_row[0].setText(proc.get("name", "Process"))
                labels_in_row[1].setText(mem)

        if len(self._hud_network_rows) >= 2:
            labels0 = self._hud_network_rows[0].findChildren(QLabel) or []
            labels1 = self._hud_network_rows[1].findChildren(QLabel) or []
            if len(labels0) >= 2:
                labels0[1].setText(net_recv)
            if len(labels1) >= 2:
                labels1[1].setText(net_sent)

    orig_init = _orig_mod.MainWindow.__init__

    def patched_init(self, *args, **kwargs):
        orig_init(self, *args, **kwargs)
        try:
            from PyQt6.QtGui import QIcon
            ico = Path(__file__).resolve().parent / "assets" / "jarvis_icono.ico"
            if ico.exists():
                self.setWindowIcon(QIcon(str(ico)))
        except Exception:
            pass
        try:
            _build_dashboard(self)
        except Exception as exc:
            try:
                self._route_log(f"HUD: no se pudo cargar dashboard ({exc})")
            except Exception:
                pass

    def patched_route_log(self, text):
        if text == "__hud_refresh__":
            try:
                _refresh_dashboard(self)
            except Exception:
                pass
            return
        return _orig_route_log(self, text)

    _orig_route_log = _orig_mod.MainWindow._route_log
    _orig_mod.MainWindow.__init__ = patched_init
    _orig_mod.MainWindow._route_log = patched_route_log

    def refresh_memory_panel(self):
        win = getattr(self, "_win", None)
        if win is not None:
            try:
                _refresh_dashboard(win)
            except Exception:
                pass

    _orig_mod.JarvisUI.refresh_memory_panel = refresh_memory_panel

    # Fallback: display_image → show_image (por si algún módulo compilado lo llama)
    def display_image(self, path):
        try:
            self.show_image([path])
        except Exception:
            pass

    _orig_mod.JarvisUI.display_image = display_image

    # ── Override ParticleOrb to implement Cyberpunk Arc Reactor ──
    _orig_orb_step = _orig_mod.ParticleOrb._step

    def patched_orb_step(self):
        import math, random, collections
        self._tick = getattr(self, "_tick", 0) + 1
        
        # Smoothly interpolate audio level for liquid-smooth physics
        audio_target = getattr(self, "_audio", 0.0)
        self._smoothed_audio = getattr(self, "_smoothed_audio", 0.0) * 0.8 + audio_target * 0.2
        
        # Initialize custom cyberpunk particles if they don't exist
        if not hasattr(self, "_cyber_particles"):
            self._cyber_particles = []
            for i in range(160):  # Increased from 120 to 160 for denser vortex
                p = type("obj", (object,), {})()
                p.angle = random.uniform(0, 2 * math.pi)
                p.radius = random.uniform(20, 200)
                p.speed = random.uniform(0.012, 0.035)
                # Particles closer to core swirl faster; boosted range for more violent motion
                p.radial_speed = random.uniform(0.6, 1.6)
                p.size = random.uniform(1.2, 3.8)
                # Bright electric-cyan / teal color palette
                g_val = int(random.uniform(200, 255))
                p.color = QColor(0, g_val, 255, int(random.uniform(140, 255)))  # Boosted alpha to 140-255
                p.trail = collections.deque(maxlen=18)  # Increased trail from 10 to 18 for longer streaks
                self._cyber_particles.append(p)
                
        cx = getattr(self, "_cx", self.width() / 2.0)
        cy = getattr(self, "_cy", self.height() / 2.0 - 30.0)
        for p in self._cyber_particles:
            # Swirl physics: angular rotation combined with inward radial attraction
            p.angle += p.speed * (1.0 + self._smoothed_audio * 2.8)
            p.radius -= p.radial_speed * (1.0 + self._smoothed_audio * 2.0)
            
            # Reset particle when it enters the center sink hole
            if p.radius < 8:
                p.radius = random.uniform(130, 165)
                p.angle = random.uniform(0, 2 * math.pi)
                p.trail.clear()
                
            px = cx + p.radius * math.cos(p.angle)
            py = cy + p.radius * math.sin(p.angle)
            p.trail.append((px, py))
            
        self.update()

    def patched_orb_paintEvent(self, event):
        import math, random
        from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QFont, QRadialGradient, QPainterPath
        from PyQt6.QtCore import QPointF, QRectF, Qt
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # ── 1. Holographic Grid Background ──
        # Grid is hidden (alpha=0) to reduce visual clutter; swirling particles are the visual focus
        # grid_pen = QPen(QColor(0, 240, 255, 0), 1)  # Commented: background grid removed
        # spacing = 40
        # for x in range(0, self.width(), spacing):
        #     painter.drawLine(x, 0, x, self.height())
        # for y in range(0, self.height(), spacing):
        #     painter.drawLine(0, y, self.width(), y)
            
        cx = getattr(self, "_cx", self.width() / 2.0)
        cy = getattr(self, "_cy", self.height() / 2.0 - 30.0)
        R = getattr(self, "_R", min(self.width(), self.height()) / 4.0)
        
        # Draw blueprint background rings
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for r_bg in (R * 0.5, R * 0.8, R * 1.1, R * 1.4):
            painter.setPen(QPen(QColor(0, 240, 255, 8), 1, Qt.PenStyle.DotLine))
            painter.drawEllipse(QPointF(cx, cy), r_bg, r_bg)
            
        # ── 2. Determine States & Colors ──
        state = getattr(self, "_state", "IDLE")
        smoothed_audio = getattr(self, "_smoothed_audio", 0.0)
        tick = getattr(self, "_tick", 0)
        
        if state == "LISTENING":
            core_color = QColor(0, 240, 255)  # Cyan
            status_text = "ESCUCHANDO"
        elif state == "THINKING":
            core_color = QColor(34, 211, 238)  # High-energy bright cyan
            status_text = "SISTEMA PENSANDO"
        elif state == "SPEAKING":
            core_color = QColor(99, 102, 241)  # Purple-blue
            status_text = "HABLANDO"
        else:
            core_color = QColor(0, 180, 220)  # Standard ambient blue
            status_text = "SYSTEM STATUS: ACTIVE"
            
        # ── 3. Radial Core Aura Glow ──
        grad = QRadialGradient(cx, cy, R * 1.5)
        grad.setColorAt(0.0, QColor(core_color.red(), core_color.green(), core_color.blue(), int(38 + smoothed_audio * 45)))
        grad.setColorAt(0.4, QColor(core_color.red(), core_color.green(), core_color.blue(), 12))
        grad.setColorAt(0.8, QColor(5, 13, 38, 5))
        grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), R * 1.6, R * 1.6)
        
        # ── 3b. Pulsing Energy Ring (Audio Reactive) ──
        energy_ring_radius = R * (1.65 + smoothed_audio * 0.35)  # Expands with audio
        energy_ring_pen = QPen(QColor(core_color.red(), core_color.green(), core_color.blue(), int(100 + smoothed_audio * 155)), 2.5)
        painter.setPen(energy_ring_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(cx, cy), energy_ring_radius, energy_ring_radius)
        
        # ── 4. Alternating Holographic Rotating Rings ──
        # Ring 1: Outer Rotating Dashed Ring
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(tick * 0.4)
        ring1_pen = QPen(QColor(core_color.red(), core_color.green(), core_color.blue(), 90), 1.5)
        ring1_pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(ring1_pen)
        painter.drawEllipse(QPointF(0, 0), R * 1.35, R * 1.35)
        painter.restore()
        
        # Ring 2: Middle Rotating Tick Ring (Anti-clockwise)
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(-tick * 0.6)
        ring2_pen = QPen(QColor(core_color.red(), core_color.green(), core_color.blue(), 60), 1.0)
        painter.setPen(ring2_pen)
        painter.drawEllipse(QPointF(0, 0), R * 1.15, R * 1.15)
        for angle_deg in range(0, 360, 15):
            rad = math.radians(angle_deg)
            x1 = R * 1.12 * math.cos(rad)
            y1 = R * 1.12 * math.sin(rad)
            x2 = R * 1.18 * math.cos(rad)
            y2 = R * 1.18 * math.sin(rad)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
        painter.restore()
        
        # Ring 3: Concentric Geometric Hexagons
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(tick * 0.25)
        hex_pen = QPen(QColor(core_color.red(), core_color.green(), core_color.blue(), 25), 1.0)
        painter.setPen(hex_pen)
        
        def draw_hexagon(r):
            path = QPainterPath()
            for i in range(6):
                angle = i * math.pi / 3
                hx = r * math.cos(angle)
                hy = r * math.sin(angle)
                if i == 0:
                    path.moveTo(hx, hy)
                else:
                    path.lineTo(hx, hy)
            path.closeSubpath()
            painter.drawPath(path)
            
        for hex_r in (R * 0.7, R * 0.76, R * 0.82):
            draw_hexagon(hex_r)
        painter.restore()
        
        # ── 5. Swirling Spiral Particles & Luminous Data Streams ──
        # Additive blending creates intense HUD emission glow
        orig_comp = painter.compositionMode()
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Plus)
        
        particles = getattr(self, "_cyber_particles", [])
        for p in particles:
            if len(p.trail) < 2:
                continue
                
            # Draw trail with progressive size and opacity fade
            for idx_pt, pt in enumerate(p.trail):
                pct = (idx_pt + 1) / len(p.trail)
                alpha = int(p.color.alpha() * pct * 0.55)  # Boosted from 0.42 to 0.55 for brighter trails
                pt_size = p.size * pct * (1.2 + smoothed_audio * 1.2)  # Boosted base multiplier from 1.0 to 1.2
                
                trail_col = QColor(p.color.red(), p.color.green(), p.color.blue(), alpha)
                painter.setBrush(QBrush(trail_col))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QPointF(pt[0], pt[1]), pt_size / 2.0, pt_size / 2.0)
                
            # Draw bright head core with enhanced glow
            head_x, head_y = p.trail[-1]
            head_size = p.size * (1.5 + smoothed_audio * 1.2)  # Boosted from 1.25 to 1.5 for thicker cores
            head_col = QColor(220, 252, 255, int(p.color.alpha() * 1.1))  # Boost alpha on head
            painter.setBrush(QBrush(head_col))
            painter.drawEllipse(QPointF(head_x, head_y), head_size / 2.0, head_size / 2.0)
            
        painter.setCompositionMode(orig_comp)
        
        # ── 6. Digital Neon Soundwave ──
        wave_y = self.height() - 75
        num_bars = 48
        bar_spacing = 6
        bar_width = 3
        
        axis_pen = QPen(QColor(core_color.red(), core_color.green(), core_color.blue(), 30), 1)
        painter.setPen(axis_pen)
        painter.drawLine(int(cx - 180), int(wave_y), int(cx + 180), int(wave_y))
        
        for i in range(num_bars):
            bx = cx + (i - num_bars / 2) * (bar_width + bar_spacing)
            dist_from_center = abs(i - num_bars / 2) / (num_bars / 2)
            factor = math.cos(dist_from_center * math.pi / 2.0)
            
            base = math.sin(i * 0.25 + tick * 0.15) * 4 * factor
            reaction = 0.0
            if smoothed_audio > 0.01:
                reaction = abs(math.sin(i * 0.45 + tick * 0.35)) * smoothed_audio * 50 * factor * random.uniform(0.7, 1.3)
                
            h = max(1.5, abs(base) + reaction)
            bar_alpha = int(80 + smoothed_audio * 120)
            bar_col = QColor(core_color.red(), core_color.green(), core_color.blue(), bar_alpha)
            bar_pen = QPen(bar_col, bar_width)
            painter.setPen(bar_pen)
            painter.drawLine(QPointF(bx, wave_y - h), QPointF(bx, wave_y + h))
            
            # Bright tips
            dot_col = QColor(220, 255, 255, int(120 + smoothed_audio * 135))
            painter.setPen(QPen(dot_col, bar_width))
            painter.drawPoint(QPointF(bx, wave_y - h))
            painter.drawPoint(QPointF(bx, wave_y + h))
            
        # ── 7. Technical HUD Labels & Bounded Status Box ──
        font_hud = QFont("Consolas", 8)
        painter.setFont(font_hud)
        
        hud_rows_left = [
            "SYS CORE: ACTIVE",
            "GRID ANALYTICS: OK",
            f"MEM_ADDR: 0x{hex(tick % 1000 + 4000).upper()}",
            f"LATENCY: {12 + int(random.uniform(0, 3))}ms",
            "ARC REACTOR STATUS",
        ]
        hud_rows_right = [
            "ASSISTANT CORE v5.1",
            f"FREQ: {24000 if state == 'SPEAKING' else (16000 if state == 'LISTENING' else 0)} Hz",
            "TELEMETRY: LIVE",
            f"AUDIO_IN: {smoothed_audio:.2f}",
            "CYBER DESIGN V1.0",
        ]
        
        for idx_row, row_text in enumerate(hud_rows_left):
            alpha = int(120 + 80 * math.sin(tick * 0.05 + idx_row))
            painter.setPen(QColor(core_color.red(), core_color.green(), core_color.blue(), alpha))
            painter.drawText(int(cx - 240), int(cy - 100 + idx_row * 16), row_text)
            
        for idx_row, row_text in enumerate(hud_rows_right):
            alpha = int(120 + 80 * math.sin(tick * 0.05 - idx_row))
            painter.setPen(QColor(core_color.red(), core_color.green(), core_color.blue(), alpha))
            painter.drawText(int(cx + 140), int(cy - 100 + idx_row * 16), row_text)
            
        # Bounded Status Box
        status_font = QFont("Consolas", 10, QFont.Weight.Bold)
        painter.setFont(status_font)
        status_width = 220
        status_height = 24
        status_x = int(cx - status_width / 2.0)
        status_y = int(wave_y - 45)
        
        bracket_pen = QPen(QColor(core_color.red(), core_color.green(), core_color.blue(), 100), 1)
        painter.setPen(bracket_pen)
        painter.drawLine(status_x, status_y, status_x + 10, status_y)
        painter.drawLine(status_x, status_y, status_x, status_y + status_height)
        painter.drawLine(status_x, status_y + status_height, status_x + 10, status_y + status_height)
        painter.drawLine(status_x + status_width, status_y, status_x + status_width - 10, status_y)
        painter.drawLine(status_x + status_width, status_y, status_x + status_width, status_y + status_height)
        painter.drawLine(status_x + status_width, status_y + status_height, status_x + status_width - 10, status_y + status_height)
        
        blink_visible = True
        if state == "LISTENING" and (tick % 30 < 15):
            blink_visible = False
        elif state == "THINKING" and (tick % 20 < 10):
            blink_visible = False
            
        if blink_visible:
            painter.setPen(QColor(core_color.red(), core_color.green(), core_color.blue(), 230))
            painter.drawText(QRectF(status_x, status_y, status_width, status_height), Qt.AlignmentFlag.AlignCenter, status_text)
            
        painter.end()

    # Re-route the functions
    _orig_mod.ParticleOrb._step = patched_orb_step
    _orig_mod.ParticleOrb.paintEvent = patched_orb_paintEvent

    _orig_mod.JarvisUI.display_image = display_image


_install_futuristic_dashboard()

# ── Re-export everything ──
_export_list = [name for name in dir(_orig_mod) if not name.startswith("_")]
for _name in _export_list:
    globals()[_name] = getattr(_orig_mod, _name)

__all__ = _export_list
