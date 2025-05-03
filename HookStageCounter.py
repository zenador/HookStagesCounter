from HookStageWindow import HookStagesWindow, NUM_SURVIVORS
from keyboard import on_press_key

def reg_key(key, i, w):
    # For some reason the loop only works through a function, not directly
    on_press_key(key, lambda event: w.show_hook(i) if event.name == key else w.hide_hook(i))

if __name__ == '__main__':
    w = HookStagesWindow()
    for i in range(NUM_SURVIVORS):
        reg_key(str(i + 1), i, w)
    on_press_key('0', lambda event: w.reset_hook())
    # on_press_key('s', lambda event: w.save_window_position())
    # on_press_key('l', lambda event: w.load_window_position())
    w.run()
