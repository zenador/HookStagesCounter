import contextlib
from base64 import b64decode
from ctypes import windll
from io import BytesIO
from tkinter import Tk, Frame, Label, constants, PhotoImage
from _tkinter import TclError
from PIL import ImageTk, Image
from win32.lib.win32con import WS_EX_TOOLWINDOW, WS_EX_APPWINDOW, GWL_EXSTYLE
from HookStageIcon import HOOK_ICO_BASE64, HOOK_IMG_BASE64

class HookStagesWindow:
    def __init__(self):
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

        hook_img_width = self._root_width // 2
        hook_img_height = hook_img_width * 4 // 3
        self.hook_img = ImageTk.PhotoImage(
            Image.open(BytesIO(b64decode(HOOK_IMG_BASE64))).resize((hook_img_width, hook_img_height)))

        frame = Frame(self._root, bg='black')
        frame.pack(side=constants.TOP, fill=constants.BOTH, expand=1)
        self.hooks = [[Label(frame, background='black') for _ in range(2)] for _ in range(4)]
        self.counter = [0, 0, 0, 0]
        self.layout_hook()

        self.post_label = Label(self._root, bg='#2980b9')
        self.post_label.bind('<Button-1>', self._get_point)
        self.post_label.bind("<B1-Motion>", self._motion_call)

        self.size_label = [Label(self._root, bg='#27ae60'), Label(self._root, bg='#27ae60')]
        self.size_label[0].bind("<B1-Motion>", self._zoom_call)
        self.size_label[1].bind("<B1-Motion>", self._zoom_call)

        self._root.bind('<FocusIn>', self._alt_press_call)
        self._root.bind('<FocusOut>', self._alt_release_call)
        self._root.bind('<ButtonPress-1>', self._start_drag)

    def layout_hook(self):
        for i in range(len(self.hooks)):
            self.hooks[i][0].place(anchor=constants.W, relx=0, rely=(0.1 + 0.25 * i))
            self.hooks[i][1].place(anchor=constants.W, relx=0.5, rely=(0.1 + 0.25 * i))

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
        self.size_label[0].place_forget()
        self.size_label[1].place_forget()

    def reset_hook(self):
        self.counter = [0, 0, 0, 0]
        for l1, l2 in self.hooks:
            l1.config(image=''), l2.config(image='')

    def show_hook(self, n: int):
        if self.counter[n] < 2:
            # print(f"show player_{n} hook {self.counter[n]} to {self.counter[n] + 1}")
            self.hooks[n][self.counter[n]].config(image=self.hook_img)
            self.counter[n] += 1

    def hide_hook(self, n: int):
        if self.counter[n] > 0:
            # print(f"hide player_{n} hook {self.counter[n]} to {self.counter[n] - 1}")
            self.counter[n] -= 1
            self.hooks[n][self.counter[n]].config(image='')

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

    def run(self):
        self._root.after(10, self._set_window)
        self._root.mainloop()


if __name__ == "__main__":
    window = HookStagesWindow()
    window.show_hook(0)
    window.show_hook(0)
    window.show_hook(1)
    window.show_hook(1)
    window.show_hook(2)
    window.show_hook(2)
    window.show_hook(3)
    window.show_hook(3)
    window.run()
