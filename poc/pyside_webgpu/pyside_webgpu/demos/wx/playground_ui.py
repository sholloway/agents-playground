"""
This module is a POC that mimics the functionality of the 
Agent Playground. Its intention is to flush out the differences
between DearPyGUI and wxPython. It is not functionally complete
and not intended to replace the UI of the Playground App. 
The idea is to flush out the wx way of building a UI.
"""

import wx 
import wx.aui as aui

"""
Thoughts
- Potentially leverage aui.AuiMDIParentFrame and aui.AuiMDIChildFrame classes
  to provide the nested simulation look. 
"""

is_client_window = lambda i: isinstance(i, aui.AuiMDIClientWindow)
is_child_frame = lambda i: isinstance(i, ChildFrame)

class PlaygroundWindow(aui.AuiMDIParentFrame):
  def __init__(self):
    super().__init__(None, 
      title="Agent Playground wxPython POC", 
      pos = wx.DefaultPosition, 
      size = (800, 800)
    )
    self._build_menu_bar()
    self.CreateStatusBar()
    self.Bind(wx.EVT_CLOSE, self._handle_close_window)

  def _build_menu_bar(self):
    menu_bar = wx.MenuBar()
    sim_menu = wx.Menu()

    # Setup the Open Sim menu item.
    open_sim = sim_menu.Append(-1, 'Open')
    self.Bind(wx.EVT_MENU, self._open_sim, open_sim)
    
    # Setup the New Sim menu item.
    new_sim = sim_menu.Append(-1, 'New')
    self.Bind(wx.EVT_MENU, self._new_sim, new_sim)

    menu_bar.Append(sim_menu, 'Simulations')
    self.SetMenuBar(menu_bar)

  def _open_sim(self, event: wx.Event):
    ChildFrame(self, 1)
    event.Skip()
  
  def _new_sim(self, event: wx.Event):
    event.Skip()

  def _handle_close_window(self, event: wx.Event):
    for frame in filter(is_client_window, self.GetChildren()):
      for child_frame in filter(is_child_frame, frame.GetChildren()):
        child_frame.Close()
    event.Skip()

class ChildFrame(aui.AuiMDIChildFrame):
  def __init__(self, parent, count):
    aui.AuiMDIChildFrame.__init__(
      self, 
      parent, 
      -1,
      title="Child: %d" % count
    )
    
    p = wx.Panel(self)
    wx.StaticText(p, -1, "This is child %d" % count, (10,10))
    p.SetBackgroundColour('light blue')

    sizer = wx.BoxSizer()
    sizer.Add(p, 1, wx.EXPAND)
    self.SetSizer(sizer)

    wx.CallAfter(self.Layout)

def main():
  app = wx.App()
  playground = PlaygroundWindow()
  playground.Show(show = True)
  app.MainLoop()

if __name__ == '__main__':
  main()