"""Legacy 'Select Experiment' / navigation helpers."""

from typing import Optional

from customtkinter import (  # type: ignore[import]
    CTk,
    CTkButton,
    CTkFrame,
    TOP,
    CENTER,
)

from shared.tk_models import MouserPage  
from experiment_pages.create_experiment.new_experiment_ui import (  
    NewExperimentUI,
)


class NewExperimentButton(CTkButton):  # pylint: disable=too-few-public-methods
    """Button that navigates to the New Experiment UI."""

    def __init__(self, parent: CTk, page: CTkFrame):
        super().__init__(
            page,
            text="Create New Experiment",
            compound=TOP,
            width=22,
            command=lambda: (self.create_next_page(), self.navigate()),
        )
        self.place(relx=0.85, rely=0.15, anchor=CENTER)
        self.parent = parent
        self.page = page
        self.next_page: Optional[NewExperimentUI] = None

    def create_next_page(self) -> None:
        """Instantiate the New Experiment UI as the next page."""
        self.next_page = NewExperimentUI(self.parent, self.page)

    def navigate(self) -> None:
        """Raise the next page, if it exists."""
        if self.next_page is not None:
            self.next_page.raise_frame()


class ExperimentsUI(  # pylint: disable=too-many-ancestors
    MouserPage
):
    """Container page for experiment-related navigation."""

    def __init__(self, parent: CTk, prev_page: Optional[CTkFrame] = None):
        super().__init__(parent, "Mouser")
        self.previous = prev_page
        self.parent = parent
