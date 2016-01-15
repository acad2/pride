
def sliding_window(windows_size, step_size, lastwindow_start):
    for i in xrange(0, lastwindow_start, step_size):
        yield (i, i + windows_size)