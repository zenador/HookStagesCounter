import sys, os
from HookStageWindow import HookStagesWindow
from keyboard import on_press_key, add_hotkey

def get_filename():
    def get_full_filename():
        # return os.path.basename(sys.argv[0])
        # determine if application is a script file or frozen exe
        if getattr(sys, 'frozen', False):
            return os.path.basename(sys.executable)
        elif __file__:
            return os.path.basename(__file__)
    return os.path.splitext(get_full_filename())[0]

def reg_key(key, fkey, i, w):
    # For some reason the loop only works through a function, not directly
    def handle_key_press(event):
        if event.name == key:
            w.show_hook(i)
        elif event.name != "end":
            # There's a bug where the end key is somehow wrongly registered here, ignore it
            w.hide_hook(i)
    def handle_fkey_press(event):
        if event.name == fkey:
            w.show_hook(i, coloured=True)
    on_press_key(key, handle_key_press)
    on_press_key(fkey, handle_fkey_press, suppress=True)
    add_hotkey('ctrl+'+key, lambda: w.colour_hook(i))

if __name__ == '__main__':
    filename = get_filename()
    if '8' in filename:
        num_survivors = 8
    else:
        num_survivors = 4
    num_stages = 2
    settings_file = filename + '_settings.json'
    w = HookStagesWindow(num_survivors=num_survivors, num_stages=num_stages, settings_file=settings_file)
    for i in range(num_survivors):
        reg_key(str(i + 1), f"f{i+1}", i, w)
    on_press_key('0', lambda event: w.reset_hook())
    # on_press_key('s', lambda event: w.save_window_position())
    # on_press_key('l', lambda event: w.load_window_position())
    w.run()
