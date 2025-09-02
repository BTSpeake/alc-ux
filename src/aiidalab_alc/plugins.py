"""Contains functions/classes for managing ALC developed AiiDA plugins."""

from importlib import import_module
from pathlib import Path

import ipywidgets as ipw
import yaml
from IPython.display import display

from aiidalab_alc.navigation import QuickAccessButtons
from aiidalab_alc.utils import get_app_dir, get_app_footer, run_subprocess


class PluginData:
    """Data required to define an ALC developed AiiDA plugin."""

    def __init__(self, name: str, data: dict):
        """
        PluginData constructor.

        Parameters
        ----------
        name: str
            The plugin's name
        data: dict
            A dictionary of plugin parameters
        """
        self.name: str = name
        self.package: str = data["package"]
        self.import_str: str = data.get("import", self.package.replace("-", "_"))
        self.description: str = data["description"]
        self.installed: bool = self._is_plugin_loaded()
        return

    def _is_plugin_loaded(self) -> bool:
        """
        Check if a given plugin is installed or not.

        Parameters
        ----------
        plugin: str
            The name of the required python package
        """
        try:
            import_module(self.import_str)
        except ImportError:
            return False
        else:
            return True

    def install(self) -> str:
        """
        Installs the required python package for an AiiDA plugin.

        Parameters
        ----------
        plugin: str
            The name of the required python package
        """
        command = ["pip", "install", self.package, "--user"]
        result = run_subprocess(command)
        if result.returncode == 0:
            self.installed = True
            return result.stdout
        self.installed = False
        return result.stderr

    def uninstall(self) -> None:
        """
        Uninstalls the required python package for an AiiDA plugin.

        Parameters
        ----------
        plugin: str
            The name of the required python package
        """
        command = ["pip", "uninstall", self.package, "--user"]
        result = run_subprocess(command)
        if result.returncode == 0:
            self.installed = True
        else:
            self.installed = False


class PluginBoxWidget(ipw.VBox):
    """Widget for a given plugin to be added to a PluginManagerView."""

    def __init__(self, plugin: PluginData, **kwargs):
        """
        PluginBoxWidget constructor.

        Parameters
        ----------
        plugin : PluginData
            The associated plugin object.
        """
        self.rendered = False
        self.plugin = plugin
        self.btns = ipw.HBox()
        self.installed_label = ipw.HTML(
            f"""
            <b>Installed:</b> {"✅" if plugin.installed else "❌"}<br>
            """
        )
        self.info = ipw.HTML(
            f"""
            <b>Description:</b> {plugin.description}<br>
            """
        )
        self.install_report = ipw.Textarea(
            value="",
            placeholder="",
            description="",
            disabled=True,
            layout={"width": "90%", "margin": "auto"},
        )
        self.title = f"{plugin.name} {'✅' if plugin.installed else ''}"
        super().__init__(**kwargs)
        return

    def _install_plugin(self, _) -> None:
        """Install the associated plugin and update the widget."""
        stdout = self.plugin.install()
        self.text.value = stdout
        self.text.layout.display = ""
        self.installed_label.value = f"""
            <b>Installed: </b> {"✅" if self.plugin.installed else "❌"}<br>
            """
        self._update_buttons()
        return

    def _remove_plugin(self, _) -> None:
        """Uninstall the associated plugin and update the widget."""
        self.plugin.uninstall()
        self.installed_label.value = f"""
            <b>Installed: </b> {"✅" if self.plugin.installed else "❌"}<br>
            """
        self._update_buttons()
        return

    def _update_buttons(self) -> None:
        """Update the state of the install/remove buttons."""
        for child in self.children:
            if isinstance(child, ipw.HBox):
                for btn in child.children:
                    if btn.description == "Install":
                        btn.disabled = self.plugin.installed
                    elif btn.description == "Remove":
                        btn.disabled = not self.plugin.installed
        return

    def render(self) -> None:
        """Create the buttons and display the widget."""
        self.install_report.layout.display = "none"
        if not self.rendered:
            self.rendered = True
            self.install_btn = ipw.Button(
                description="Install",
                button_style="success",
                disabled=self.plugin.installed,
                tooltip=f"Install the {self.plugin.name} plugin",
            )
            self.install_btn.on_click(self._install_plugin)
            self.remove_btn = ipw.Button(
                description="Remove",
                button_style="danger",
                disabled=not self.plugin.installed,
                tooltip=f"Uninstall the {self.plugin.name} plugin",
            )
            self.remove_btn.on_click(self._remove_plugin)
            self.btns.children = [self.install_btn, self.remove_btn]
            self.children = [
                self.installed_label,
                self.info,
                self.btns,
                self.install_report,
            ]
        return


class PluginManagerView(ipw.VBox):
    """View widget for the PluginManager."""

    def __init__(self, plugin_list: list[PluginData], **kwargs):
        """
        PluginManagerView constructor.

        Parameters
        ----------
        plugin_list: list[PluginData]
            A list of PluginData objects for all compatible plugins.
        **kwargs: dict
            To be passed to the parent class' constructor.
        """
        header = ipw.VBox(
            children=[
                ipw.HTML(
                    """
                    <h1 id='title'><b>ALC AiiDA Plugin Manager</b></h1>
                    """,
                    layout=ipw.Layout(margin="auto"),
                ),
                ipw.HTML(
                    "<h4 id='subtitle'>Manage installation of available AiiDA \
                        plugins developed by the ALC.</h4>",
                    layout=ipw.Layout(margin="auto"),
                ),
            ],
            layout={"width": "90%", "margin": "auto"},
        )

        self.accordion = ipw.Accordion()

        self.plugin_widgets = []
        for i, plugin in enumerate(plugin_list):
            box = PluginBoxWidget(plugin)
            self.accordion.set_title(i, box.title)
            self.plugin_widgets.append(box)
        self.accordion.children = self.plugin_widgets
        self.accordion.selected_index = None
        self.accordion.observe(self._on_accordion_change, "selected_index")

        footer = get_app_footer()

        super().__init__(
            children=[header, QuickAccessButtons(), self.accordion, footer], **kwargs
        )
        return

    def _on_accordion_change(self, change) -> None:
        """Render the selected plugin's widget."""
        if (step_index := change["new"]) is not None:
            self.accordion.children[step_index].render()
        return


class PluginManager:
    """Manage ALC developed AiiDA plugins."""

    def __init__(self):
        """PluginManager constructor."""
        self.plugins = PluginManager._get_plugin_list()
        self.view = PluginManagerView(self.plugins)
        display(self.view)

        return

    @classmethod
    def _get_plugin_list(cls, path: Path = None) -> list[PluginData]:
        """
        Retrieve the list of compatible AiiDA workflow plugins.

        Parameters
        ----------
        path : pathlib.Path | None
            The path to the yaml file containing the plugins and their
            definitions

        Returns
        -------
        plugins : list[PluginData]
            A list of PluginData objects for each compatible plugin.
        """
        if not path:
            path = get_app_dir() / "Resources/plugin_list.yml"
        plugins = []
        try:
            with open(path) as file:
                data = yaml.safe_load(file)
        except (FileNotFoundError, yaml.YAMLError) as e:
            print(f"WARNING: Failed to load plugin list from {path}")
            print(f"{e}")
        else:
            for key in data:
                plugins.append(PluginData(key, data[key]))
        return plugins
