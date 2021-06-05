import pywinauto

mywindows = pywinauto.findwindows.find_windows(title_re=".*888.*")

# proof that two windows are found
print(len(mywindows))

for handle in mywindows:
    print('\nhandle {}'.format(handle))

    app = pywinauto.Application().connect(handle=handle)
    navwin = app.window(handle=handle)
    navwin.print_control_identifiers()

    for x in navwin.descendants():
        print(x.window_text())
        print(x.class_name())
