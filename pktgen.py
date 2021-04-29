#!/usr/bin/env python3

import sys
import os
import subprocess
import signal

import curses
import npyscreen
#npyscreen.disableColor()
from parse_configuration import parse_configuration

def main():
    app = App()
    app.run()

def signal_wait_for_subprocess(sig, frame):
    pass

class PktgenInfo:
    def __init__(self, path):
        self.abs_path = os.path.join(os.path.abspath(os.getcwd()), path)
        self.cfg_path = os.path.join(self.abs_path, "cfg")
        self.tools_path = os.path.join(self.abs_path, "tools")

pinfo = PktgenInfo(path="./Pktgen-DPDK")

from npyscreen import npysThemeManagers as ThemeManagers
class CustomTheme(ThemeManagers.ThemeManager):
    default_colors = {
        'DEFAULT'     : 'WHITE_BLACK',
        'FORMDEFAULT' : 'WHITE_BLACK',
        'NO_EDIT'     : 'BLUE_BLACK',
        'STANDOUT'    : 'CYAN_BLACK',
        'CURSOR'      : 'YELLOW_BLACK',
        'CURSOR_INVERSE': 'BLACK_WHITE',
        'LABEL'       : 'GREEN_BLACK',
        'LABELBOLD'   : 'WHITE_BLACK',
        'CONTROL'     : 'YELLOW_BLACK',
        'WARNING'     : 'RED_BLACK',
        'CRITICAL'    : 'BLACK_RED',
        'GOOD'        : 'GREEN_BLACK',
        'GOODHL'      : 'GREEN_BLACK',
        'VERYGOOD'    : 'BLACK_GREEN',
        'CAUTION'     : 'YELLOW_BLACK',
        'CAUTIONHL'   : 'BLACK_YELLOW',
    }
    
class App(npyscreen.NPSApp):

    def get_configuration_list(self, path):
       configuration_list = []
       for root, dirs, files in os.walk(path):
           for filename in files:
               configuration_list.append(filename)
           return configuration_list

    def get_configuration_content_list(self, path, configuration_list):
        configuration_content_list = []
        for c in configuration_list:
           with open(os.path.join(path,c)) as file:
               configuration_content_list.append(file.read())
               file.close()
        return configuration_content_list

    def get_cmd_list(self, path, configuration_list):
        cmd_list = []
        for c in configuration_list:
            cmd_list.append(parse_configuration(os.path.join(path, c)))
        return cmd_list

    def on_ctrl_q(self, event):
        sys.exit(0)

    def main(self):
        npyscreen.setTheme(CustomTheme)
        form = npyscreen.FormBaseNew(name = "Pktgen-DPDK")
        column_height = terminal_dimensions()[0] - 9

        widget_configuration_list = form.add(
            ColumnSelect,
            name       = "Run configuration",
            relx       = 2,
            rely       = 2,
            max_width  = 27,
            max_height = column_height,
        )
        widget_configuration_content = form.add(
            ColumnText,
            name       = "",
            relx       = 30,
            rely       = 2,
            max_height = column_height, 
        )
        widget_cmd = form.add(
            ColumnText,
            name       = "Execute",
            max_height = 3
        )
        widget_cmd.resize

        configuration_list         = self.get_configuration_list(pinfo.cfg_path)
        configuration_content_list = self.get_configuration_content_list(pinfo.cfg_path, configuration_list)
        cmd_list                   = self.get_cmd_list(pinfo.cfg_path, configuration_list)

        widget_configuration_list.values = configuration_list
        widget_configuration_list.set_configuration_list(configuration_list)
        widget_configuration_list.set_content_list(configuration_content_list)
        widget_configuration_list.set_content_widget(widget_configuration_content)
        widget_configuration_list.set_cmd_widget(widget_cmd)
        widget_configuration_list.set_cmd_list(cmd_list)
        widget_configuration_list.set_form(form) 

        widget_configuration_list.entry_widget.add_handlers({
            curses.KEY_DOWN: widget_configuration_list.on_key_down,
            curses.KEY_UP: widget_configuration_list.on_key_up,
            curses.KEY_RIGHT: widget_configuration_list.on_key_right,
            curses.KEY_LEFT: widget_configuration_list.on_key_left,
            ord('\n'): widget_configuration_list.on_key_cr,
        })

        widget_configuration_content.entry_widget.color = 'CONTROL'
        widget_configuration_content.entry_widget.value = widget_configuration_list.content_list[0]
        widget_cmd.entry_widget.value                   = widget_configuration_list.cmd_list[0]

        exit_button = form.add(
            ExitButton,
            name       = "Cancel",
            relx       = int(terminal_dimensions()[1]-13),
            rely       = int(terminal_dimensions()[0]-4)
        )
        widget_configuration_list.max_height = 5
        form.add_handlers({
             "^Q": self.on_ctrl_q
        })
        form.edit()

class Column(npyscreen.BoxTitle):
    def resize(self):
        self.max_height = int(0.73 * terminal_dimensions()[0])

import time
class suspend_curses():
    """Context Manager to temporarily leave curses mode"""

    def __enter__(self):
        curses.endwin()

    def __exit__(self, exc_type, exc_val, tb):
        newscr = curses.initscr()
        newscr.addstr('Newscreen is %s\n' % newscr)
        newscr.refresh()
        curses.doupdate()

class ColumnSelect(Column):
    idx = 0

    def _update_widgets(self):
        self.content_widget.entry_widget.value = self.content_list[self.idx]
        self.content_widget.entry_widget.update()
        self.cmd_widget.entry_widget.value = self.cmd_list[self.idx]
        self.cmd_widget.entry_widget.update()

    def set_content_widget(self, content_widget):
        self.content_widget = content_widget

    def set_cmd_widget(self, cmd_widget):
        self.cmd_widget = cmd_widget

    def set_content_list(self, content_list):
        self.content_list = content_list

    def set_cmd_list(self, cmd_list):
        self.cmd_list = cmd_list

    def on_key_down(self, event):
        if self.idx >= len(self.content_list)-1:
            return
        # Call default key down handler
        self.entry_widget.h_cursor_line_down(curses.KEY_DOWN)
	# Extend default key down handler
        self.idx = self.idx + 1
        self._update_widgets()

    def on_key_up(self, event):
        if self.idx <= 0:
            return
        # Call default key up handler
        self.entry_widget.h_cursor_line_up(curses.KEY_UP)
        # Extend default key up handler
        self.idx = self.idx - 1
        self._update_widgets()

    def on_key_right(self, event):
        if self.idx >= len(self.content_list)-1:
            return
        # Call default key down handler
        self.entry_widget.h_cursor_line_down(curses.KEY_RIGHT)
        # Extend default key down handler
        self.idx = self.idx + 1
        self._update_widgets()
 
    def on_key_left(self, event):
        if self.idx <= 0:
            return
        # Call default key up handler
        self.entry_widget.h_cursor_line_up(curses.KEY_LEFT)
        # Extend default key up handler
        self.idx = self.idx - 1
        self._update_widgets()

    def on_key_cr(self, event):
        cmd = "tools/run.py" + " " + self.configuration_list[self.idx].replace(".cfg", "")
        with suspend_curses():
            signal.signal(signal.SIGINT, signal_wait_for_subprocess)
            proc = subprocess.Popen(cmd, cwd=pinfo.abs_path, shell=True, stdout=sys.stdout, stderr=sys.stderr, stdin=sys.stdin)
            stdout,stderr = proc.communicate()
            exit_code = proc.wait()
            proc.kill()

    def set_form(self, form):
        self.form = form

    def set_configuration_list(self, configuration_list):
        self.configuration_list = configuration_list

class ColumnText(Column):
    _contained_widget = npyscreen.MultiLineEdit

class ExitButton(npyscreen.ButtonPress):
    def whenPressed(self):
        sys.exit(0)

def terminal_dimensions():
    return curses.initscr().getmaxyx()

if __name__ == "__main__":
    main()
