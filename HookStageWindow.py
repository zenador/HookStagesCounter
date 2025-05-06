import contextlib
import json
from base64 import b64decode
from ctypes import windll
from io import BytesIO
from tkinter import Tk, Frame, Label, constants, PhotoImage
from _tkinter import TclError
from PIL import ImageTk, Image, ImageOps
from win32.lib.win32con import WS_EX_TOOLWINDOW, WS_EX_APPWINDOW, GWL_EXSTYLE
from HookStageIcon import HOOK_ICO_BASE64, HOOK_IMG_BASE64

class HookStagesWindow:
    def __init__(self, num_survivors, num_stages, settings_file):
        self.num_survivors = num_survivors
        self.num_stages = num_stages
        self.settings_file = settings_file

        self.start_abs_x, self.start_abs_y, self.start_width, self.start_height = None, None, None, None

        self._root = Tk()
        self._root.title('HookStagesWindow')
        self._root.minsize(50, 300)  # 设置窗口最小值
        self._root.iconphoto(True, PhotoImage(data=b64decode(HOOK_ICO_BASE64)))
        self._root.overrideredirect(True)  # 设置隐藏窗口标题栏和任务栏图标
        self._root.attributes('-topmost', True)
        self._root.attributes('-transparentcolor', 'black')

        self._root_x = int(self._root.winfo_screenwidth() * 0.01)
        self._root_y = int(self._root.winfo_screenheight() * 0.4)
        self._root_width = int(self._root.winfo_screenwidth() * 0.02)
        self._root_height = int(self._root_width * 10)
        # print(f'{self._root_x=}, {self._root_y=}, {self._root_width=}, {self._root_height=}')
        self._root.geometry(f'{self._root_width}x{self._root_height}+{self._root_x}+{self._root_y}')
        self.load_settings()

        hook_img_width = self._root_width // 2
        hook_img_height = hook_img_width * 4 // 3
        hook_img = Image.open(BytesIO(b64decode(HOOK_IMG_BASE64))).resize((hook_img_width, hook_img_height))
        self.hook_img = ImageTk.PhotoImage(hook_img)

        coloured_hook_img = ImageOps.colorize(hook_img.convert("L"), "#000000", self.hook_colour)
        self.coloured_hook_img = ImageTk.PhotoImage(coloured_hook_img)

        frame = Frame(self._root, bg='black')
        frame.pack(side=constants.TOP, fill=constants.BOTH, expand=1)
        self.hooks = [[Label(frame, background='black') for _ in range(self.num_stages)] for _ in range(self.num_survivors)]
        self.counter = [0] * self.num_survivors
        self.layout_hook()

        self.post_label = Label(self._root, bg='#2980b9')
        self.post_label.bind('<Button-1>', self._get_point)
        self.post_label.bind("<B1-Motion>", self._motion_call)

        self.size_label = [Label(self._root, bg='#27ae60')] * 2
        for i in range(2):
            self.size_label[i].bind("<B1-Motion>", self._zoom_call)

        self._root.bind('<FocusIn>', self._alt_press_call)
        self._root.bind('<FocusOut>', self._alt_release_call)
        self._root.bind('<ButtonPress-1>', self._start_drag)

    def layout_hook(self):
        for i in range(len(self.hooks)):
            for j in range(len(self.hooks[i])):
                self.hooks[i][j].place(anchor=constants.W, relx=j / self.num_stages, rely=(0.4 + i) / self.num_survivors)

    def _get_point(self, event):
        """获取当前窗口位置并保存"""
        self._root_x, self._root_y = event.x, event.y

    def _motion_call(self, event):
        """窗口移动事件"""
        new_x = (event.x - self._root_x) + self._root.winfo_x()
        new_y = (event.y - self._root_y) + self._root.winfo_y()
        self._root.geometry(f'{self._root.winfo_width()}x{self._root.winfo_height()}+{new_x}+{new_y}')

    def _start_drag(self, event):
        self._root.update_idletasks()
        self.start_abs_x = self._root.winfo_pointerx() - self._root.winfo_rootx()
        self.start_abs_y = self._root.winfo_pointery() - self._root.winfo_rooty()
        self.start_width = self._root.winfo_width()
        self.start_height = self._root.winfo_height()

    def _zoom_call(self, event):
        self._root.update_idletasks()
        end_abs_x = self._root.winfo_pointerx() - self._root.winfo_rootx()
        end_abs_y = self._root.winfo_pointery() - self._root.winfo_rooty()
        calc_w = self.start_width + (end_abs_x - self.start_abs_x)
        calc_h = self.start_height + (end_abs_y - self.start_abs_y)

        with contextlib.suppress(TclError):
            self._root.geometry(f'{calc_w}x{calc_h}+{self._root.winfo_x()}+{self._root.winfo_y()}')

    def _alt_press_call(self, event):
        self._root.attributes('-transparentcolor', '')
        self._root.attributes('-alpha', 0.5)
        self.post_label.place(relwidth=1, height=10, relx=0, rely=0, anchor=constants.NW)
        self.size_label[0].place(width=5, height=15, relx=1, rely=1, anchor=constants.SE)
        self.size_label[1].place(width=15, height=5, relx=1, rely=1, anchor=constants.SE)

    def _alt_release_call(self, event):
        self._root.attributes('-transparentcolor', 'black')
        self._root.attributes('-alpha', 1)
        self.post_label.place_forget()
        for i in range(2):
            self.size_label[i].place_forget()

    def reset_hook(self):
        self.counter = [0] * self.num_survivors
        for hook in self.hooks:
            for l in hook:
                l.config(image='')

    def show_hook(self, n: int, coloured: bool = False):
        if self.counter[n] < self.num_stages:
            # print(f"show player_{n} hook {self.counter[n]} to {self.counter[n] + 1}")
            hook_img = self.coloured_hook_img if coloured else self.hook_img
            self.hooks[n][self.counter[n]].config(image=hook_img)
            self.counter[n] += 1

    def hide_hook(self, n: int):
        if self.counter[n] > 0:
            # print(f"hide player_{n} hook {self.counter[n]} to {self.counter[n] - 1}")
            self.counter[n] -= 1
            self.hooks[n][self.counter[n]].config(image='')

    def colour_hook(self, n: int):
        if self.counter[n] <= self.num_stages:
            self.hooks[n][self.counter[n] - 1].config(image=self.coloured_hook_img)

    def save_settings(self):
        with open(self.settings_file, 'w') as f:
            json.dump({
                'x': self._root.winfo_x(),
                'y': self._root.winfo_y(),
                'geometry': self._root.geometry(),
                'hook_colour': self.hook_colour,
            }, f)

    def load_settings(self):
        DEFAULT_HOOK_COLOUR = "#00FF00"
        try:
            with open(self.settings_file, 'r') as f:
                pos = json.load(f)
                self._root.geometry(pos['geometry'])
                self.hook_colour = pos.get('hook_colour', DEFAULT_HOOK_COLOUR)
        except:
            self.hook_colour = DEFAULT_HOOK_COLOUR

    def _set_window(self):
        """
        在任务栏上显示
        """
        hwnd = windll.user32.GetParent(self._root.winfo_id())
        style = windll.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
        style &= ~WS_EX_TOOLWINDOW
        style |= WS_EX_APPWINDOW
        res = windll.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, style)
        # re-assert the new window style
        self._root.withdraw()
        self._root.after(10, self._root.deiconify)

    def _on_closing(self):
        self.save_settings()
        self._root.destroy()

    def run(self):
        self._root.after(10, self._set_window)
        self._root.wm_protocol("WM_DELETE_WINDOW", self._on_closing)
        self._root.mainloop()


if __name__ == "__main__":
    window = HookStagesWindow()
    for i in range(self.num_survivors):
        window.show_hook(i)
        window.show_hook(i)
    window.run()
