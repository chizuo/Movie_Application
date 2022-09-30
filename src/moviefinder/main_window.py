from typing import Optional

from moviefinder.about_menu import AboutMenu
from moviefinder.account_creation_menu import AccountCreationMenu
from moviefinder.browse_menu import BrowseMenu
from moviefinder.login_menu import LoginMenu
from moviefinder.settings_menu import SettingsMenu
from moviefinder.start_menu import StartMenu
from moviefinder.user import User
from PySide6 import QtWidgets


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Movie Finder")
        self.central_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.init_menus()
        self.show_start_menu()
        self.show()

    def init_menus(self) -> None:
        self.init_start_menu()
        self.init_account_creation_menu()
        self.init_login_menu()
        self.init_about_menu()
        self.settings_menu: Optional[SettingsMenu] = None
        self.browse_menu: Optional[BrowseMenu] = None

    def init_start_menu(self) -> None:
        self.start_menu = StartMenu(self)
        self.start_menu.create_account_button.clicked.connect(
            self.show_account_creation_menu
        )
        self.start_menu.login_button.clicked.connect(self.show_login_menu)
        self.start_menu.about_button.clicked.connect(self.show_about_menu)
        self.central_widget.addWidget(self.start_menu)

    def init_account_creation_menu(self) -> None:
        self.account_creation_menu = AccountCreationMenu(self)
        self.account_creation_menu.submit_button.clicked.connect(self.create_account)
        self.account_creation_menu.cancel_button.clicked.connect(self.show_start_menu)
        self.central_widget.addWidget(self.account_creation_menu)

    def init_login_menu(self) -> None:
        self.login_menu = LoginMenu(self)
        self.login_menu.submit_button.clicked.connect(self.log_in)
        self.login_menu.cancel_button.clicked.connect(self.show_start_menu)
        self.central_widget.addWidget(self.login_menu)

    def init_about_menu(self) -> None:
        self.about_menu = AboutMenu(self)
        self.about_menu.back_button.clicked.connect(self.show_start_menu)
        self.central_widget.addWidget(self.about_menu)

    def show_start_menu(self) -> None:
        self.central_widget.setCurrentWidget(self.start_menu)

    def show_account_creation_menu(self) -> None:
        self.central_widget.setCurrentWidget(self.account_creation_menu)

    def show_login_menu(self) -> None:
        self.central_widget.setCurrentWidget(self.login_menu)

    def show_about_menu(self) -> None:
        self.central_widget.setCurrentWidget(self.about_menu)

    def show_settings_menu(self) -> None:
        """Shows the settings menu.

        Assumes the browse menu has a user object.
        """
        if self.settings_menu is None:
            assert self.browse_menu is not None
            self.settings_menu = SettingsMenu(self.browse_menu.user, self)
            self.settings_menu.save_button.clicked.connect(self.save_settings)
            self.central_widget.addWidget(self.settings_menu)
        self.central_widget.setCurrentWidget(self.settings_menu)

    def show_browse_menu(self, user: User) -> None:
        if self.browse_menu is None:
            self.browse_menu = BrowseMenu(user, self)
            self.browse_menu.settings_button.clicked.connect(self.show_settings_menu)
            self.central_widget.addWidget(self.browse_menu)
        self.central_widget.setCurrentWidget(self.browse_menu)

    def create_account(self) -> None:
        menu = self.account_creation_menu
        if not menu.email_line_edit.hasAcceptableInput():
            msg = QtWidgets.QMessageBox()
            msg.setText("Invalid email address.")
            msg.exec()
            return
        if not menu.password_line_edit.hasAcceptableInput():
            msg = QtWidgets.QMessageBox()
            msg.setText("Invalid password. The password must have 9 to 50 characters.")
            msg.exec()
            return
        if menu.password_line_edit.text() != menu.confirm_password_line_edit.text():
            menu.confirm_password_line_edit.clear()
            msg = QtWidgets.QMessageBox()
            msg.setText("The passwords do not match.")
            msg.exec()
            return
        print("create account menu's submit button clicked")
        name = menu.name_line_edit.text()
        email = menu.email_line_edit.text()
        password = menu.password_line_edit.text()
        menu.password_line_edit.clear()
        menu.confirm_password_line_edit.clear()
        region = menu.region_combo_box.currentText()
        services = menu.get_services()
        print(f"{name = }")
        print(f"{email = }")
        print(f"{password = }")
        print(f"{region = }")
        print(f"{services = }")
        # TODO: save the name, email, region, password, and services to the database.
        self.show_browse_menu(User(name, email, region, services))

    def log_in(self) -> None:
        print("log in menu's submit button clicked")
        email = self.login_menu.email_line_edit.text()
        password = self.login_menu.password_line_edit.text()
        self.login_menu.password_line_edit.clear()
        print(f"{email = }")
        print(f"{password = }")
        # TODO: check if the given email address and password are in the database.
        # TODO: get the user's name, region, and services from the database.
        name = ""
        region = ""
        services: list[str] = []
        self.show_browse_menu(User(name, email, region, services))

    def save_settings(self) -> None:
        print("Submit menu's save button clicked.")
        assert self.settings_menu is not None
        name = self.settings_menu.name_line_edit.text()
        email = self.settings_menu.email_line_edit.text()
        password = self.settings_menu.password_line_edit.text()
        self.settings_menu.password_line_edit.clear()
        self.settings_menu.confirm_password_line_edit.clear()
        region = self.settings_menu.region_combo_box.currentText()
        services = self.settings_menu.get_services()
        print(f"{name = }")
        print(f"{email = }")
        print(f"{password = }")
        print(f"{region = }")
        print(f"{services = }")
        # TODO: update the database with the new info.
        self.show_browse_menu(User(name, email, region, services))
