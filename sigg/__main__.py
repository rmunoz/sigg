import logging
import logging.config

from gi.repository import Gtk
from constants import RESOURCES_DIR
from ui import CompaniesManagerWindow


def main():
    logging.config.fileConfig(RESOURCES_DIR + "/logging.ini")
    logging.info("SIGG Started")

    CompaniesManagerWindow()

    Gtk.main()


if __name__ == '__main__':
    main()
