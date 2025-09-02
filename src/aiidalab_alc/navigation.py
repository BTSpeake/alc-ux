"""Defines navigation based components for the AiiDAlab ALC app."""

from functools import partial

from ipywidgets import Button, HBox

from aiidalab_alc.utils import open_link_in_new_tab


class QuickAccessButtons(HBox):
    """Quick access buttons present in the apps header and start banner."""

    def __init__(self, **kwargs):
        """
        QuickAccessButtons constructor.

        Parameters
        ----------
        **kwargs :
            Keyword arguments passed to the `ipywidgets.HBox.__init__()`.
        """
        self.new_calc_link = Button(
            description="New Calculation",
            disabled=False,
            button_style="success",
            tooltip="Start a new calculation",
            icon="plus",
        )
        self.new_calc_link.on_click(
            partial(open_link_in_new_tab, "../alc-ux/main.ipynb")
        )

        self.history_link = Button(
            description="History",
            disabled=False,
            button_style="primary",
            tooltip="View Calculation History",
            icon="history",
        )
        self.history_link.on_click(
            partial(open_link_in_new_tab, "../alc-ux/history.ipynb")
        )

        self.resource_setup_link = Button(
            description="Setup Resources",
            disabled=False,
            button_style="primary",
            tooltip="Configure Computational Resources",
            icon="cogs",
            # on_click=partial(onLinkClickt get_app_dir() / "../home/code_setup.ipynb"),
        )
        self.resource_setup_link.on_click(
            partial(open_link_in_new_tab, "../home/code_setup.ipynb")
        )

        self.plugin_manager_link = Button(
            description="Manage Plugins",
            disabled=False,
            button_style="primary",
            tooltip="Manage AiiDA plugins",
            icon="cogs",
        )
        self.plugin_manager_link.on_click(
            partial(open_link_in_new_tab, "../alc-ux/plugin_manager.ipynb")
        )

        self.docs_link = Button(
            description="Documentation",
            disabled=False,
            button_style="info",
            tooltip="Open Documentation",
            icon="book",
        )
        self.docs_link.on_click(
            partial(open_link_in_new_tab, "https://github.com/stfc/alc-ux")
        )

        children = [
            self.new_calc_link,
            self.history_link,
            self.resource_setup_link,
            self.plugin_manager_link,
            self.docs_link,
        ]
        super().__init__(
            children=children, layout={"margin": "auto", "width": "85%"}, **kwargs
        )
        return
