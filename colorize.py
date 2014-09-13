#!/usr/bin/python

# Plugin by Lukasz Chrzaszcz <l.chrzaszcz@gmail.com>

""" colorize.py - Terminator Plugin to change color of titlebar of individual
terminals """

import os
import sys
import gtk
import terminatorlib.plugin as plugin
from terminatorlib.translation import _

AVAILABLE = ['Colorize']

class ColorizeConfig:
    new_config = {}
    previous_config = {}

    def __init__(self, previous_config, new_config):
        self.new_config = new_config
        self.previous_config = previous_config

    def __getitem__(self, item):
        return self.get(item)

    def get(self, item):

        if item in self.new_config:
            print 'item on list, returning:', self.new_config[item]
            return self.new_config[item]
        else:
            return self.previous_config[item]


class Colorize(plugin.MenuItem):
    """ Add custom command to the terminal menu"""
    capabilities = ['terminal_menu']

    def __init__(self):
        plugin.MenuItem.__init__(self)


    def callback(self, menuitems, menu, terminal):
        """ Add save menu item to log 'content'the menu"""
        vte_terminal = terminal.get_vte()

        item = gtk.MenuItem(_('Change color'))
        item.connect("activate", self.change_color, terminal)
        item.set_has_tooltip(True)
        item.set_tooltip_text("Change titlebar color of this terminal")
        menuitems.append(item)

    def change_color(self, _widget, Terminal):
        """ Handle menu item callback by saving text to a file"""
        color_dialog = gtk.ColorSelectionDialog("Pick new terminal's titlebar color")
        color_sel = color_dialog.colorsel

        # set previous colors
        previous_color = gtk.gdk.color_parse(Terminal.config['title_transmit_bg_color'])

        color_sel.set_previous_color(previous_color)
        color_sel.set_current_color(previous_color)
        color_sel.set_has_palette(True)


        response = color_dialog.run()
        if response == gtk.RESPONSE_OK:
            print type(Terminal.titlebar.config)
            print dir(Terminal.titlebar.config)

            new_color_config = {
                'title_transmit_bg_color': color_sel.get_current_color().to_string()
            }
            print color_sel.get_current_color().to_string()
            new_config = ColorizeConfig(Terminal.titlebar.config, new_color_config)
            Terminal.titlebar.config = new_config
            # Terminal.titlebar.config['title_transmit_bg_color'] = color_sel.get_current_color().to_string()
        # response = savedialog.run()
        # if response == gtk.RESPONSE_OK:
        #     try:
        #         # logfile = os.path.join(savedialog.get_current_folder(),
        #         #                        savedialog.get_filename())
        #         fd = open(logfile, 'w+')
        #         # Save log file path,
        #         # associated file descriptor, signal handler id
        #         # and last saved col,row positions respectively.
        #         vte_terminal = Terminal.get_vte()
        #         (col, row) = vte_terminal.get_cursor_position()
        #
        #         self.loggers[vte_terminal] = {"filepath":logfile,
        #                                       "handler_id":0, "fd":fd,
        #                                       "col":col, "row":row}
        #         # Add contents-changed callback
        #         self.loggers[vte_terminal]["handler_id"] = vte_terminal.connect('contents-changed', self.save)
        #     except:
        #         e = sys.exc_info()[1]
        #         error = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR,
        #                                   gtk.BUTTONS_OK, e.strerror)
        #         error.run()
        #         error.destroy()

        color_dialog.destroy()

    def stop_logger(self, _widget, terminal):
        vte_terminal = terminal.get_vte()
        last_saved_col = self.loggers[vte_terminal]["col"]
        last_saved_row = self.loggers[vte_terminal]["row"]
        (col, row) = vte_terminal.get_cursor_position()
        if last_saved_col != col or last_saved_row != row:
            # Save unwritten bufer to the file
            self.write_content(vte_terminal, last_saved_row, last_saved_col, row, col)
        fd = self.loggers[vte_terminal]["fd"]
        fd.close()
        vte_terminal.disconnect(self.loggers[vte_terminal]["handler_id"])
        del(self.loggers[vte_terminal])
