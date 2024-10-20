import math


def sagitta(radius: float, chord_length: float) -> float:
    """Calculate the height of an arc from its radius and chord half-length.

    Length is to the midpoint of the arc/chord, i.e. where its height is measured, not the
    length of the whole chord.
    """
    height = radius - math.sqrt((radius**2) - (chord_length**2))
    return height


def chord_length_from_sagitta_and_radius(sagitta: float, radius: float) -> float:
    """Calculate the half-length of a chord / width of an arc from its radius and height.

    Length is to the midpoint of the arc/chord, i.e. where its height is measured, not the
    length of the whole chord.
    """
    length = math.sqrt(2 * sagitta * radius - sagitta**2) / 2
    return length


def radius_from_sagitta_and_chord_length(sagitta: float, chord_length: float) -> float:
    """Calculate the radius of an arc from its chord half-length and sagitta.

    Length is to the midpoint of the arc/chord, i.e. where its height is measured, not the
    length of the whole chord.
    """
    radius = (sagitta**2 + chord_length**2) / (2 * sagitta)
    return radius


def sagitta_from_radius_and_arc_length(radius: float, arc_length: float) -> float:
    """Calculate the height of an arc from its radius and arc length.

    Arc length is measured like circumference, and with radius can be used to calculate the
    sagitta/arc height.
    """
    chord_length = radius * math.sin(arc_length / (2 * radius))
    return sagitta(radius, chord_length)


def angle_from_radius_and_chord_length(radius: float, chord_length: float) -> float:
    """Calculate the angle of a circle occupied by a chord of a given half-length.

    Length is to the midpoint of the arc/chord, i.e. where its height is measured, not the
    length of the whole chord.

    Return value is in degrees, not radians, as CadQuery uses degrees.
    """
    arc_height = sagitta(radius, chord_length)
    y = radius - arc_height
    x = chord_length
    angle = math.degrees(math.atan2(y, x))
    return 2 * angle
