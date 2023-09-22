# Copyright 2023, European Centre for Medium Range Weather Forecasts.
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

try:
    # NOTE: the `version.py` file must not be present in the git repository
    #   as it is generated by setuptools at install time
    from .version import __version__
except ImportError:  # pragma: no cover
    # Local copy or not installed with setuptools
    __version__ = "999"


from . import figures
from .schema import schema


@figures.Figure.new_if_none()
def line(*args, fig=None, **kwargs):
    return fig.add_line(*args, **kwargs)


@figures.Figure.new_if_none()
def scatter(*args, fig=None, **kwargs):
    return fig.add_scatter(*args, **kwargs)


@figures.Figure.new_if_none()
def bar(*args, fig=None, **kwargs):
    return fig.add_bar(*args, **kwargs)


@figures.Figure.new_if_none()
def envelope(*args, fig=None, **kwargs):
    return fig.add_envelope(*args, **kwargs)


@figures.Figure.new_if_none(schema=schema.figures.stripes)
def stripes(*args, fig=None, **kwargs):
    return fig.add_stripes(*args, **kwargs)