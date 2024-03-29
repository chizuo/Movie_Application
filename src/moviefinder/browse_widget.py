from moviefinder.dev_settings import POSTER_WIDTH
from moviefinder.movie_menu import MovieMenu
from moviefinder.movie_widget import MovieWidget
from moviefinder.movies import movies
from moviefinder.worker import Worker
from PySide6 import QtCore
from PySide6 import QtWidgets


class BrowseWidget(QtWidgets.QWidget):
    """A widget that displays a list of movies and shows.

    This widget is deleted and recreated every time the user changes the genres,
    services, and/or region.
    """

    def __init__(self, main_window: QtWidgets.QMainWindow):
        QtWidgets.QWidget.__init__(self)
        self.main_window = main_window
        self.main_window.window_resized.connect(
            self.__unset_parents_and_reset_movies_layout
        )
        self.__START_ROW_COUNT = 2
        self.__MAX_SHOWN_MOVIES = 100
        self.movie_menu: MovieMenu | None = None
        self.movie_widgets: dict[str, MovieWidget] = {}  # movie_id: MovieWidget
        self.__movies_loader = Worker()
        self.__movies_loader.done.connect(self.__add_row)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.__movies_layout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.__movies_layout)
        self.__row_layouts: list[QtWidgets.QHBoxLayout] = []
        self.layout.addSpacerItem(QtWidgets.QSpacerItem(1, 100))
        self.__loading_label = QtWidgets.QLabel("<h2>Loading...</h2>")
        self.layout.addWidget(self.__loading_label, alignment=QtCore.Qt.AlignCenter)
        self.reset_movies_layout()

    def __unset_parents_and_reset_movies_layout(self) -> None:
        for movie_widget in self.movie_widgets.values():
            movie_widget.setParent(None)
        self.reset_movies_layout()

    def reset_movies_layout(self) -> None:
        self.__total_shown_movie_count = 0
        self.__movies_per_row = self.main_window.width() // (POSTER_WIDTH + 10) - 1
        for row_layout in self.__row_layouts:
            row_layout.setParent(None)
        self.__row_layouts = []
        self.__row_movie_count = 0
        if movies:
            self.__load_starting_movie_rows()
        else:
            self.layout.addWidget(
                QtWidgets.QLabel(
                    "No movies match your chosen genres, services, and region."
                ),
                alignment=QtCore.Qt.AlignCenter,
            )

    def __load_starting_movie_rows(self) -> None:
        for _ in range(self.__START_ROW_COUNT):
            self.add_row()
        # Prevent movie widgets from each being a different window.
        for movie_widget in self.movie_widgets.values():
            if movie_widget.parent() is None:
                movie_widget.setParent(self)

    def update_movies_buttons(self) -> None:
        for movie_widget in self.movie_widgets.values():
            movie_widget.update_movie_buttons()

    def show_movie_menu(self, movie_id: str) -> None:
        if self.movie_menu is None:
            self.movie_menu = MovieMenu(self.main_window)
            self.main_window.central_widget.addWidget(self.movie_menu)
        if not self.movie_menu.update_movie_data(
            movie_id, movies[movie_id].poster_pixmap
        ):
            print(f'Error: movie "{movie_id}" is invalid.')
        else:
            self.main_window.central_widget.setCurrentWidget(self.movie_menu)

    def add_row(self) -> None:
        """Loads more movies if needed and adds a row of movies to the browse widget."""
        if self.__total_shown_movie_count >= self.__MAX_SHOWN_MOVIES:
            print("Maximum number of movies shown.")
            self.__loading_label.hide()
            return
        if self.__total_shown_movie_count < len(movies):
            self.__add_row()
        if self.__total_shown_movie_count >= len(movies) - 3 * self.__movies_per_row:
            if not self.__movies_loader.is_running:
                self.__movies_loader.start(movies.load)

    def __add_row(self, ok: bool | None = True) -> None:
        """Adds a row of movies to the browse widget.

        Parameters
        ----------
        ok : bool | None, optional
            Whether the movies were loaded successfully. If False or None, the row is
            not added. The default is True.
        """
        if not ok:
            if ok is None:
                self.__loading_label.hide()
            return
        is_new_row = False
        if (
            self.__row_movie_count == 0
            or self.__row_movie_count >= self.__movies_per_row
        ):
            is_new_row = True
            self.__row_movie_count = 0
            self.__row_layouts.append(QtWidgets.QHBoxLayout())
        for movie_id in movies.range(self.__total_shown_movie_count):
            if self.__row_movie_count >= self.__movies_per_row:
                break
            movie_widget: MovieWidget | None = None
            if movie_id in self.movie_widgets:
                movie_widget = self.movie_widgets[movie_id]
            else:
                movie_widget = self.__create_movie_widget(movie_id)
            if movie_widget is not None:
                self.__row_layouts[-1].addWidget(movie_widget)
                self.__row_movie_count += 1
                self.__total_shown_movie_count += 1
        if is_new_row:
            self.__movies_layout.addLayout(self.__row_layouts[-1])
        elif self.main_window.browse_menu is not None:
            scroll_bar = self.main_window.browse_menu.scroll_bar
            if scroll_bar.value() == scroll_bar.maximum():
                scroll_bar.setValue(scroll_bar.maximum() - 1)

    def __create_movie_widget(self, movie_id: str) -> MovieWidget | None:
        if movie_widget := MovieWidget(movie_id, self):
            movie_widget.poster_button.clicked.connect(
                lambda self=self, movie_id=movie_id: self.show_movie_menu(movie_id)
            )
            self.movie_widgets[movie_id] = movie_widget
            return movie_widget
        return None
