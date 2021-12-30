#!/usr/bin/python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, GdkPixbuf
import os

class GtkClient(Gtk.Window):
    def __init__(self, music_provider):
        self.music_provider = music_provider
        Gtk.Window.__init__(self, title="Simple Notebook Example")
        self.set_border_width(3)

        self.notebook = Gtk.Notebook()
        self.add(self.notebook)
        self.notebook.set_tab_pos(Gtk.PositionType.LEFT)


        self.albums_page = Gtk.FlowBox(orientation=Gtk.Orientation.HORIZONTAL)
        self.albums_page.set_homogeneous(True)
        self.albums_page.set_row_spacing(10)
        self.albums_page.set_border_width(10)
        self.albums_page.set_valign(Gtk.Align.START)
        self.albums_page.set_selection_mode(Gtk.SelectionMode.NONE)

        try:
            for filename in os.listdir("/tmp/art"):
                if filename.endswith(".png"):
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                        filename="/tmp/art/{}".format(filename),
                        width=200,
                        height=200,
                        preserve_aspect_ratio=True)

                    image = Gtk.Image.new_from_pixbuf(pixbuf)
                    self.albums_page.insert(image, 1)
        except:
            pass

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.albums_page)
        self.notebook.append_page(scrolled, Gtk.Label(label="Albums"))

        self.artists_page = Gtk.Box()
        self.artists_page.set_border_width(10)
        self.artists_page.add(Gtk.Label(label="artists appear here!"))
        self.notebook.append_page(self.artists_page, Gtk.Label(label="Artists"))

        self.show_all()
        self.connect("destroy", Gtk.main_quit)

if __name__ == '__main__':
    c = GtkClient(None)
    Gtk.main()
