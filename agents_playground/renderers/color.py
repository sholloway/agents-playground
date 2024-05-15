from typing import NamedTuple, Tuple
from enum import Enum

"""RGBA Color Definition"""


class Color(NamedTuple):
    red: int
    green: int
    blue: int
    alpha: int = 255


class ColorUtilities:
    @staticmethod
    def invert(color: Color) -> Color:
        return Color(255 - color[0], 255 - color[1], 255 - color[2])


class PrimaryColors(Enum):
    red: Color = Color(255, 0, 0)
    green: Color = Color(0, 255, 0)
    blue: Color = Color(0, 0, 255)


class BasicColors(Enum):
    aqua: Color = Color(0, 255, 255)
    black: Color = Color(0, 0, 0)
    blue: Color = Color(0, 0, 255)
    cyan: Color = Color(0, 255, 255)
    fuchsia: Color = Color(217, 2, 125)
    gray: Color = Color(128, 128, 128)
    green: Color = Color(0, 128, 0)
    lime: Color = Color(0, 255, 0)
    magenta: Color = Color(255, 0, 255)
    maroon: Color = Color(128, 0, 0)
    navy: Color = Color(0, 0, 128)
    olive: Color = Color(128, 128, 0)
    purple: Color = Color(128, 0, 128)
    red: Color = Color(255, 0, 0)
    silver: Color = Color(192, 192, 192)
    teal: Color = Color(0, 128, 128)
    white: Color = Color(255, 255, 255)
    yellow: Color = Color(255, 255, 0)


# TODO: Sort these alphabetically
class Colors(Enum):
    aliceblue: Color = Color(239, 247, 255)
    antiquewhite: Color = Color(249, 234, 214)
    aqua: Color = Color(0, 255, 255)
    aquamarine: Color = Color(127, 255, 211)
    azure: Color = Color(239, 255, 255)

    bark: Color = Color(63, 48, 33)
    beige: Color = Color(244, 244, 219)
    bisque: Color = Color(255, 226, 196)
    black: Color = Color(0, 0, 0)
    blanchedalmond: Color = Color(255, 234, 204)
    blue: Color = Color(0, 0, 255)
    blueviolet: Color = Color(137, 43, 226)
    brown: Color = Color(165, 40, 40)
    burlywood: Color = Color(221, 183, 135)

    cadetblue: Color = Color(94, 158, 160)
    chartreuse: Color = Color(127, 255, 0)
    chocolate: Color = Color(209, 104, 30)
    coral: Color = Color(255, 127, 79)
    cornflowerblue: Color = Color(99, 147, 237)
    cornsilk: Color = Color(255, 247, 219)
    crimson: Color = Color(219, 20, 61)
    cyan: Color = Color(0, 173, 239)

    darkblue: Color = Color(0, 0, 140)
    darkcyan: Color = Color(0, 140, 140)
    darkgoldenrod: Color = Color(183, 135, 10)
    darkgray: Color = Color(168, 168, 168)
    darkgreen: Color = Color(0, 99, 0)
    darkkhaki: Color = Color(188, 183, 107)
    darkmagenta: Color = Color(140, 0, 140)
    darkolivegreen: Color = Color(84, 107, 45)
    darkorange: Color = Color(255, 140, 0)
    darkorchid: Color = Color(153, 51, 204)
    darkred: Color = Color(140, 0, 0)
    darksalmon: Color = Color(232, 150, 122)
    darkseagreen: Color = Color(142, 188, 142)
    darkslateblue: Color = Color(71, 61, 140)
    darkslategray: Color = Color(45, 79, 79)
    darkturquoise: Color = Color(0, 206, 209)
    darkviolet: Color = Color(147, 0, 211)
    deeppink: Color = Color(255, 20, 147)
    deepskyblue: Color = Color(0, 191, 255)
    dimgray: Color = Color(104, 104, 104)
    dimgrey: Color = Color(104, 104, 104)
    dodgerblue: Color = Color(30, 142, 255)

    firebrick: Color = Color(178, 33, 33)
    floralwhite: Color = Color(255, 249, 239)
    forestgreen: Color = Color(33, 140, 33)
    fuchsia: Color = Color(217, 2, 125)

    gainsboro: Color = Color(219, 219, 219)
    ghostwhite: Color = Color(247, 247, 255)
    gold: Color = Color(255, 214, 0)
    goldenrod: Color = Color(216, 165, 33)
    gray: Color = Color(127, 127, 127)
    green: Color = Color(0, 127, 0)
    greenyellow: Color = Color(173, 255, 45)
    grey: Color = Color(127, 127, 127)

    honeydew: Color = Color(239, 255, 239)
    hotpink: Color = Color(255, 104, 181)

    indianred: Color = Color(204, 91, 91)
    indigo: Color = Color(73, 0, 130)
    ivory: Color = Color(255, 255, 239)

    khaki: Color = Color(239, 229, 140)

    lavender: Color = Color(229, 229, 249)
    lavenderblush: Color = Color(255, 239, 244)
    lawngreen: Color = Color(124, 252, 0)
    lemonchiffon: Color = Color(255, 249, 204)
    lightblue: Color = Color(173, 216, 229)
    lightcoral: Color = Color(239, 127, 127)
    lightcyan: Color = Color(224, 255, 255)
    lightgoldenrodyellow: Color = Color(249, 249, 209)
    lightgreen: Color = Color(142, 237, 142)
    lightgrey: Color = Color(211, 211, 211)
    lightpink: Color = Color(255, 181, 193)
    lightsalmon: Color = Color(255, 160, 122)
    lightseagreen: Color = Color(33, 178, 170)
    lightskyblue: Color = Color(135, 206, 249)
    lightslategray: Color = Color(119, 135, 153)
    lightsteelblue: Color = Color(175, 196, 221)
    lightyellow: Color = Color(255, 255, 224)
    lime: Color = Color(0, 255, 0)
    limegreen: Color = Color(51, 204, 51)
    linen: Color = Color(249, 239, 229)

    magenta: Color = Color(255, 0, 255)
    maroon: Color = Color(127, 0, 0)
    mediumaquamarine: Color = Color(102, 204, 170)
    mediumblue: Color = Color(0, 0, 204)
    mediumorchid: Color = Color(186, 84, 211)
    mediumpurple: Color = Color(147, 112, 219)
    mediumseagreen: Color = Color(61, 178, 112)
    mediumslateblue: Color = Color(122, 104, 237)
    mediumspringgreen: Color = Color(0, 249, 153)
    mediumturquoise: Color = Color(71, 209, 204)
    mediumvioletred: Color = Color(198, 20, 132)
    midnightblue: Color = Color(25, 25, 112)
    mintcream: Color = Color(244, 255, 249)
    mistyrose: Color = Color(255, 226, 224)
    moccasin: Color = Color(255, 226, 181)

    navajowhite: Color = Color(255, 221, 173)
    navy: Color = Color(0, 0, 127)

    oldlace: Color = Color(252, 244, 229)
    olive: Color = Color(127, 127, 0)
    olivedrab: Color = Color(107, 142, 35)
    orange: Color = Color(255, 165, 0)
    orangered: Color = Color(255, 68, 0)
    orchid: Color = Color(216, 112, 214)

    palegoldenrod: Color = Color(237, 232, 170)
    palegreen: Color = Color(153, 249, 153)
    paleturquoise: Color = Color(175, 237, 237)
    palevioletred: Color = Color(219, 112, 147)
    papayawhip: Color = Color(255, 239, 214)
    peachpuff: Color = Color(255, 216, 186)
    peru: Color = Color(204, 132, 63)
    pink: Color = Color(255, 191, 204)
    plum: Color = Color(221, 160, 221)
    powderblue: Color = Color(175, 224, 229)
    purple: Color = Color(127, 0, 127)

    red: Color = Color(255, 0, 0)
    rosybrown: Color = Color(188, 142, 142)
    royalblue: Color = Color(63, 104, 224)

    saddlebrown: Color = Color(140, 68, 17)
    salmon: Color = Color(249, 127, 114)
    sandybrown: Color = Color(244, 163, 96)
    seagreen: Color = Color(45, 140, 86)
    seashell: Color = Color(255, 244, 237)
    sienna: Color = Color(160, 81, 45)
    silver: Color = Color(191, 191, 191)
    skyblue: Color = Color(135, 206, 234)
    slateblue: Color = Color(107, 89, 204)
    slategray: Color = Color(112, 127, 142)
    snow: Color = Color(255, 249, 249)
    springgreen: Color = Color(0, 255, 127)
    steelblue: Color = Color(68, 130, 181)

    tan: Color = Color(209, 181, 140)
    teal: Color = Color(0, 127, 127)
    thistle: Color = Color(216, 191, 216)
    tomato: Color = Color(255, 99, 71)
    transparent: Color = Color(0, 0, 0, 0)
    turquoise: Color = Color(63, 224, 209)

    violet: Color = Color(237, 130, 237)
    wheat: Color = Color(244, 221, 17)
    white: Color = Color(255, 255, 255)
    whitesmoke: Color = Color(244, 244, 244)
    yellow: Color = Color(255, 255, 0)
    yellowgreen: Color = Color(153, 204, 51)
