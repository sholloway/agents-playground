import itertools
from typing import Callable, Generic, List, Optional
from types import FunctionType
from agents_playground.core.callable_utils import CallableUtility

from agents_playground.core.priority_queue import (
    PriorityItem,
    PriorityItemDecorator,
    PriorityQueue,
)
from agents_playground.core.time_utilities import TimeInMS, TimeUtilities

"""
Domain Concepts
- Emitter: Raises and can handle events
- Dispatcher: Passes events to all relevant listeners.
- Scheduler: Notifies entities to update at a particular time.
  What are examples of schedulers IRL?
  Train Conductor, OS Schedulers
- Schedulable? Something that can be scheduled?

OS Schedulers: https://en.wikipedia.org/wiki/Scheduling_(computing)
OSs have process schedulers. They may have up to three distinct scheduler types: 
  - a long-term scheduler (also known as an admission scheduler or high-level scheduler), 
  - a mid-term or medium-term scheduler,
  - a short-term scheduler.
The process scheduler will move items from one queue to the next based on frequency of 
when the item shall be scheduled. So a process scheduled far out may transition like:
Long Term Scheduler -> Mid Term Scheduler -> Short Term Scheduler

Considerations
- How to handle pausing?
  Current time probably needs an ADT so the current time can be slide around.
- What is game time vs real-time?
  Ultimately I'd like to play with concepts like the passage of time
  and things like weather. 1 minute in the game won't be 1 minute IRL.
- We want to avoid calling time.sleep() as much as possible.
- The ability to pause a sim and render a timing diagram (https://en.wikipedia.org/wiki/Earliest_deadline_first_scheduling#Timing_diagram)
  may be useful during debugging. 
- For each scheduled thing:
  - The amount of time the event will take.
  - When the event should occur. 

Godot locks the framerate using https://github.com/godotengine/godot/blob/master/main/main_timer_sync.h
There is no point trying to recreate full game engine capability. Rather, I just 
need to focus on the patterns and algorithms I'm trying to study.

60 FPS is the target in Godot and most AAA games. 
This is to align with the 144 Hz monitor refreshing.
60 FPS means each frame has a duration of ~16.6 ms or 0.01666666667 seconds.
"""


"""Rez's API

class DelayedCallbackManager:
  callbacks: List = []
  curr_time: float = 0.0

  def update(self, delta_ms: float) -> None:
    # Invokes the callable for everything that the time has come for.
    pass

  def add_callback(self, delayed_callback: Callable, delay_until_call_ms: float) -> int:
    pass

  def remove_callback(self, id: int) -> bool:
    pass

  def change_time(self, id: int, new_time: float) -> None:
    pass
"""


class DelayedCallback:
    id: int
    callback: Callable
    time_to_call: int


"""Possible Alternative"""

ScheduledJobId = int


class JobScheduler(Generic[PriorityItem]):
    """Schedules the execution of callbacks at specific times.

    Time is always specified in ms.
    """

    def __init__(self) -> None:
        self._jobs_queue: PriorityQueue = PriorityQueue()
        self._job_counter = itertools.count()

    def run_due_jobs(self, duration: TimeInMS):
        """Runs all jobs that are scheduled for the current time window.

        This is called once per frame. The delta is the amount of time the frame
        shall take. Runs anything older than current time + frame time

        Args:
          duration: How much time to consider when running jobs.
        """
        current_time_ms: TimeInMS = self._current_time()
        scheduled_time = current_time_ms + duration

        while len(self._jobs_queue) > 0 and self._jobs_queue.jobs_due(scheduled_time):
            run_time: float
            job: PriorityItem
            job_data: Optional[dict]
            run_time, job, job_data = self._jobs_queue.pop()
            CallableUtility.invoke(job, job_data)

    def _current_time(self) -> TimeInMS:
        return TimeUtilities.now()

    def schedule(
        self, job: Callable, scheduled_time: TimeInMS, job_data: Optional[dict] = None
    ) -> ScheduledJobId:
        """Schedules a job to run in the future.

        Args:
          job: A function to be invoked at a future time.
          scheduled_time: The time when the job will be ran expressed in milliseconds.

        Returns:
          A job ID that identifies the scheduled job.
        """
        job_id = self._generate_job_id()
        self._jobs_queue.push(job, job_id, scheduled_time, job_data)
        return job_id

    def cancel(self, job_id: ScheduledJobId):
        """Removes a job from the scheduler without executing it.

        Args:
          job_id: The ID of the job to be removed.
        """
        if job_id in self._jobs_queue:
            self._jobs_queue.remove(job_id)

    def reschedule(self, job_id: ScheduledJobId, new_scheduled_time: TimeInMS):
        """Updates the time to run a specific job.

        Args:
          job_id: The ID of the job to be rescheduled.
          new_scheduled_time: The new time to run the job.
        """
        if job_id in self:
            queued_item_bundle: Optional[PriorityItemDecorator] = (
                self._jobs_queue.index(job_id)
            )
            if queued_item_bundle is not None:
                self._jobs_queue.push(
                    queued_item_bundle.item, job_id, new_scheduled_time
                )

    def __contains__(self, job_id: ScheduledJobId) -> bool:
        return job_id in self._jobs_queue

    def scheduled(self, job_id: ScheduledJobId) -> TimeInMS:
        """Returns the time of the job is schedule.

        Raises:
          KeyError: Raises a key error if job does not exist.
        """
        if job_id in self:
            bundled_item: Optional[PriorityItemDecorator] = self._jobs_queue.index(
                job_id
            )
            return bundled_item.priority if bundled_item else -1
        else:
            raise KeyError(f"Job {job_id} not scheduled.")

    def _generate_job_id(self) -> ScheduledJobId:
        """Generates a unique ID for identifying a scheduled job."""
        return next(self._job_counter)
