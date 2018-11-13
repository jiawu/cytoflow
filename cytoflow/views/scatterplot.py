#!/usr/bin/env python2.7

# (c) Massachusetts Institute of Technology 2015-2016
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Created on Apr 19, 2015

@author: brian
"""

from traits.api import HasStrictTraits, provides, Str

import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import timeit
import re

import cytoflow.utility as util
from .i_view import IView
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.colors as colors
import matplotlib.cm as cmx

from scipy.stats import gaussian_kde

@provides(IView)
class ScatterplotView(HasStrictTraits):
    """
    Plots a 2-d scatterplot.

    Attributes
    ----------

    name : Str
        The name of the plot, for visualization (and the plot title)

    xchannel : Str
        The channel to plot on the X axis

    xscale : Enum("linear", "log", "logicle") (default = "linear")
        What scale to use on the X axis

    ychannel : Str
        The channel to plot on the Y axis

    yscale : Enum("linear", "log", "logicle") (default = "linear")
        The scale to use on the Y axis

    xfacet : Str
        The conditioning variable for multiple plots (horizontal)

    yfacet = Str
        The conditioning variable for multiple plots (vertical)

    huefacet = Str
        The conditioning variable for multiple plots (color)

    subset = Str
        A string passed to pandas.DataFrame.query() to subset the data before
        we plot it.

        .. note: should this be a param instead?
    """

    id = 'edu.mit.synbio.cytoflow.view.scatterplot'
    friend_id = "Scatter Plot"

    name = Str
    xchannel = Str
    xscale = util.ScaleEnum
    ychannel = Str
    yscale = util.ScaleEnum
    xfacet = Str
    yfacet = Str
    huefacet = Str
    subset = Str

    def plot(self, experiment, size = 6, vertices_list = None, gradient = False, save = None, **kwargs):
        """Plot a faceted scatter plot view of a channel"""

        if not experiment:
            raise util.CytoflowViewError("No experiment specified")

        if not self.xchannel:
            raise util.CytoflowViewError("X channel not specified")

        if self.xchannel not in experiment.data:
            raise util.CytoflowViewError("X channel {0} not in the experiment"
                                    .format(self.xchannel))

        if not self.ychannel:
            raise util.CytoflowViewError("Y channel not specified")

        if self.ychannel not in experiment.data:
            raise util.CytoflowViewError("Y channel {0} not in the experiment"
                                         .format(self.ychannel))

        if self.xfacet and self.xfacet not in experiment.conditions:
            raise util.CytoflowViewError("X facet {0} not in the experiment"
                                         .format(self.xfacet))

        if self.yfacet and self.yfacet not in experiment.conditions:
            raise util.CytoflowViewError("Y facet {0} not in the experiment"
                                         .format(self.yfacet))

        if self.huefacet and self.huefacet not in experiment.metadata:
            raise util.CytoflowViewError("Hue facet {0} not in the experiment"
                                         .format(self.huefacet))

        if self.subset:
            try:
                data = experiment.query(self.subset).data.reset_index()
            except:
                raise util.CytoflowViewError("Subset string '{0}' isn't valid"
                                        .format(self.subset))

            if len(data) == 0:
                raise util.CytoflowViewError("Subset string '{0}' returned no events"
                                        .format(self.subset))
        else:
            data = experiment.data

        legend = kwargs.pop('legend', False)

        kwargs.setdefault('alpha', 0.4)
        kwargs.setdefault('s', 2)
        kwargs.setdefault('marker', 'o')
        kwargs.setdefault('antialiased', True)

        xscale = util.scale_factory(self.xscale, experiment, self.xchannel)
        yscale = util.scale_factory(self.yscale, experiment, self.ychannel)

        if gradient:
            kwargs.setdefault('cmap', plt.get_cmap('Spectral_r'))
            kwargs.setdefault('edgecolor', '')
            g,ax = plt.subplots(figsize = (7,4))
            idx = data['density'].values.argsort()
            #ax.scatter(data[self.xchannel][idx], data[self.ychannel][idx], c=data['density'][idx], s=10, edgecolor='', cmap = 'Spectral_r')
            ax.scatter(data[self.xchannel], data[self.ychannel], c=data['density'], s=4, edgecolor='', cmap = 'Spectral_r')
            ax.set_xscale(self.xscale, **xscale.mpl_params)
            ax.set_yscale(self.yscale, **yscale.mpl_params)

        else:
            g = sns.FacetGrid(data,
                              size = size,
                              aspect = 1.5,
                              col = (self.xfacet if self.xfacet else None),
                              row = (self.yfacet if self.yfacet else None),
                              hue = (self.huefacet if self.huefacet else None),
                              col_order = (np.sort(data[self.xfacet].unique()) if self.xfacet else None),
                              row_order = (np.sort(data[self.yfacet].unique()) if self.yfacet else None),
                              hue_order = (np.sort(data[self.huefacet].unique()) if self.huefacet else None),
                              legend_out = False,
                              sharex = False,
                              sharey = False)
            for ax in g.axes.flatten():
                    ax.set_xscale(self.xscale, **xscale.mpl_params)
                    ax.set_yscale(self.yscale, **yscale.mpl_params)

        if vertices_list is not None:
            for vert, ind in vertices_list:
                patch_vert = np.concatenate((np.array(vert), np.array((0,0), ndmin = 2)))
                gate = mpl.patches.PathPatch(mpl.path.Path(patch_vert, closed = True), edgecolor = "black", linewidth = 2, fill = False)
                target_ax = g.axes[ind[0],ind[1]]
                target_ax.add_patch(gate)


        if gradient:
            def g_scatter(x, y, c, **kwargs):
                plt.scatter(x, y, c=c, **kwargs)
            #g.map(g_scatter, self.xchannel, self.ychannel, 'density', **kwargs)

        else:
            g.map(plt.scatter, self.xchannel, self.ychannel, **kwargs)

        # if we have an xfacet, make sure the y scale is the same for each
        fig = plt.gcf()
        fig_y_min = float("inf")
        fig_y_max = float("-inf")
        for ax in fig.get_axes():
            ax_y_min, ax_y_max = ax.get_ylim()
            if ax_y_min < fig_y_min:
                fig_y_min = ax_y_min
            if ax_y_max > fig_y_max:
                fig_y_max = ax_y_max

        for ax in fig.get_axes():
            ax.set_ylim(fig_y_min, fig_y_max)

        # if we have a yfacet, make sure the x scale is the same for each
        fig = plt.gcf()
        fig_x_min = float("inf")
        fig_x_max = float("-inf")

        for ax in fig.get_axes():
            ax_x_min, ax_x_max = ax.get_xlim()
            if ax_x_min < fig_x_min:
                fig_x_min = ax_x_min
            if ax_x_max > fig_x_max:
                fig_x_max = ax_x_max

        # if we have a hue facet and a lot of hues, make a color bar instead
        # of a super-long legend.

        if self.huefacet and legend:
            current_palette = mpl.rcParams['axes.color_cycle']
            if (experiment.conditions[self.huefacet] == "int" or
                experiment.conditions[self.huefacet] == "float") and \
                len(g.hue_names) > len(current_palette):

                plot_ax = plt.gca()
                cmap = mpl.colors.ListedColormap(sns.color_palette("husl",
                                                                   n_colors = len(g.hue_names)))
                cax, _ = mpl.colorbar.make_axes(plt.gca())
                norm = mpl.colors.Normalize(vmin = np.min(g.hue_names),
                                            vmax = np.max(g.hue_names),
                                            clip = False)
                mpl.colorbar.ColorbarBase(cax,
                                          cmap = cmap,
                                          norm = norm,
                                          label = self.huefacet)
                plt.sca(plot_ax)
            else:
                plot_ax = plt.gca()
                box = plot_ax.get_position()
                plot_ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
                legend = plot_ax.legend(bbox_to_anchor=(1.01, 1.0), loc=2, borderaxespad=0.)
                for label in legend.get_texts():
                        label.set_text(re.escape(label.get_text()))

                #g.add_legend(title = self.huefacet)

        if save:
            if 'png' in save:
                fig.savefig(save)
                plt.close()
            else:
                with PdfPages(save) as pdf:
                    pdf.savefig(fig)
                    plt.close()



if __name__ == '__main__':
    import cytoflow as flow
    tube1 = flow.Tube(file = '../../cytoflow/tests/data/Plate01/RFP_Well_A3.fcs',
                      conditions = {"Dox" : 10.0})

    tube2 = flow.Tube(file = '../../cytoflow/tests/data/Plate01/CFP_Well_A4.fcs',
                      conditions = {"Dox" : 1.0})

    ex = flow.ImportOp(conditions = {"Dox" : "float"}, tubes = [tube1, tube2])

    thresh = flow.ThresholdOp()
    thresh.name = "Y2-A+"
    thresh.channel = 'Y2-A'
    thresh.threshold = 200.0

    ex2 = thresh.apply(ex)

    scatter = flow.ScatterplotView()
    scatter.name = "Scatter"
    scatter.xchannel = "FSC-A"
    scatter.ychannel = "SSC-A"
    scatter.xscale = "logicle"
    scatter.yscale = "logicle"
    scatter.huefacet = 'Dox'

    plt.ioff()
    scatter.plot(ex2)
    plt.show()
