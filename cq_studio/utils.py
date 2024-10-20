import math

import cadquery as cq


class Size(list):
    """A fixed-size list for 2- or 3-dimensional sizes (in width, depth, height order) with
    meaningful named attributes to access the individual values.

    Use like `cadquery.workplane("XY).bow(*sizeobj)`.

    Note CadQuery confusingly uses "length" for the dimension *across* the normal view of an
    XY plane, and "width" for the dimension perpendicular to the screen/viewport.
    A viewer would instead probably consider the first one the "width" of the object.
    So this class uses width, depth, height for the axes' names, and avoids length entirely.
    """

    def __init__(self, w: float, d: float, h: float | None = None):
        super().__init__([w, d, h])

    @property
    def w(self) -> float:
        """Width."""
        return self[0]

    @property
    def d(self) -> float:
        """Depth."""
        return self[1]

    @property
    def h(self) -> float | None:
        """Height."""
        return self[2]


class CylinderSize(list):
    """A fixed-size list for defining the size of a cylinder (height and radius), with
    meaningful named attributes to access the individual values (or the derived diameter).

    Use like `cadquery.workplane("XY).cylinder(*sizeobj)`.

    Note some of CadQuery's cylinder-related methods use (height, radius), while others use
    (radius, height) or even (diameter, height).  This uses the (radius, height) order of
    parameters, which is more natural to me and seems to be used more commonly in other
    contexts.
    """

    def __init__(self, r: float, h: float):
        super().__init__([h, r])

    @property
    def r(self) -> float:
        """Radius."""
        return self[1]

    @property
    def h(self) -> float:
        """Height."""
        return self[0]

    @property
    def d(self) -> float:
        """Diameter."""
        return 2 * self.r


def support_snip(
    wp: cq.Workplane,
    length: float,
    thickness: float,
    solid_join_size: float = 0.4,
    trim_rear_width: float | None = None,
) -> cq.Workplane:
    """This is an early attempt at a function for making breakaway parts/walls, such as when
    you have to manually design support into a model to make it printable.  I'm not going to
    document it yet as it is in flux.
    """
    if trim_rear_width is None:
        # default to 2 * thickness so it doesn't cut through end walls on the inside edge
        trim_rear_width = 2 * thickness
    half_thickness = thickness / 2
    snip_front = wp.box(length, thickness, thickness, centered=False).rotate(
        (0, half_thickness, half_thickness), (1, half_thickness, half_thickness), 45
    )
    snip_rear = (
        wp.box(length - trim_rear_width, thickness, thickness, centered=False)
        .rotate(
            (0, half_thickness, half_thickness), (1, half_thickness, half_thickness), 45
        )
        .translate((trim_rear_width / 2, 0, 0))
    )
    diagonal = thickness * math.sqrt(2)
    offset = (diagonal + solid_join_size) / 2
    return snip_front.translate(
        (0, -offset - half_thickness, -half_thickness)
    ) + snip_rear.translate((0, offset - half_thickness, -half_thickness))
