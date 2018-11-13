#!/usr/bin/env python2.7

from __future__ import division, absolute_import

from traits.api import (HasStrictTraits, Str, CStr, List, Float, provides, Instance, Bool, on_trait_change, DelegatesTo, Any, Constant)

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import scale
import numpy as np

import cytoflow.utility as util
import cytoflow.views

from .i_operation import IOperation

@provides(IOperation)
class EllipseOp(HasStrictTraits):
    id = Constant('edu.mit.synbio.cytoflow.operations.ellipse')
    friendly_id = Constant("Ellipse")

    name = CStr()
    xchannel = Str()
    ychannel = Str()
    vertices = List((Float, Float))

    _xscale = Str("linear")
    _yscale = Str("linear")

    center =
    width =
    height =
    angle =


    def _plot_ellipse(self, center, width, height, angle, **kwargs):
        tf = transforms.Affine2D() \
             .scale(width * 0.5, height * 0.5) \
             .rotate_deg(angle) \
             .translate(*center)

        tf_path = tf.transform_path(path.Path.unit_circle())
        v = tf_path.vertices
        v = np.vstack((self.op._xscale.inverse(v[:, 0]),
                       self.op._yscale.inverse(v[:, 1]))).T

        scaled_path = path.Path(v, tf_path.codes)
        scaled_patch = patches.PathPatch(scaled_path, **kwargs)
        plt.gca().add_patch(scaled_patch)


    name = CStr()
    xchannel = Str()
    ychannel = Str()
    vertices = List((Float, Float))


