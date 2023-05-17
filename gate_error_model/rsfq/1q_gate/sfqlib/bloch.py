from numpy import (array, linspace, pi, outer, cos, sin, ones, size,
                   sqrt, real, dot, transpose, conj)
from numpy.linalg import norm
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from itertools import count


def sigma_x(): return array([[0.0, 1.0], [1.0, 0.0]])


def sigma_y(): return array([[0.0 + 0.0j, 0.0 - 1.0j], [0. + 1.0j, 0.0 + 0.0j]])


def sigma_z(): return array([[1.0, 0.0], [0.0, -1.0]])


def expect(opt, ket):
    """Compute the expectation value <ket|opt|ket>."""
    return float(real(dot(dot(conj(transpose(ket)), opt), ket)))


def expect_vec(ket):
    """Compute the expectation value of the S vector operator."""
    return [expect(sigma_x(), ket), expect(sigma_y(), ket),
            expect(sigma_z(), ket)]


class ProjectionDoesNotExist(Exception):
    def __init__(self, project_source):
        message = 'Projection '  + project_source + ' Does not exist.'
        super(ProjectionDoesNotExist, self).__init__(message)


class VectorPlot():
    """Represent a plotted vector. This class is written for the convenience of removing the vector from plot."""
    def __init__(self,vec, vec_ax, text_ax):
        self.vec, self.vec_ax, self.text_ax = vec, vec_ax, text_ax
    def remove(self):
        """Remove the vector and the text if applicable."""
        self.vec_ax.remove()
        if self.text_ax:
            self.text_ax.remove()


class VectorPlotStream():
    """A stream of plotted vector, with misc information. This can be used to represent the time evolution of a ket."""
    def __init__(self, vec_list, color, text):
        self.vec_list, self.color, self.text = vec_list, color, text

    def __getattr__(self, attr):
        return getattr(self.vec_list, attr)


class Bloch():
    """The bloch sphere for visualization of a two level system."""
    def __init__(self, axes, background=False):
        self.axes = axes
        self.background = background
        self.sphere_color, self.sphere_alpha = 'azure', 0.2
        self.frame_width, self.frame_alpha = 1, 0.2
        self.frame_color = 'gray'
        self.projection_source = 'origin'
        self.vec_streams = None
        self._config_axes()
        self._plot_sphere_angles(linspace(0, pi, 15), linspace(0, pi, 15))
        self._plot_sphere_angles(linspace(-pi, 0, 15), linspace(0, pi, 15))
        self.color_generator = _gen_color()
        self.clear()

    def clear(self):
        """Clean the bloch sphere. Remove all vector streams."""
        if self.vec_streams:
            for vec_stream in self.vec_streams:
                for plotted_vec in vec_stream.vec_list:
                    plotted_vec.remove()
        self.vec_streams = dict()

    def set_projection_source(self, projection_source):
        """Set the source of projection, which project a point in space onto the bloch sphere.
        If set to 'origin', the point will be projected along the r direction.
        if set to 'z-axis', the point will be projected along the rho direction.
        :param projection_source: Either 'origin' or 'z-axis' """
        if projection_source != 'origin' and projection_source != 'z-axis':
            raise ProjectionDoesNotExist(projection_source)
        else:
            self.projection_source = projection_source

    def shovel_ket(self, ket, id, trace=False, text=""):
        """Add a ket onto the bloch sphere. Replace the old one with the same id.
        :param ket: The ket to add
        :param id: The ket to replace
        :param trace: Whether the trajectory should be draw between the replaced ket and the new ket.
        :param text: Label on the ket. """

        # Create a new stream if the id is encountered for the first time.
        vec_stream = self.vec_streams.get(
            id, VectorPlotStream([], color=self.color_generator.next(), text=text))
        # Use the old text if a new one is not provided.
        text, vec_stream.text =  (vec_stream.text, vec_stream.text) if text == "" else (text, text)
        vec = expect_vec(ket)
        vec_norm = norm(vec)
        vec = vec / vec_norm if vec_norm != 0 else vec
        vec_ax = self.axes.scatter([vec[0]], [vec[1]], [vec[2]], color=vec_stream.color, marker='o', s=100)
        text_ax = self.axes.text(vec[0], vec[1], vec[2]+0.05, text)
        vec_stream.append(VectorPlot(vec, vec_ax, text_ax))
        if len(vec_stream) > 1:
            old_vec_plt = vec_stream.pop(0)
            old_vec_plt.remove()
            if trace:
                self._interpolate(old_vec_plt.vec, vec, color=vec_stream.color)
        else:
            self.vec_streams[id] = vec_stream

    def _project(self, vec):
        vec_norm = norm(vec)
        if self.projection_source == 'origin':
            return [v / vec_norm for v in vec]  if vec_norm != 0 else vec
        if self.projection_source == 'z-axis': # If source is z axis
            x, y, z = vec
            xy_scale, xy_norm = sqrt(1 - pow(z, 2)), norm([x, y])
            x, y = (x * xy_scale / xy_norm, y * xy_scale / xy_norm) if xy_norm != 0 else (x, y)
            return [x, y, z]

    def _interpolate(self, old_vec, new_vec, color='b'):
        # First make a straight line connecting the two vectors.
        vector_collection = [linspace(n_c, o_c, 5) for n_c, o_c in zip(old_vec, new_vec)]
        # Project straight line onto the Bloch sphere
        for index, vec in enumerate(zip(*vector_collection)):
            projected_vec = self._project(vec)
            for i in range(3):
                vector_collection[i][index] = projected_vec[i]
        linewidth = 0.3 if self.projection_source == 'z-axis' else 1.0 # Thin line for precession
        self.axes.plot(*vector_collection, color=color, linewidth=linewidth)

    def _plot_sphere_angles(self, u, v):
        x, y = 0.9 * outer(cos(u), sin(v)), outer(sin(u), sin(v))
        z = 0.9 * outer(ones(size(u)), cos(v))
        self.axes.plot_surface(x, y, z, rstride=2, cstride=2,
                               color=self.sphere_color, linewidth=0,
                               alpha=self.sphere_alpha)
        # Plot the equators.
        self.axes.plot(1.0 * cos(u), 1.0 * sin(u), zs=0, zdir='z',
                       lw=self.frame_width, color=self.frame_color)
        self.axes.plot(1.0 * cos(u), 1.0 * sin(u), zs=0, zdir='x',
                       lw=self.frame_width, color=self.frame_color)

    def _config_axes(self):
        span = linspace(-1.0, 1.0, 2)
        # Plot the axes
        self.axes.plot(xs=span, ys=span*0, zs=span*0, label='X',
                       lw=self.frame_width, color=self.frame_color)
        self.axes.plot(xs=0*span, ys=span, zs=span*0, label='Y',
                       lw=self.frame_width, color=self.frame_color)
        self.axes.plot(xs=0*span, ys=span*0, zs=span, label='Z',
                       lw=self.frame_width, color=self.frame_color)
        self.axes.set_axis_off()
        self.axes.set_xlim3d(-0.7, 0.7)
        self.axes.set_ylim3d(-0.7, 0.7)
        self.axes.set_zlim3d(-0.7, 0.7)
        self.axes.grid(False)

    def __getattr__(self, attr): return getattr(self.axes, attr)


def _gen_color():
    """A color generator that attempts to generate distinct color every time."""
    rgb = [(0.5, 0, 0), (0, 0.5, 0), (0, 0, 0.5)]
    for i in count():
        yield tuple((c + (0.2 * i) % 1) % 1 for c in rgb[i%3])


# def test_shovel_kets():
#     fig = plt.figure(figsize=(10, 10))
#     axes = fig.gca(projection='3d')
#     b = Bloch(fig=fig, axes=axes)
#     ket = array([[0], [1]])
#     ket_2 = array([[1.0/sqrt(2)], [1.0/sqrt(2)]])
#
#
#
# fig = plt.figure(figsize=(10, 10))
# axes = fig.gca(projection='3d')
# b = Bloch(fig=fig, axes=axes)
# plt.ion()
# ket_1 = array([[0], [1]])
# ket_2 = array([[1.0/sqrt(2)], [1.0/sqrt(2)]])
# ket_3 = array([[1.0j/sqrt(2)], [1.0/sqrt(2)]])
# b.shovel_ket(ket_1, 1, trace=True, text="Stream1")
# b.shovel_ket(ket_2, 1, trace=True)
# b.shovel_ket(ket_3, 1, trace=True)
#
# ket_1 = array([[1], [0]])
# ket_2 = array([[1.0/sqrt(2)], [1.0/sqrt(2)]])
# ket_3 = array([[1.0/sqrt(2)], [1.0j/sqrt(2)]])
# b.shovel_ket(ket_1, 2, trace=True, text="Stream2")
# b.shovel_ket(ket_2, 2, trace=True)
# b.shovel_ket(ket_3, 2, trace=True)
# plt.show()



#        old_theta, old_phi = self.polar_angle(old_vec)
#        new_theta, new_phi = self.polar_angle(new_vec)
#
#        if old_phi and new_phi:
#            pass
#        elif new_phi and not old_phi:
#            old_phi = new_phi
#        elif old_phi and not new_phi:
#            new_phi = old_phi
#        else:
#            old_phi, new_phi = pi/2
#
#        angle_space = zip(linspace(old_theta, new_theta, 100),
#                          linspace(old_phi, new_phi, 100))
#        xx = [sin(theta) * cos(phi) for theta, phi in angle_space]
#        yy = [sin(theta) * sin(phi) for theta, phi in angle_space]
#        zz = [cos(theta) for theta, phi in angle_space]
#        self.axes.plot(xx, yy, zz, color=color)


#     @staticmethod
#     def polar_angle(vec):
#         theta = arccos(vec[2])
#         if round(sin(theta), 7) != 0:
#             phi = arccos(vec[0]/sin(theta))
#             phi = phi if vec[1] > 0 else 2*pi-phi
#         else:
#             phi = None
#         return theta, phi

