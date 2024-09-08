"""
This is a temporary test to help work through creating a frame graph/render graph based 
rendering pipeline. It'll probably need to be removed after that is established.
"""

from deprecated import deprecated  # type: ignore

def uniform(cls):
    class Uniform:
        x = 14 

        def __init__(self) -> None:
            self._internal_state = 42
        
        def has_changed(self) -> bool:
            return self._internal_state != 42
    return Uniform

@uniform
class Overlay:
    pass 

@deprecated(reason="This test class is just to help work through the complexities of working with compute shaders. It will be removed after building the render/compute graph system.")
class TestFrameGraph:
    def test_something(self) -> None:
        overlay = Overlay()
        assert overlay.x == 14
        assert isinstance(overlay, Overlay)
        assert overlay.has_changed() == False
        overlay._internal_state = 92
        assert overlay.has_changed() == True