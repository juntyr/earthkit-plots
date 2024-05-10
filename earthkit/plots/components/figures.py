# Copyright 2024, European Centre for Medium Range Weather Forecasts.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import matplotlib.pyplot as plt

from earthkit.plots.components.subplots import Subplot
from earthkit.plots.components.layers import LayerGroup
from earthkit.plots.components.maps import Map
from earthkit.plots.metadata import formatters
from earthkit.plots.schemas import schema
from earthkit.plots.utils import string_utils


class Figure:
    
    def __init__(self, rows=1, columns=1, size=None, domain=None, **kwargs):
        self.rows = rows
        self.columns = columns
        
        self._row = 0
        self._col = 0
        
        self.fig = plt.figure(figsize=size, constrained_layout=True)
        self.gridspec = self.fig.add_gridspec(rows, columns, **kwargs)
        
        self._domain = domain
        
        self.subplots = []
        self._last_subplot_location = None
        self._isubplot = 0
    
    def __len__(self):
        return len(self.subplots)

    def __getitem__(self, i):
        return self.subplots[i]

    def apply_to_subplots(method):
        def wrapper(self, *args, **kwargs):
            success = False
            for subplot in self.subplots:
                try:
                    getattr(subplot, method.__name__)(*args, **kwargs)
                    success = True
                except (NotImplementedError, AttributeError):
                    continue
            if not success:
                raise NotImplementedError(
                    f"No subplots have method '{method.__name__}'"
                )
        return wrapper
    
    def _determine_row_column(self, row, column):
        if row is not None and column is not None:
            pass
        else:
            if self._last_subplot_location is None:
                row, column = (0, -1)
            if row is None:
                row = self._last_subplot_location[0]
            if column is None:
                column = self._last_subplot_location[1]
        if column < self.columns-1:
            column = column + 1
        else:
            column = 0
            row = row + 1
        self._last_subplot_location = row, column
        return row, column

    def add_subplot(self, row=None, column=None, **kwargs):
        row, column = self._determine_row_column(row, column)
        subplot = Subplot(row=row, column=column, figure=self, **kwargs)
        self.subplots.append(subplot)
        return subplot

    def add_map(self, row=None, column=None, domain=None, **kwargs):
        if domain is None:
            domain = self._domain
        row, column = self._determine_row_column(row, column)
        subplot = Map(row=row, column=column, domain=domain, figure=self, **kwargs)
        self.subplots.append(subplot)
        return subplot
    
    def subplot_titles(self, *args, **kwargs):
        return [subplot.title(*args, **kwargs) for subplot in self.subplots]

    def distinct_legend_layers(self, subplots=None):
        """
        Get a list of layers with distinct styles.

        Parameters
        ----------
        subplots : list, optional
            If provided, only these subplots will be considered when identifying
            unique styles.
        """
        if subplots is None:
            subplots = self.subplots

        subplot_layers = [subplot.distinct_legend_layers for subplot in subplots]
        subplot_layers = [item for sublist in subplot_layers for item in sublist]

        groups = []
        for layer in subplot_layers:
            for i in range(len(groups)):
                if groups[i][0].style == layer.style:
                    groups[i].append(layer)
                    break
            else:
                groups.append([layer])

        groups = [LayerGroup(layers) for layers in list(groups)]

        return groups

    @schema.legend.apply()
    def legend(self, *args, subplots=None, location=None, **kwargs):
        """
        Add legends to the chart for all subplots.

        Parameters
        ----------

        """
        legends = []

        anchor = None
        non_cbar_layers = []
        for i, layer in enumerate(self.distinct_legend_layers(subplots)):
            if isinstance(location, (list, tuple)):
                loc = location[i]
            else:
                loc = location
            if layer.style is not None:
                legend = layer.style.legend(
                    layer,
                    *args,
                    location=loc,
                    **kwargs,
                )
            if legend.__class__.__name__ != "Colorbar":
                non_cbar_layers.append(layer)
            else:
                anchor = layer.axes[0].get_anchor()
            legends.append(legend)

        if anchor is not None:
            for layer in non_cbar_layers:
                for ax in layer.axes:
                    ax.set_anchor(anchor)

        return legends
    
    @apply_to_subplots
    def coastlines(self, *args, **kwargs):
        """"""
    
    @apply_to_subplots
    def countries(self, *args, **kwargs):
        """"""
    
    @apply_to_subplots
    def land(self, *args, **kwargs):
        """"""
    
    @apply_to_subplots
    def borders(self, *args, **kwargs):
        """"""
    
    @apply_to_subplots
    def administrative_areas(self, *args, **kwargs):
        """"""
    
    @apply_to_subplots
    def stock_img(self, *args, **kwargs):
        """"""
    
    def gridlines(self, *args, sharex=False, sharey=False, **kwargs):
        draw_labels = kwargs.pop("draw_labels", ["left", "bottom"])
        if draw_labels is True:
            draw_labels = ["left", "right", "bottom", "top"]
        for subplot in self.subplots:
            subplot_draw_labels = [item for item in draw_labels]
            if sharex:
                if "top" in draw_labels and subplot.row != 0:
                    subplot_draw_labels = [loc for loc in subplot_draw_labels if loc != "top"]
                if "bottom" in draw_labels and subplot.row != max(sp.row for sp in self.subplots):
                    subplot_draw_labels = [loc for loc in subplot_draw_labels if loc != "bottom"]
            if sharey:
                if "left" in draw_labels and subplot.column != 0:
                    subplot_draw_labels = [loc for loc in subplot_draw_labels if loc != "left"]
                if "right" in draw_labels and subplot.column != max(sp.column for sp in self.subplots):
                    subplot_draw_labels = [loc for loc in subplot_draw_labels if loc != "right"]
            subplot.gridlines(*args, draw_labels=subplot_draw_labels, **kwargs)


    @schema.title.apply()
    def title(self, label=None, unique=True, grouped=True, y=None, **kwargs):
        """
        Add a top-level title to the chart.

        Parameters
        ----------
        label : str, optional
            The text to use in the title. This text can include format keys
            surrounded by `{}` curly brackets, which will extract metadata from
            your plotted data layers.
        unique : bool, optional
            If True, format keys which are uniform across subplots/layers will
            produce a single result. For example, if all data layers have the
            same `variable_name`, only one variable name will appear in the
            title.
            If False, each format key will evaluate to a list of values found
            across subplots/layers.
        grouped : bool, optional
            If True, a single title will be generated to represent all data
            layers, with each format key evaluating to a list where layers
            differ - e.g. `"{variable} at {time}"` might be evaluated to
            `"temperature and wind at 2023-01-01 00:00".
            If False, the title will be duplicated by the number of subplots/
            layers - e.g. `"{variable} at {time}"` might be evaluated to
            `"temperature at 2023-01-01 00:00 and wind at 2023-01-01 00:00".
        kwargs : dict, optional
            Keyword argument to matplotlib.pyplot.suptitle (see
            https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.suptitle.html#matplotlib-pyplot-suptitle
            ).
        """
        if label is None:
            label = self._default_title_template
        label = self.format_string(label, unique, grouped)

        self.fig.canvas.draw()
        return self.fig.suptitle(label, y=y, **kwargs)

    def format_string(self, string, unique=True, grouped=True):
        if not grouped:
            results = [
                subplot.format_string(string, unique, grouped)
                for subplot in self.subplots
            ]
            result = string_utils.list_to_human(results)
        else:
            result = formatters.FigureFormatter(self.subplots, unique=unique).format(string)
        return result

    @property
    def _default_title_template(self):
        return self.subplots[0]._default_title_template

    def show(self, *args, **kwargs):
        return plt.show(*args, **kwargs)

    def save(self, *args, bbox_inches="tight", **kwargs):
        return plt.savefig(*args, bbox_inches=bbox_inches, **kwargs)