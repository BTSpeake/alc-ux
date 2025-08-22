"""Contains functions/classes for managing ALC developed AiiDA plugins."""

from importlib import import_module
from pathlib import Path

import ipywidgets as ipw
import yaml
from IPython.display import display

from aiidalab_alc.utils import get_app_dir, run_subprocess


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

    def install(self) -> None:
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
            pass
        else:
            pass

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
            pass
        else:
            pass


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
        self.plugin = plugin
        btns = ipw.HBox()
        install_btn = ipw.Button(
            description="Install",
            buttons_style="success",
            disabled=self.plugin.installed,
        )
        remove_btn = ipw.Button(
            description="Remove",
            buttons_style="danger",
            disabled=not self.plugin.installed,
        )
        btns.children = [install_btn, remove_btn]

        info = ipw.HTML(
            f"""
            <b>Description:</b> {plugin.description}<br>
            """
        )

        self.title = f"{plugin.name} {'✅' if plugin.installed else ''}"

        super().__init__(children=[info, btns], **kwargs)


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
        self.accordion = ipw.Accordion()

        self.plugin_widgets = []
        for i, plugin in enumerate(plugin_list):
            box = PluginBoxWidget(plugin)
            self.accordion.set_title(i, box.title)
            self.plugin_widgets.append(box)
        self.accordion.children = self.plugin_widgets

        self.children = [
            self.accordion,
        ]

        super().__init__(children=self.children, **kwargs)
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
