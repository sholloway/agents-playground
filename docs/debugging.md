Debugging

---

I use [pudb](https://github.com/inducer/pudb) for interactive debugging. This is a cheat sheet.

- [FAQ](#faq)
  - [How to set a breakpoint?](#how-to-set-a-breakpoint)
  - [How to set the theme?](#how-to-set-the-theme)
- [Interactive Commands](#interactive-commands)
  - [Moving Around](#moving-around)
  - [Navigation](#navigation)
  - [Inspection](#inspection)
  - [Breakpoints](#breakpoints)
  - [Misc](#misc)

## FAQ

### How to set a breakpoint?

In the code just add a line:

```python
breakpoint()
```

### How to set the theme?

You can change the theme of the debugger in ~/.config/pudb.
I prefer theme _monokai_. The default is classic.
The list of available [themes](https://github.com/inducer/pudb/blob/main/pudb/theme.py).

## Interactive Commands

### Moving Around

You can move around the various panes using VIM commands or the arrow keys.
h,j,k,l,gg,G,C-u,C-d

### Navigation

- _n(ext)_: Execute the current line of code. Goes to the next line.
- _s(tep)_: Steps into a function call.
- _c(ontinue)_: continues to the next breakpoint.
- _t_: Runs to cursor.
- _r/f(eturn)_: Finishes the current function.
- _j(ump) <line number>_: Jumps to a line number. Useful for breaking out of loops.
- _until <condition>_: Continues until a condition is met. Useful for loops.

### Inspection

- _a(rgs)_: displays the args that were passed into the current function.
- _u_: Up a level in a stack trace.
- _d_: Down a level in a stack trace.
- _p(rint)_: Prints a variable/expression.
- _pp_: Pretty prints a variable/expression.
- _l(ist)_ or _ll_: Lists the code around the current line.
- _w(here)_: Prints the current position and stack trace.

### Breakpoints

- _b(reak)_: Toggles a breakpoint.
- _b <line number>_: Sets a breakpoint on that line number.

### Misc

- _?_: display the help.
- _q(uit)_: Exits pudb.
