"""
Module that runs in its own process and collects metrics about the running
simulation's hardware utilization. Communication between the processes is
done via a shared uni-directional pipe.
"""

from __future__ import annotations


import sys
import traceback
import threading
from multiprocessing import Event, Pipe, Process
from multiprocessing.connection import Connection

import os
from time import sleep
from typing import NamedTuple

from agents_playground.core.constants import BYTES_IN_MB, MONITOR_FREQUENCY, SAMPLES_WINDOW
from agents_playground.core.samples import SamplesWindow
from agents_playground.core.time_utilities import TimeUtilities
from agents_playground.core.types import TimeInSecs

from agents_playground.fp import Maybe, Nothing, Something
from agents_playground.sys.logger import get_default_logger, log_call

logger = get_default_logger()


class PerformanceMonitor:
    @log_call
    def __init__(self) -> None:
        self._process: Maybe[Process] = Nothing()
        self._stop = Event()

    @log_call
    def __del__(self):
        logger.info("PerformanceMonitor deleted.")

    @log_call
    def start(self, monitor_pid: int) -> Connection:
        """Starts the monitor process.

        Args
          - monitor_pid: The process ID of the process that will be monitored.

        Returns
          The output connection of the process.
        """
        pipe_receive, pipe_send = Pipe(duplex=False)

        self._process = Something(
            Process(
                target=monitor,
                name="child-process",
                args=(monitor_pid, pipe_send, self._stop),
                daemon=False,
            )
        )

        self._process.unwrap().start()
        return pipe_receive

    @log_call
    def stop(self) -> None:
        """Terminates the monitor process."""
        # Send the event to the sub process (if it exists) to stop.
        self._stop.set() 

        if self._process.is_something():
            try:
                # Close the child process.
                logger.info('Attempting to join the performance monitor process.')
                process = self._process.unwrap()
                process.join()
                if process.exitcode != 0:
                    logger.error(f"The exit code for the performance monitor process was {process.exitcode}. 0 expected.")
                logger.info('Attempting to close the child process.')
                process.close()
            except Exception as e:
                logger.error('An error occurred trying to shutdown the performance monitor.')
                logger.error(e)
        else:
            logger.info('The performance monitor process did not exist. Nothing to stop.')

def monitor(
    monitor_pid: int, 
    output_pipe: Connection, 
    stop: threading.Event #Note that at run time, multiprocessing.Event is what's passed.
) -> None:
    logger.info(f"Process Monitor started. {os.getpid()}")
    logger.info(f"Process Monitor process user: {os.getuid()}")
    logger.info(f"Monitoring as user: {os.getuid()}")
    
    import psutil

    simulation_start_time: TimeInSecs = TimeUtilities.now_sec()

    sim_running_time: TimeInSecs = 0
    cpu_utilization = SamplesWindow(SAMPLES_WINDOW, 0)
    non_swapped_physical_memory_used = SamplesWindow(SAMPLES_WINDOW, 0)
    virtual_memory_used = SamplesWindow(SAMPLES_WINDOW, 0)
    memory_unique_to_process = SamplesWindow(SAMPLES_WINDOW, 0)
    page_faults = SamplesWindow(SAMPLES_WINDOW, 0)
    pageins = SamplesWindow(SAMPLES_WINDOW, 0)

    ps = psutil.Process(monitor_pid)

    try:
        while not stop.is_set():
            # 1. How long has the simulation been running?
            sim_running_time = TimeUtilities.now_sec() - simulation_start_time

            # 2. How heavy is the CPU(s) being taxed?
            # The CPU utilization for 1 second.
            cpu_utilization.collect(ps.cpu_percent(interval=1))

            # 3. How much memory is being used?
            memory_info = ps.memory_full_info()

            # “Resident Set Size” is the non-swapped physical memory a process has used.
            # Convert Bytes into MB
            non_swapped_physical_memory_used.collect(memory_info.rss / BYTES_IN_MB)

            # Virtual Memory Size is the total amount of virtual memory used by the process.
            virtual_memory_used.collect(memory_info.vms / BYTES_IN_MB)

            # “Unique Set Size” is the memory which is unique to a process and which
            # would be freed if the process was terminated right now.
            # uss is probably the most representative metric for determining how much
            # memory is actually being used by a process. It represents the amount of
            # memory that would be freed if the process was terminated right now.
            memory_unique_to_process.collect(memory_info.uss / BYTES_IN_MB)

            # How is the sim retrieving memory?
            # Page Faults are requests for more memory.
            page_faults.collect(memory_info.pfaults)

            # The total number of requests for pages from a pager.
            # https://www.unix.com/man-page/osx/1/vm_stat
            # Manually view this on the CLI with vm_stat
            pageins.collect(memory_info.pageins)

            metrics = PerformanceMetrics(
                sim_running_time=sim_running_time,
                cpu_utilization=cpu_utilization,
                non_swapped_physical_memory_used=non_swapped_physical_memory_used,
                virtual_memory_used=virtual_memory_used,
                memory_unique_to_process=memory_unique_to_process,
                page_faults=page_faults,
                pageins=pageins,
            )

            # print('Performance Monitor Sending:')
            # print(metrics)
            output_pipe.send(metrics)

            sleep(MONITOR_FREQUENCY)
        else:
            logger.info("Asked to stop.")
    except BaseException as e:
        logger.error("The Performance Monitor threw an exception and stopped.")
        logger.error(e,exc_info=True)
        # traceback.print_exception(e)
        # sys.stdout.flush()


class PerformanceMetrics(NamedTuple):
    sim_running_time: TimeInSecs
    cpu_utilization: SamplesWindow
    non_swapped_physical_memory_used: SamplesWindow
    virtual_memory_used: SamplesWindow
    memory_unique_to_process: SamplesWindow
    page_faults: SamplesWindow
    pageins: SamplesWindow
