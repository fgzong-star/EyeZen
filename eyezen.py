import sys
import random
import os
import time

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QSlider, 
                             QFrame, QGridLayout, QCheckBox, QComboBox, 
                             QGraphicsDropShadowEffect, QSpinBox, QSystemTrayIcon, 
                             QMenu, QPlainTextEdit, QDialog, QTabWidget, QSizePolicy,
                             QScrollArea, QProgressBar, QSplashScreen)
# 引入 QThread 等多线程组件
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QThread, QObject, QSize, QSharedMemory, QMutex, QWaitCondition
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QAction, QIcon, QPixmap, QBrush

# --- 配置文件路径 ---
CONFIG_FILE = "eyezen_config.json"
APP_NAME = "EyeZen"
# 更新实例锁 Key
SINGLE_INSTANCE_KEY = "EyeZen-V3.4-AsynchronousSplashScreen"

# --- 默认配置 ---
DEFAULT_CONFIG = {
    "work_mins": 20,
    "rest_secs": 20,
    "brightness": 80,
    "temperature": 0,
    "startup": False, 
    "sound_enabled": True,
    "custom_preset": {"b": 50, "t": 30},
    "exclude_fullscreen": True,
    "excluded_apps": [],
    "auto_start_rest_secs": 30
}

# --- 样式配置 (保持不变) ---
STYLESHEET = """
QMainWindow, QDialog { background-color: #f0f3f8; }
QWidget { font-family: 'Segoe UI Variable Display', 'Segoe UI', sans-serif; color: #333; }
QFrame#Card { background-color: rgba(255, 255, 255, 0.9); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 1); }
QLabel#Header { font-size: 26px; font-weight: 600; color: #2c2c2c; }
QLabel#SubHeader { font-size: 14px; font-weight: 600; color: #666; margin-top: 10px; }
QPushButton#PresetBtn { background-color: #f3f3f3; border-radius: 12px; padding: 12px; border: 1px solid #e0e0e0; font-size: 13px; color: #444; }
QPushButton#PresetBtn:hover { background-color: #ffffff; border-color: #ccc; }
QPushButton#PresetBtn:checked { background-color: #e0e4e9; border-color: #2752cb; color: #2752cb; } 
QPushButton#SaveBtn { background-color: transparent; color: #2752cb; border: 1px dashed #2752cb; border-radius: 8px; padding: 8px; font-size: 12px; }
QPushButton#SaveBtn:hover { background-color: rgba(39, 82, 203, 0.1); }
QPushButton#MainControlBtn { background-color: #ffffff; color: #333; border: 1px solid #ccc; border-radius: 8px; font-size: 16px; padding: 10px 25px; font-weight: 600; }
QPushButton#MainControlBtn:hover { background-color: #f0f0f0; border-color: #bbb;}
QPushButton#MainControlBtn:pressed { background-color: #e0e0e0;}
QPushButton#MainControlBtn[active="true"] { background-color: #2752cb; color: white; border: none;}
QPushButton#MainControlBtn[active="true"]:hover { background-color: #1e40a3;}
QPushButton#OverlayBtnPrimary { background-color: #ffffff; color: #2752cb; border: 2px solid #2752cb; border-radius: 8px; padding: 10px 30px; font-size: 16px; font-weight: bold; }
QPushButton#OverlayBtnPrimary:hover { background-color: #2752cb; color: #ffffff; }
QPushButton#OverlayBtnSecondary { background-color: transparent; color: #444; border: 1px solid #666; border-radius: 8px; padding: 10px 30px; font-size: 16px; }
QPushButton#OverlayBtnSecondary:hover { background-color: rgba(0,0,0,0.05); color: #000; border-color: #333; }
QSpinBox { border: 1px solid #ccc; border-radius: 6px; padding: 4px; background-color: white; font-weight: bold; color: #2752cb; selection-background-color: #2752cb; }
QSpinBox::up-button, QSpinBox::down-button { width: 0px; }
QComboBox { border: 1px solid #ccc; border-radius: 8px; padding: 6px 10px; background: #ffffff; color: #333; font-size: 13px; }
QComboBox::drop-down { border: 0px; width: 20px; }
QComboBox QAbstractItemView { background-color: #ffffff; border: 1px solid #ccc; selection-background-color: #eef2f6; selection-color: #333; outline: none; padding: 4px; }
QSlider::groove:horizontal { border: 0px; background: #e0e0e0; height: 6px; border-radius: 3px; }
QSlider::sub-page:horizontal { background: #2752cb; border-radius: 3px; }
QSlider::handle:horizontal { background: #fff; border: 2px solid #2752cb; width: 16px; height: 16px; margin: -5px 0; border-radius: 9px; }
QCheckBox::indicator:checked { background-color: #2752cb; border-color: #2752cb; }
QPlainTextEdit { border: 1px solid #ccc; border-radius: 8px; padding: 8px; background-color: white; font-family: 'Consolas', 'Segoe UI'; font-size: 13px; color: #444; }
#NavBar { background-color: transparent; padding: 10px 20px; }
#NavTitle { font-size: 24px; font-weight: 800; color: #2752cb; }
QPushButton#SettingsBtn { background-color: transparent; border: None; padding: 6px; border-radius: 8px;}
QPushButton#SettingsBtn:hover { background-color: rgba(0,0,0,0.05); }
QTabWidget::pane { border: none; }
QTabBar::tab { background: transparent; padding: 10px 20px; font-size: 15px; color: #666; font-weight: 600; border-bottom: 3px solid transparent; }
QTabBar::tab:selected { color: #2752cb; border-bottom-color: #2752cb; }
QDialog QFrame#Card { background-color: #ffffff; border: none; }
QPushButton#BigIconBtn { background-color: #ffffff; color: #555; border-radius: 10px; font-size: 22px; border: 1px solid #ddd; }
QPushButton#BigIconBtn:hover { background-color: #f5f5f5; color: #2752cb; border-color: #2752cb;}
QScrollArea { border: none; background-color: transparent; }
QScrollBar:vertical { border: none; background: #f0f3f8; width: 10px; margin: 0px 0px 0px 0px; }
QScrollBar::handle:vertical { background: #c0c5ce; min-height: 20px; border-radius: 5px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }

/* V3.4 新增: 启动画面样式 */
#SplashFrame {
    background-color: #ffffff;
    border-radius: 20px;
    border: 1px solid #e0e0e0;
}
QProgressBar#SplashProgress {
    border: none;
    background-color: #f0f3f8;
    border-radius: 4px;
    height: 8px;
    text-align: center;
}
QProgressBar#SplashProgress::chunk {
    background-color: #2752cb;
    border-radius: 4px;
}
"""

# ... (WarmOverlay, HardwareThread, WindowsUtils, ConfigManager, StartupManager, SoundManager, SmoothController, BreakOverlay, create_eyezen_icon, create_gear_icon, create_slider_with_input, CircularProgress, SettingsDialog, DashboardPage 这些类的代码与 V3.3 保持完全一致，为了节省篇幅，这里省略，请确保最终文件中包含它们) ...
# -------------------------------------------------------------------------
# --- 为了方便复制，我将 V3.3 的完整组件代码再次放在这里 ---
# -------------------------------------------------------------------------

# --- V3.2: 稳定的色温调节覆盖层 ---
class WarmOverlay(QWidget):
    def __init__(self, screen_geometry):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowTransparentForInput | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setGeometry(screen_geometry)
        self.opacity = 0.0
        self.color = QColor(255, 130, 20) 

    def set_warmth(self, value):
        self.opacity = (value / 100.0) * 0.45 
        self.update()

    def paintEvent(self, event):
        if self.opacity > 0:
            painter = QPainter(self)
            color = QColor(self.color)
            color.setAlphaF(self.opacity)
            painter.fillRect(self.rect(), color)

# --- 硬件控制工作线程 (仅保留亮度控制) ---
class HardwareThread(QThread):
    def __init__(self, initial_bri):
        super().__init__()
        self.target_brightness = initial_bri
        self.current_brightness = -1
        self._running = True
        self._mutex = QMutex()
        self._condition = QWaitCondition()

    def update_target_brightness(self, bri):
        self._mutex.lock()
        try:
            self.target_brightness = bri
            self._condition.wakeOne()
        finally:
            self._mutex.unlock()

    def stop(self):
        self._mutex.lock()
        try:
            self._running = False
            self._condition.wakeOne()
        finally:
            self._mutex.unlock()
        self.wait()

    def run(self):
        # 延迟导入 sbc
        import screen_brightness_control as sbc
        while True:
            self._mutex.lock()
            try:
                while self._running and self.target_brightness == self.current_brightness:
                    self._condition.wait(self._mutex)
                
                if not self._running:
                    break
                
                bri = self.target_brightness
            finally:
                self._mutex.unlock()

            try:
                if bri != self.current_brightness:
                    sbc.set_brightness(bri) 
                    self.current_brightness = bri
            except Exception:
                pass
            
            self.msleep(30)


# --- Windows API 工具类 ---
class WindowsUtils:
    @staticmethod
    def _init_ctypes():
        import ctypes
        from ctypes import wintypes
        class RECT(ctypes.Structure):
            _fields_ = [('left', wintypes.LONG), ('top', wintypes.LONG), ('right', wintypes.LONG), ('bottom', wintypes.LONG)]
        class MONITORINFO(ctypes.Structure):
            _fields_ = [('cbSize', wintypes.DWORD), ('rcMonitor', RECT), ('rcWork', RECT), ('dwFlags', wintypes.DWORD)]
        return ctypes, wintypes, RECT, MONITORINFO

    @staticmethod
    def is_current_window_fullscreen():
        try:
            ctypes, wintypes, RECT, MONITORINFO = WindowsUtils._init_ctypes()
            user32 = ctypes.windll.user32
            GWL_STYLE = -16
            WS_POPUP = 0x80000000
            WS_CAPTION = 0x00C00000

            hwnd = user32.GetForegroundWindow()
            if not hwnd: return False
            win_rect = RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(win_rect))
            win_w, win_h = win_rect.right - win_rect.left, win_rect.bottom - win_rect.top
            monitor = user32.MonitorFromWindow(hwnd, 2)
            mi = MONITORINFO()
            mi.cbSize = ctypes.sizeof(MONITORINFO)
            user32.GetMonitorInfoW(monitor, ctypes.byref(mi))
            mon_w, mon_h = mi.rcMonitor.right - mi.rcMonitor.left, mi.rcMonitor.bottom - mi.rcMonitor.top
            style = user32.GetWindowLongW(hwnd, GWL_STYLE)
            is_popup = (style & WS_POPUP) != 0
            has_caption = (style & WS_CAPTION) == WS_CAPTION
            if (win_w >= mon_w and win_h >= mon_h) and (is_popup or not has_caption):
                return True
            return False
        except: return False

    @staticmethod
    def _get_foreground_process_name_internal():
        try:
            import ctypes
            from ctypes import wintypes
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            psapi = ctypes.windll.psapi

            hwnd = user32.GetForegroundWindow()
            if not hwnd: return None
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            h_process = kernel32.OpenProcess(0x0400 | 0x0010, False, pid)
            if not h_process: return None
            buf = ctypes.create_unicode_buffer(1024)
            if psapi.GetModuleFileNameExW(h_process, None, buf, 1024):
                full_path = buf.value
                kernel32.CloseHandle(h_process)
                return os.path.basename(full_path).lower()
            kernel32.CloseHandle(h_process)
            return None
        except: return None

    @staticmethod
    def is_current_process_in_list(app_list):
        if not app_list: return False
        current_app = WindowsUtils._get_foreground_process_name_internal()
        if current_app and current_app in app_list:
            return True
        return False

# --- 管理器类 ---
class ConfigManager:
    @staticmethod
    def load():
        import json
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    config = DEFAULT_CONFIG.copy()
                    config.update(data)
                    for key, val in DEFAULT_CONFIG.items():
                        if key not in config: config[key] = val
                    return config
            except: return DEFAULT_CONFIG.copy()
        return DEFAULT_CONFIG.copy()
    @staticmethod
    def save(config):
        import json
        try:
            with open(CONFIG_FILE, 'w') as f: json.dump(config, f)
        except: pass

class StartupManager:
    @staticmethod
    def set_startup(enable=True):
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
            app_path = f'"{sys.executable}"' if getattr(sys, 'frozen', False) else f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'
            if enable: winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, app_path)
            else:
                try: winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError: pass
            winreg.CloseKey(key)
        except: pass

class SoundManager:
    @staticmethod
    def play_alert():
        import winsound
        try: winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
        except: pass
    @staticmethod
    def play_finish():
        import winsound
        try: winsound.PlaySound("SystemHand", winsound.SND_ALIAS | winsound.SND_ASYNC)
        except: pass

class SmoothController(QObject):
    value_changed = pyqtSignal(int)
    def __init__(self, initial_val=0):
        super().__init__()
        self.timer = QTimer(); self.timer.setInterval(20); self.timer.timeout.connect(self._step)
        self.current_val = initial_val; self.target_val = initial_val; self.step_size = 1
    def set_target(self, target, current_start=None):
        if current_start is not None: self.current_val = current_start
        self.target_val = target
        diff = abs(self.target_val - self.current_val)
        self.step_size = max(1, diff / 20.0) 
        if diff > 0: self.timer.start()
        else: self.value_changed.emit(int(self.target_val))
    def _step(self):
        if abs(self.current_val - self.target_val) < self.step_size:
            self.current_val = self.target_val; self.timer.stop()
        else:
            if self.current_val < self.target_val: self.current_val += self.step_size
            else: self.current_val -= self.step_size
        self.value_changed.emit(int(self.current_val))

# --- 强制休息遮罩层 ---
class BreakOverlay(QWidget):
    action_triggered = pyqtSignal(str) 
    def __init__(self, screen_geo, auto_start_secs=30):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setGeometry(screen_geo); self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.bg_color = QColor(250, 248, 240, 245); self.quotes = ["休息是为了走更远的路。", "眼睛是心灵的窗户，请呵护它。", "Work hard, rest harder.", "停下来，深呼吸。", "健康是最大的财富。", "Look away, see the world."]
        self.setWindowOpacity(0.0)
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity"); self.fade_anim.setDuration(800); self.fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        layout = QVBoxLayout(self); layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame = QFrame(); frame.setStyleSheet("background: transparent;")
        c_layout = QVBoxLayout(frame); c_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.title_lbl = QLabel("Time to rest your eyes"); self.title_lbl.setStyleSheet("font-size: 36px; color: #222; font-weight: bold;")
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.quote_lbl = QLabel(""); self.quote_lbl.setStyleSheet("font-size: 22px; color: #444; margin-top: 20px; font-style: italic; font-family: 'KaiTi', 'Segoe UI';"); self.quote_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter); self.quote_lbl.setWordWrap(True)
        
        self.auto_start_secs_config = auto_start_secs
        self.current_auto_start_secs = auto_start_secs
        self.auto_start_lbl = QLabel(f"Auto-starting in {self.current_auto_start_secs}s..."); self.auto_start_lbl.setStyleSheet("font-size: 16px; color: #666; margin-top: 15px;"); self.auto_start_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.timer_lbl = QLabel("20 seconds remaining"); self.timer_lbl.setStyleSheet("font-size: 20px; color: #2752cb; margin-top: 30px; font-weight: bold;"); self.timer_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter); self.timer_lbl.hide() 
        
        self.btn_widget = QWidget(); btn_layout = QHBoxLayout(self.btn_widget); btn_layout.setSpacing(25)
        self.btn_start = QPushButton("Start Rest", objectName="OverlayBtnPrimary"); self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor); self.btn_start.clicked.connect(lambda: self.action_triggered.emit("START"))
        self.btn_skip = QPushButton("Skip", objectName="OverlayBtnSecondary"); self.btn_skip.setCursor(Qt.CursorShape.PointingHandCursor); self.btn_skip.clicked.connect(lambda: self.action_triggered.emit("SKIP"))
        btn_layout.addWidget(self.btn_start); btn_layout.addWidget(self.btn_skip)
        
        c_layout.addWidget(self.title_lbl); c_layout.addWidget(self.quote_lbl); c_layout.addWidget(self.auto_start_lbl); c_layout.addWidget(self.timer_lbl); c_layout.addSpacing(40); c_layout.addWidget(self.btn_widget); layout.addWidget(frame)
        
        self.rest_seconds = 20; 
        self.rest_timer = QTimer(); self.rest_timer.timeout.connect(self.rest_tick)
        self.auto_start_timer = QTimer(); self.auto_start_timer.setInterval(1000); self.auto_start_timer.timeout.connect(self.auto_start_tick)
    
    def paintEvent(self, event): painter = QPainter(self); painter.fillRect(self.rect(), self.bg_color)
    
    def closeEvent(self, event):
        self.rest_timer.stop(); self.auto_start_timer.stop(); self.fade_anim.stop()
        super().closeEvent(event)

    def fade_in(self):
        self.title_lbl.setText("Time to rest your eyes"); self.quote_lbl.setText(f"“{random.choice(self.quotes)}”")
        self.timer_lbl.hide(); self.btn_widget.show(); 
        self.current_auto_start_secs = self.auto_start_secs_config
        self.auto_start_lbl.setText(f"Auto-starting in {self.current_auto_start_secs}s..."); self.auto_start_lbl.show()
        self.auto_start_timer.start()
        self.showFullScreen(); self.fade_anim.setStartValue(0.0); self.fade_anim.setEndValue(1.0); self.fade_anim.start()

    def fade_out(self, callback=None):
        self.auto_start_timer.stop()
        self.fade_anim.setStartValue(1.0); self.fade_anim.setEndValue(0.0)
        if callback: self.fade_anim.finished.connect(callback)
        self.fade_anim.start()

    def auto_start_tick(self):
        self.current_auto_start_secs -= 1
        if self.current_auto_start_secs > 0:
            self.auto_start_lbl.setText(f"Auto-starting in {self.current_auto_start_secs}s...")
        else:
            self.auto_start_timer.stop()
            self.action_triggered.emit("START")

    def start_rest_countdown(self, duration):
        self.auto_start_timer.stop(); self.auto_start_lbl.hide()
        self.rest_seconds = duration; self.btn_widget.hide(); self.title_lbl.setText("Relaxing...")
        self.timer_lbl.show(); self.update_timer_display(); self.rest_timer.start(1000)

    def rest_tick(self):
        self.rest_seconds -= 1; self.update_timer_display()
        if self.rest_seconds <= 0: self.rest_timer.stop(); self.action_triggered.emit("FINISHED")
    def update_timer_display(self): self.timer_lbl.setText(f"{self.rest_seconds} seconds remaining")

# --- 图标生成器 ---
def create_eyezen_icon():
    pixmap = QPixmap(64, 64); pixmap.fill(Qt.GlobalColor.transparent); painter = QPainter(pixmap); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QBrush(QColor("white"))); painter.setPen(QPen(QColor("#2752cb"), 4)); painter.drawEllipse(4, 12, 56, 40)
    painter.setBrush(QBrush(QColor("#2752cb"))); painter.setPen(Qt.PenStyle.NoPen); painter.drawEllipse(22, 22, 20, 20)
    painter.setBrush(QBrush(QColor("white"))); painter.drawEllipse(28, 28, 8, 8); painter.end()
    return QIcon(pixmap)

def create_gear_icon():
    pixmap = QPixmap(32, 32); pixmap.fill(Qt.GlobalColor.transparent); painter = QPainter(pixmap); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor("#2752cb"), 2)); painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(6, 6, 20, 20); painter.drawEllipse(12, 12, 8, 8)
    painter.end()
    return QIcon(pixmap)

# --- UI Helper ---
def create_slider_with_input(parent_layout, text, min_v, max_v, default):
    wrapper = QWidget(); l = QVBoxLayout(wrapper); l.setContentsMargins(0,0,0,0); header = QHBoxLayout(); label = QLabel(text)
    spin = QSpinBox(); spin.setRange(min_v, max_v); spin.setValue(default); spin.setFixedWidth(60); spin.setAlignment(Qt.AlignmentFlag.AlignCenter); spin.setCursor(Qt.CursorShape.PointingHandCursor)
    header.addWidget(label); header.addStretch(); header.addWidget(spin); slider = QSlider(Qt.Orientation.Horizontal); slider.setRange(min_v, max_v); slider.setValue(default); slider.setCursor(Qt.CursorShape.PointingHandCursor)
    slider.valueChanged.connect(spin.setValue); spin.valueChanged.connect(slider.setValue)
    l.addLayout(header); l.addWidget(slider); parent_layout.addWidget(wrapper)
    return slider, spin

# --- 圆形进度条 ---
class CircularProgress(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self.setFixedSize(300, 300); self.value = 100; self.time_str = "20:00"; self.status_str = "FOCUS"
    def set_progress(self, val, time_text, status): self.value = val; self.time_str = time_text; self.status_str = status; self.update()
    def paintEvent(self, event):
        painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing); rect = self.rect(); center = rect.center(); radius = 110
        pen_bg = QPen(QColor("#e0e0e0"), 12, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap); painter.setPen(pen_bg); painter.drawEllipse(center, radius, radius)
        if self.value > 0:
            pen_prog = QPen(QColor("#2752cb"), 12, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap); painter.setPen(pen_prog)
            span_angle = int(-360 * (self.value / 100) * 16); painter.drawArc(int(center.x() - radius), int(center.y() - radius), radius*2, radius*2, 90 * 16, span_angle)
        painter.setPen(QColor("#333")); painter.setFont(QFont("Segoe UI", 48, QFont.Weight.Light)); painter.drawText(rect.adjusted(0, -10, 0, -10), Qt.AlignmentFlag.AlignCenter, self.time_str)
        painter.setPen(QColor("#2752cb")); painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold)); painter.drawText(rect.adjusted(0, -80, 0, -80), Qt.AlignmentFlag.AlignCenter, self.status_str)

# --- 模态设置对话框 ---
class SettingsDialog(QDialog):
    config_changed = pyqtSignal(int, int, bool, bool, list, int)
    startup_changed = pyqtSignal(bool)

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings - EyeZen")
        self.setFixedSize(700, 580)
        self.config = config
        
        scroll_area = QScrollArea(self); scroll_area.setWidgetResizable(True); self.setLayout(QVBoxLayout()); self.layout().addWidget(scroll_area); self.layout().setContentsMargins(0, 0, 0, 0)
        content_widget = QWidget(); scroll_area.setWidget(content_widget); layout = QVBoxLayout(content_widget); layout.setContentsMargins(0,0,0,0)
        tab_widget = QTabWidget(); layout.addWidget(tab_widget)
        
        gen_tab = QWidget(); gen_layout = QVBoxLayout(gen_tab); gen_layout.setContentsMargins(30, 30, 30, 30)
        
        timer_card = QFrame(objectName="Card"); tc_layout = QVBoxLayout(timer_card); tc_layout.setContentsMargins(25, 25, 25, 25)
        tc_layout.addWidget(QLabel("Timer Intervals", objectName="SubHeader")); tc_layout.addSpacing(15)
        self.work_slider, self.work_spin = create_slider_with_input(tc_layout, "Work Duration (mins)", 1, 120, self.config["work_mins"]); tc_layout.addSpacing(15)
        self.rest_slider, self.rest_spin = create_slider_with_input(tc_layout, "Rest Duration (secs)", 10, 300, self.config["rest_secs"]); tc_layout.addSpacing(25)
        self.auto_start_slider, self.auto_start_spin = create_slider_with_input(tc_layout, "Auto-start Rest after (secs)", 5, 60, self.config.get("auto_start_rest_secs", 30)); tc_layout.addSpacing(25)
        
        tc_layout.addWidget(QLabel("System & Notifications", objectName="SubHeader")); self.startup_check = QCheckBox("Start with Windows"); self.startup_check.setChecked(self.config["startup"]); tc_layout.addWidget(self.startup_check)
        self.sound_check = QCheckBox("Enable Sound Notification"); self.sound_check.setChecked(self.config["sound_enabled"]); tc_layout.addWidget(self.sound_check)
        
        ex_card = QFrame(objectName="Card"); ec_layout = QVBoxLayout(ex_card); ec_layout.setContentsMargins(25, 25, 25, 25)
        ec_layout.addWidget(QLabel("Exclusions Rules", objectName="SubHeader"))
        self.fullscreen_check = QCheckBox("Pause during full-screen activities (Games/Videos)"); self.fullscreen_check.setChecked(self.config.get("exclude_fullscreen", True)); ec_layout.addWidget(self.fullscreen_check); ec_layout.addSpacing(15)
        ec_layout.addWidget(QLabel("Excluded Processes (one per line, e.g., vlc.exe)", objectName="SubHeader")); self.apps_edit = QPlainTextEdit(); self.apps_edit.setPlaceholderText("vlc.exe\ngame.exe"); self.apps_edit.setPlainText("\n".join(self.config.get("excluded_apps", []))); ec_layout.addWidget(self.apps_edit)
        
        gen_layout.addWidget(timer_card); gen_layout.addSpacing(20); gen_layout.addWidget(ex_card)
        
        btn_box = QHBoxLayout(); btn_box.addStretch()
        save_btn = QPushButton("Save & Apply", objectName="MainControlBtn"); save_btn.setProperty("active", True); save_btn.setCursor(Qt.CursorShape.PointingHandCursor); save_btn.clicked.connect(self.on_save)
        cancel_btn = QPushButton("Cancel", objectName="MainControlBtn"); cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor); cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(cancel_btn); btn_box.addSpacing(10); btn_box.addWidget(save_btn); gen_layout.addSpacing(20); gen_layout.addLayout(btn_box)

        about_tab = QWidget(); ab_layout = QVBoxLayout(about_tab); ab_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_lbl = QLabel(); logo_lbl.setPixmap(create_eyezen_icon().pixmap(96, 96)); ab_layout.addWidget(logo_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        title_lbl = QLabel("EyeZen v3.4 (Async Splash)"); title_lbl.setStyleSheet("font-size: 28px; font-weight: bold; color: #2752cb; margin-top: 15px;"); ab_layout.addWidget(title_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        desc_lbl = QLabel("A minimalist eye-care assistant.\nFeatures asynchronous startup for instant responsiveness.\n\nDeveloped with Python & PyQt6."); desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter); desc_lbl.setStyleSheet("font-size: 16px; color: #666; margin-top: 10px;"); ab_layout.addWidget(desc_lbl)

        tab_widget.addTab(gen_tab, "General Settings"); tab_widget.addTab(about_tab, "About")

    def on_save(self):
        work = self.work_spin.value(); rest = self.rest_spin.value(); auto_start = self.auto_start_spin.value()
        sound = self.sound_check.isChecked(); startup = self.startup_check.isChecked()
        ex_fs = self.fullscreen_check.isChecked(); ex_apps = [line.strip().lower() for line in self.apps_edit.toPlainText().split('\n') if line.strip()]
        self.config_changed.emit(work, rest, sound, ex_fs, ex_apps, auto_start)
        self.startup_changed.emit(startup)
        self.accept()

# --- 仪表盘 ---
class DashboardPage(QWidget):
    time_up_signal = pyqtSignal()
    brightness_target_signal = pyqtSignal(int)
    temperature_changed_signal = pyqtSignal(int)

    def __init__(self, window_ref):
        super().__init__(); self.window = window_ref; self.config = ConfigManager.load()
        self.custom_preset_val = self.config.get("custom_preset", DEFAULT_CONFIG["custom_preset"])
        self.total_time = self.config["work_mins"] * 60; self.current_time = self.total_time; self.timer_state = "STOPPED"; self.timer = QTimer(); self.timer.timeout.connect(self.tick)
        
        layout = QHBoxLayout(self); layout.setContentsMargins(30, 20, 30, 30); layout.setSpacing(30)
        
        timer_card = QFrame(objectName="Card"); shadow1 = QGraphicsDropShadowEffect(); shadow1.setBlurRadius(30); shadow1.setColor(QColor(0,0,0,15)); shadow1.setOffset(0,8); timer_card.setGraphicsEffect(shadow1)
        t_layout = QVBoxLayout(timer_card); t_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress = CircularProgress(); t_layout.addWidget(self.progress, alignment=Qt.AlignmentFlag.AlignCenter)
        btn_layout = QHBoxLayout(); self.play_btn = QPushButton("Start", objectName="MainControlBtn"); self.play_btn.setProperty("active", True); self.play_btn.setCursor(Qt.CursorShape.PointingHandCursor); self.play_btn.clicked.connect(self.toggle_timer)
        self.reset_btn = QPushButton("Reset", objectName="MainControlBtn"); self.reset_btn.setCursor(Qt.CursorShape.PointingHandCursor); self.reset_btn.clicked.connect(self.reset_timer)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter); btn_layout.setSpacing(25); btn_layout.addWidget(self.play_btn); btn_layout.addWidget(self.reset_btn); t_layout.addSpacing(40); t_layout.addLayout(btn_layout); t_layout.addSpacing(20)
        
        control_card = QFrame(objectName="Card"); shadow2 = QGraphicsDropShadowEffect(); shadow2.setBlurRadius(30); shadow2.setColor(QColor(0,0,0,15)); shadow2.setOffset(0,8); control_card.setGraphicsEffect(shadow2)
        c_layout = QVBoxLayout(control_card); c_layout.setContentsMargins(35, 45, 35, 45)
        c_layout.addWidget(QLabel("Display Controls", objectName="SubHeader")); c_layout.addSpacing(20)
        
        self.bri_slider, self.bri_spin = create_slider_with_input(c_layout, "Brightness (All Monitors)", 0, 100, self.config['brightness']); self.bri_slider.valueChanged.connect(self.on_bri_ui_change); self.bri_spin.valueChanged.connect(self.on_bri_ui_change); c_layout.addSpacing(25)
        self.temp_slider, self.temp_spin = create_slider_with_input(c_layout, "Temperature (Overlay)", 0, 100, self.config['temperature']); self.temp_slider.valueChanged.connect(self.on_temp_ui_change); self.temp_spin.valueChanged.connect(self.on_temp_ui_change); c_layout.addSpacing(35)
        
        ph = QHBoxLayout(); ph.addWidget(QLabel("Presets", objectName="SubHeader")); ph.addStretch(); self.save_custom_btn = QPushButton("Save Current", objectName="SaveBtn"); self.save_custom_btn.setCursor(Qt.CursorShape.PointingHandCursor); self.save_custom_btn.clicked.connect(self.save_custom_preset); ph.addWidget(self.save_custom_btn); c_layout.addLayout(ph); c_layout.addSpacing(15)
        
        grid = QGridLayout(); grid.setSpacing(12); self.presets = [("Normal",100,0), ("Smart",80,10), ("Office",90,5), ("Game",100,0), ("Movie",60,20), ("Reading",50,40), ("Night",30,60), ("Custom", -1, -1)] 
        for idx, (n, b, t) in enumerate(self.presets):
            btn = QPushButton(n, objectName="PresetBtn"); btn.setCursor(Qt.CursorShape.PointingHandCursor); btn.setCheckable(True); btn.setAutoExclusive(True); btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            if n == "Custom": btn.clicked.connect(lambda _,: self.apply_custom_preset())
            else: btn.clicked.connect(lambda _,b=b,t=t: self.apply_preset(b,t))
            grid.addWidget(btn, idx//4, idx%4)
        c_layout.addLayout(grid); c_layout.addStretch()
        
        layout.addWidget(timer_card, 45); layout.addWidget(control_card, 55)
        self.update_ui(); self.toggle_timer()

    def on_bri_ui_change(self, v):
        if self.bri_slider.value() != v: self.bri_slider.blockSignals(True); self.bri_slider.setValue(v); self.bri_slider.blockSignals(False)
        if self.bri_spin.value() != v: self.bri_spin.blockSignals(True); self.bri_spin.setValue(v); self.bri_spin.blockSignals(False)
        self.window.smooth_bri.set_target(v, None)
    def on_temp_ui_change(self, v):
        if self.temp_slider.value() != v: self.temp_slider.blockSignals(True); self.temp_slider.setValue(v); self.temp_slider.blockSignals(False)
        if self.temp_spin.value() != v: self.temp_spin.blockSignals(True); self.temp_spin.setValue(v); self.temp_spin.blockSignals(False)
        self.window.smooth_temp.set_target(v, None)
    def apply_preset(self, b, t): self.window.smooth_bri.set_target(b, self.bri_slider.value()); self.window.smooth_temp.set_target(t, self.temp_slider.value()); self.bri_slider.setValue(b); self.temp_slider.setValue(t)
    def apply_custom_preset(self): b, t = self.custom_preset_val.get('b', 50), self.custom_preset_val.get('t', 30); self.apply_preset(b, t)
    
    def save_custom_preset(self):
        self.custom_preset_val = {"b": self.bri_slider.value(), "t": self.temp_slider.value()}
        self.window.config["custom_preset"] = self.custom_preset_val
        original = self.save_custom_btn.text(); self.save_custom_btn.setText("Saved!"); QTimer.singleShot(1000, lambda: self.save_custom_btn.setText(original))
    
    def get_current_dashboard_state(self):
        return {"brightness": self.bri_slider.value(), "temperature": self.temp_slider.value(), "custom_preset": self.custom_preset_val}

    def toggle_timer(self):
        if self.timer_state == "RUNNING": self.timer.stop(); self.timer_state = "PAUSED"; self.play_btn.setText("Start")
        else: self.timer.start(1000); self.timer_state = "RUNNING"; self.play_btn.setText("Pause")
        self.update_ui()
    def reset_timer(self): self.timer.stop(); self.timer_state = "STOPPED"; self.current_time = self.total_time; self.play_btn.setText("Start"); self.update_ui()
    def tick(self):
        if self.current_time > 0: self.current_time -= 1; self.update_ui()
        else: self.timer.stop(); self.timer_state = "STOPPED"; self.play_btn.setText("Start"); self.time_up_signal.emit() 
    def set_work_duration(self, mins): self.total_time = mins * 60; self.reset_timer(); self.toggle_timer()
    def update_ui(self): m, s = divmod(self.current_time, 60); pct = (self.current_time / self.total_time * 100) if self.total_time else 0; status = "PAUSED" if self.timer_state == "PAUSED" else ("FOCUS" if self.timer_state == "RUNNING" else "READY"); self.progress.set_progress(pct, f"{m:02d}:{s:02d}", status)

# ==========================================
# --- V3.4 新增: 启动画面窗口 ---
# ==========================================
class SplashWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(320, 240)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        frame = QFrame(objectName="SplashFrame")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0,0,0,50))
        shadow.setOffset(0, 5)
        frame.setGraphicsEffect(shadow)
        
        flayout = QVBoxLayout(frame)
        flayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        flayout.setSpacing(20)
        
        icon_lbl = QLabel()
        icon_lbl.setPixmap(create_eyezen_icon().pixmap(80, 80))
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_lbl = QLabel("EyeZen")
        title_lbl.setStyleSheet("font-size: 28px; font-weight: 800; color: #2752cb;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        loading_lbl = QLabel("Loading components...")
        loading_lbl.setStyleSheet("font-size: 13px; color: #666;")
        loading_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 设置为繁忙模式的进度条
        self.progress = QProgressBar(objectName="SplashProgress")
        self.progress.setFixedWidth(200)
        self.progress.setRange(0, 0) # Indeterminate mode
        
        flayout.addWidget(icon_lbl)
        flayout.addWidget(title_lbl)
        flayout.addWidget(loading_lbl)
        flayout.addWidget(self.progress, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(frame)
        self.center_on_screen()

    def center_on_screen(self):
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

# ==========================================
# --- V3.4 新增: 后台启动任务线程 ---
# ==========================================
class StartupWorker(QThread):
    initialization_done = pyqtSignal(int) # 发回当前亮度值

    def run(self):
        try:
            # 在后台线程中执行耗时的导入和硬件查询
            import screen_brightness_control as sbc
            # 稍微等待一下，让启动画面展示一会，避免闪烁
            self.msleep(500) 
            current_bri = sbc.get_brightness()[0]
        except:
            current_bri = 50 # 默认值
        
        # 发送结果信号
        self.initialization_done.emit(current_bri)

# --- 主窗口 ---
class EyeZenWindow(QMainWindow):
    # V3.4 修改构造函数，接收初始亮度值
    def __init__(self, initial_real_bri):
        super().__init__()
        self.shared_memory = QSharedMemory(SINGLE_INSTANCE_KEY)
        if not self.shared_memory.create(1): sys.exit(0)
        self.setWindowTitle("EyeZen"); self.resize(980, 680); self.setWindowIcon(create_eyezen_icon())
        self.config = ConfigManager.load()
        self.rest_duration = self.config.get("rest_secs", 20); self.sound_enabled = self.config.get("sound_enabled", True)
        self.exclude_fullscreen = self.config.get("exclude_fullscreen", True); self.excluded_apps = self.config.get("excluded_apps", [])
        self.auto_start_rest_secs = self.config.get("auto_start_rest_secs", 30)
        
        # V3.4: 使用从启动画面传来的真实初始值
        initial_temp = self.config.get('temperature', 0)
        
        # 初始化硬件线程
        self.hardware_thread = HardwareThread(initial_real_bri)
        self.hardware_thread.start()

        # 初始化平滑控制器，使用真实初始值
        self.smooth_bri = SmoothController(initial_val=initial_real_bri)
        self.smooth_bri.value_changed.connect(self.on_smooth_bri_changed)
        
        self.smooth_temp = SmoothController(initial_val=initial_temp)
        self.smooth_temp.value_changed.connect(self.update_warm_overlays)
        
        self.init_tray(); 
        self.break_overlays = []; self.warm_overlays = []; self.reinit_overlays()
        
        main_widget = QWidget(); self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget); main_layout.setContentsMargins(0,0,0,0); main_layout.setSpacing(0)
        
        nav_bar = QWidget(objectName="NavBar"); nav_layout = QHBoxLayout(nav_bar); nav_layout.setContentsMargins(25, 15, 25, 15)
        title_lbl = QLabel("EyeZen", objectName="NavTitle"); nav_layout.addWidget(title_lbl)
        nav_layout.addStretch()
        settings_btn = QPushButton(objectName="SettingsBtn"); settings_btn.setIcon(create_gear_icon()); settings_btn.setIconSize(QSize(24, 24)); settings_btn.setCursor(Qt.CursorShape.PointingHandCursor); settings_btn.setToolTip("Settings & About")
        settings_btn.clicked.connect(self.open_settings_dialog)
        nav_layout.addWidget(settings_btn)
        main_layout.addWidget(nav_bar)
        
        self.dashboard = DashboardPage(self)
        main_layout.addWidget(self.dashboard)
        
        self.dashboard.time_up_signal.connect(self.trigger_break_prompt)
        self.dashboard.brightness_target_signal.connect(self.update_hardware_bri_target)

        # V3.4: 移除原有的 delayed_init_hardware 调用
        # QTimer.singleShot(0, self.delayed_init_hardware)

    # V3.4: 移除该方法
    # def delayed_init_hardware(self): ...

    def on_smooth_bri_changed(self, val):
        self.dashboard.brightness_target_signal.emit(self.smooth_bri.current_val)
    
    def update_warm_overlays(self, val):
        for wo in self.warm_overlays:
            wo.set_warmth(val)

    def update_hardware_bri_target(self, bri):
        if self.hardware_thread.isRunning():
            self.hardware_thread.update_target_brightness(int(bri))

    def open_settings_dialog(self):
        dialog = SettingsDialog(self.config, self)
        dialog.config_changed.connect(self.on_config_changed)
        dialog.startup_changed.connect(StartupManager.set_startup)
        dialog.exec()

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self); self.tray_icon.setIcon(create_eyezen_icon()); menu = QMenu(); show_action = QAction("Show EyeZen", self); show_action.triggered.connect(self.show_window); quit_action = QAction("Quit", self); quit_action.triggered.connect(self.quit_app); menu.addAction(show_action); menu.addSeparator(); menu.addAction(quit_action); self.tray_icon.setContextMenu(menu); self.tray_icon.activated.connect(self.on_tray_activated); self.tray_icon.show()
    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick: self.show_window()
    def show_window(self): self.showNormal(); self.activateWindow()
    def quit_app(self): self.tray_icon.hide(); QApplication.quit()
    
    def reinit_overlays(self):
        for o in self.break_overlays + self.warm_overlays: o.close()
        self.break_overlays.clear()
        self.warm_overlays.clear()
        screens = QApplication.instance().screens()
        for screen in screens:
            bo = BreakOverlay(screen.geometry(), self.auto_start_rest_secs); bo.action_triggered.connect(self.handle_break_action); self.break_overlays.append(bo)
            wo = WarmOverlay(screen.geometry()); wo.set_warmth(self.smooth_temp.current_val); wo.show(); self.warm_overlays.append(wo)
            
    def on_config_changed(self, w_min, r_sec, sound, ex_fs, ex_apps, auto_start):
        self.dashboard.set_work_duration(w_min); self.rest_duration = r_sec; self.sound_enabled = sound; self.exclude_fullscreen = ex_fs; self.excluded_apps = ex_apps
        self.auto_start_rest_secs = auto_start
        self.config.update({"work_mins": w_min, "rest_secs": r_sec, "sound_enabled": sound, "exclude_fullscreen": ex_fs, "excluded_apps": ex_apps, "auto_start_rest_secs": auto_start})

    def trigger_break_prompt(self):
        if self.exclude_fullscreen and WindowsUtils.is_current_window_fullscreen():
            print("Fullscreen app detected (Stable check). Skipping break.")
            self.dashboard.reset_timer(); self.dashboard.toggle_timer(); return
        if WindowsUtils.is_current_process_in_list(self.excluded_apps):
             print(f"Excluded app detected. Skipping break.")
             self.dashboard.reset_timer(); self.dashboard.toggle_timer(); return
        if self.sound_enabled: SoundManager.play_alert()
        self.reinit_overlays()
        for bo in self.break_overlays: bo.fade_in()
        for wo in self.warm_overlays: wo.raise_()
        for bo in self.break_overlays: bo.raise_()
        
    def handle_break_action(self, action):
        if action == "START":
            for bo in self.break_overlays: bo.start_rest_countdown(self.rest_duration)
        elif action == "SKIP" or action == "FINISHED":
            if action == "FINISHED" and self.sound_enabled: SoundManager.play_finish()
            for bo in self.break_overlays: bo.fade_out(lambda: bo.hide()); self.dashboard.reset_timer(); self.dashboard.toggle_timer() 
    
    def closeEvent(self, e):
        if self.tray_icon.isVisible():
            self.hide(); self.tray_icon.showMessage("EyeZen", "App is running in background.", QSystemTrayIcon.MessageIcon.Information, 2000)
            dash_state = self.dashboard.get_current_dashboard_state()
            self.config.update({
                "brightness": dash_state['brightness'],
                "temperature": dash_state['temperature'],
                "custom_preset": dash_state['custom_preset']
            })
            ConfigManager.save(self.config); e.ignore()
        else:
            if hasattr(self, 'smooth_bri') and self.smooth_bri.timer.isActive(): self.smooth_bri.timer.stop()
            if hasattr(self, 'smooth_temp') and self.smooth_temp.timer.isActive(): self.smooth_temp.timer.stop()
            
            for o in self.break_overlays + self.warm_overlays: o.close()

            if self.hardware_thread.isRunning():
                self.hardware_thread.stop()
            
            e.accept()

# ==========================================
# --- V3.4: 主程序入口重构 (包含启动画面逻辑) ---
# ==========================================
if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)

    # 1. 创建并显示启动画面
    splash = SplashWidget()
    splash.show()

    # 2. 创建后台启动线程
    worker = StartupWorker()

    # 定义启动完成后的回调函数
    def on_startup_finished(initial_bri):
        # 关闭启动画面
        splash.close()
        # 创建主窗口，传入初始化好的亮度值
        global window # 使用 global 以便 app.exec() 可以访问
        window = EyeZenWindow(initial_bri)
        window.show()

    # 3. 连接信号并启动线程
    worker.initialization_done.connect(on_startup_finished)
    # 当线程结束时，自动清理线程对象
    worker.finished.connect(worker.deleteLater) 
    worker.start()

    # 进入事件循环
    sys.exit(app.exec())