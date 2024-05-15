import wx
import wgpu
import wgpu.backends.wgpu_native
from wgpu.gui.wx import WgpuWidget

from agents_playground.core.observe import Observable


class WebGPULandscapeEditor(Observable):
    def __init__(
        self,
        parent: wx.Window,
        canvas: WgpuWidget,
        landscape_path: str,
    ) -> None:
        super().__init__()
        self._parent_window = parent
        self._canvas = canvas
        self._landscape_path = landscape_path

    def update(self, msg: str) -> None:
        """Receives a notification message from an observable object."""
        # This is a holder over from the DearPyGUI based design. Skipping for the moment.
        pass

    def bind_event_listeners(self, frame: wx.Panel) -> None:
        """
        Given a panel, binds event listeners.
        """
        pass  # No event listens for the moment...

    def launch(self) -> None:
        """
        Starts the simulation running.
        """
        print("Boga Boga")

        """
    How should this work? Considerations:
    - I need a HalfEdgeMesh to store the active lattice.
    - Every time there is an edit, I need to produce:
      - A triangle mesh
      - Face Normals
      - Vertex Normals
      - VBO
      - VBI
      This will need to be additive/subtractive...
      The two meshes will need to be kept in sync.
      This will need to be optimized.

    GPU Pipelines
    - Infinite Grid
    - Heads Up Display for any text that needs to be overlaid. (e.g. RPS)
    - Axis Widget (display a 3D axis in a corner to help with orientation.)
    - Landscape Mesh
    - Active tile/face to add/subtract to.
    """
