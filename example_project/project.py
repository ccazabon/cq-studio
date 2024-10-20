import cadquery as cq
# This imports the `Size` and `CylinderSize` helper classes from cq-studio, along with
# several trigonometric functions related to sagitta (height of an arc) not provided in the
# Python standard library `math` module.
from cq_studio import *


size_block = Size(20, 100, 120)
size_ball = 50  # diameter, not radius
size_bearing_hole = CylinderSize(40, size_block.w)
size_dowels = CylinderSize(2.5, size_block.w)
# how far in from the corners of the block the dowel pin holes are
offset_dowels = 10.0
size_axle = CylinderSize(8.0, 200)


def make_block():
    wp = cq.Workplane("XY")
    block = (
        wp.box(*size_block, centered=center_w)
        .faces("<X")
        .workplane(centerOption="CenterOfMass")
        .tag("top")
        .rect(
            size_block.d - 2 * offset_dowels,
            size_block.h - 2 * offset_dowels,
            forConstruction=True,
        )
        .vertices()
        .hole(size_dowels.d)
        .workplaneFromTagged("top")
        .hole(size_bearing_hole.d)
    )
    # robin's-egg blue/turquoise
    block.colour = (0, 1.0, 1.0)
    return block


def make_ball():
    wp = cq.Workplane("XY")
    ball = wp.sphere(radius=size_ball / 2)
    ball.colour = (0.4, 0.4, 1.0)  # mauve
    return ball


def make_dowel():
    wp = cq.Workplane("XY")
    dowel = wp.cylinder(*size_dowels)  # default centering on all axes
    # This colour won't get used because it is overridden in the descendent object
    # created in dowels() below.
    dowel.colour = (0, 0.0, 1.0)
    return dowel


def dowels():
    dowel = make_dowel().rotate((0, 0, 0), (0, 1, 0), 90)
    dowels = (
        (dowel.translate((0, offset_dowels, offset_dowels)))
        + (dowel.translate((0, size_block.d - offset_dowels, offset_dowels)))
        + (dowel.translate((0, offset_dowels, size_block.h - offset_dowels)))
        + (dowel.translate((0, size_block.d - offset_dowels, size_block.h - offset_dowels)))
    )
    dowels.color = (0.6, 0.2, 0.9)  # Or use American spelling.  And why not purple?
    return dowels


def make_axle():
    wp = cq.Workplane("XY")
    axle = (
        wp.cylinder(*size_axle)
        .rotate((0, 0, 0), (0.3, 1, 0.3), 60)
        .translate((0, size_block.d / 2, size_block.h / 2))
    )
    axle.colour = (1.0, 0.2, 0)  # orange
    return axle


def main():
    # Can apply transformations here rather than where you create them if you just want to
    # move your models around to show assembly positions etc.
    #
    # By returning a dictionary, you can give your models meaningful names (which are shown
    # in the viewer when you expand the left control panel.
    return {
        "block": make_block(),
        "ball": (
            make_ball()
            .translate((0, size_block.d / 2, size_block.h / 2))
        ),
        "dowels": (
            dowels()
            .translate((-2 * size_dowels.h, 0, 0))
        ),
        "axle": make_axle(),
    }
