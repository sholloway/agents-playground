# Need to move this out of here. It was just a file to explore looping patterns.

from agents_playground.core.time_utilities import (
  TimeUtilities, 
  TimeInMS, 
  UPDATE_BUDGET
)

# https://gameprogrammingpatterns.com/game-loop.html
"""
 The difference between an “engine” and a “library”: 
 With libraries, you own the main game loop and call into the library. 
 An engine owns the loop and calls into your code.
"""

def da_stupid_loop():
  while True:
    process_input()
    run_ai()
    run_physics()
    render()


"""Fixed Time Step
The sleep() here makes sure the game doesn’t run too fast if it processes a 
frame quickly. It doesn’t help if your game runs too slowly. If it takes longer 
than 16ms to update and render the frame, your sleep time goes negative.
"""
def da_fixed_time_step():
  while True:
    start = get_current_time();
    process_input()
    run_ai()
    run_physics()
    render()
    sleep(start + MS_PER_FRAME - get_current_time())

"""Variable/Fluid Time Step
Each frame, we determine how much real time passed since the last 
game update (elapsed). When we update the game state, we pass that in. 
The engine is then responsible for advancing the game world forward by that 
amount of time.

Say you’ve got a bullet shooting across the screen. With a fixed time step, in 
each frame, you’ll move it according to its velocity. With a variable time step, 
you scale that velocity by the elapsed time. As the time step gets bigger, the 
bullet moves farther in each frame. That bullet will get across the screen in 
the same amount of real time whether it’s twenty small fast steps or four big 
slow ones. 

Issues with This:
- The game non-deterministic and unstable
"""
def da_variable_time_step_loop():
  last_time = get_current_time()
  while True:
    current = get_current_time()
    time_elapsed = current - last_time
    process_input()
    run_ai(time_elapsed)
    run_physics(time_elapsed)
    render()
    lastTime = current;

"""Hybrid: Fixed Time Step for Updates, Fluid Step for Rendering
One part of the engine that usually isn’t affected by a variable time step 
is rendering. Since the rendering engine captures an instant in time, it doesn’t 
care how much time advanced since the last one. It renders things wherever they 
happen to be right then.

We can use this fact to our advantage. We’ll update the game using a fixed time 
step because that makes everything simpler and more stable for physics and AI. 
But we’ll allow flexibility in when we render in order to free up some 
processor time.

It goes like this: A certain amount of real time has elapsed since the last turn 
of the game loop. This is how much game time we need to simulate for the game’s 
“now” to catch up with the player’s. We do that using a series of fixed time steps.

Note that the time step here isn’t the visible frame rate anymore.
MS_PER_UPDATE is just the granularity we use to update the game. The shorter 
this step is, the more processing time it takes to catch up to real time. 
The longer it is, the choppier the gameplay is. Ideally, you want it pretty 
short, often faster than 60 FPS, so that the game simulates with high fidelity 
on fast machines.

But be careful not to make it too short. You need to make sure the time step is 
greater than the time it takes to process an update(), even on the slowest 
hardware. Otherwise, your game simply can’t catch up.

I left it out here, but you can safeguard this by having the inner update loop 
bail after a maximum number of iterations. The game will slow down then, but 
that’s better than locking up completely.

Fortunately, we’ve bought ourselves some breathing room here. The trick is that 
we’ve yanked rendering out of the update loop. That frees up a bunch of CPU time. 
The end result is the game simulates at a constant rate using safe fixed time 
steps across a range of hardware. It’s just that the player’s visible window 
into the game gets choppier on a slower machine.
"""
def da_hybrid():
  previous = get_current_time()
  lag = 0.0
  while True:
    current = get_current_time()
    elapsed = current - previous
    previous = current
    lag += elapsed
    process_input()
    while (lag >= MS_PER_UPDATE):
      update() #AI, Physics, Whatever...
      lag -= MS_PER_UPDATE
    render()


"""My Approach
Leverage the hybrid approach with the event schedule
This needs to probably live in Simulation, however, having it be delegated 
as a public method will probably make testing cleaner.
The event_loop method might need to be a thread's callback. Or perhaps have 
EventLoop extend the Thread class.

EventBasedSimulation -> Simulation
"""

class EventLoop:
  def event_loop(self) -> None:
    previous_time: TimeInMS = TimeUtilities.now()
    lag: TimeInMS = 0
    while True: #Change to Simulation State
      current_time: TimeInMS = TimeUtilities.now()
      elapsed_time: TimeInMS = current_time - previous_time
      previous_time = current_time
      lag += elapsed_time
      # process_input()
      while lag >= UPDATE_BUDGET:
        # do the update
        lag -= UPDATE_BUDGET
      #render()


