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

class PlaygroundWindow(aui.AuiMDIParentFrame):
  def __init__(self):
    super().__init__(None, 
      title="Agent Playground wxPython POC", 
      pos = wx.DefaultPosition, 
      size = (800, 800)
    )

def main():
  app = wx.App()
  playground = PlaygroundWindow()
  playground.Show(show = True)
  app.MainLoop()

if __name__ == '__main__':
  main()