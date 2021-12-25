import pytest
from agents_playground.core.scheduler import JobScheduler
from agents_playground.core.time_utilities import MS_PER_SEC, TimeUtilities

"""
Test Plan
- [X] Test Generating IDs
- [X] Schedule Jobs
- [X] Cancel Jobs
- [ ] Reschedule Jobs
- [ ] Reoccurring Jobs
- [ ] Running Jobs
  - [ ] Need to test things at the 60 FPS frequency. 16.6 ms per Frame
"""


current_time = TimeUtilities.now()
IN_FIVE_SECS = current_time + MS_PER_SEC*5
IN_TEN_SECS = current_time + MS_PER_SEC*10
IN_TWENTY_SECS = current_time + MS_PER_SEC*10

class TestJobScheduler:
  def test_schedule_jobs(self):
    js = JobScheduler()
    fake_task = lambda: True

    job1 = js.schedule(fake_task, IN_FIVE_SECS)
    job2 = js.schedule(fake_task, IN_TEN_SECS)
    job3 = js.schedule(fake_task, IN_TWENTY_SECS)

    assert job1 in js and js.scheduled(job1) == IN_FIVE_SECS
    assert job2 in js and js.scheduled(job2) == IN_TEN_SECS
    assert job3 in js and js.scheduled(job3) == IN_TWENTY_SECS

  def test_cancelling_jobs(self):
    js = JobScheduler()
    fake_task = lambda: True

    job1 = js.schedule(fake_task, IN_FIVE_SECS)
    assert job1 in js and js.scheduled(job1) == IN_FIVE_SECS

    js.cancel(job1)
    assert job1 not in js 
    
    with pytest.raises(KeyError) as error:
      js.scheduled(job1)

    assert f'Job {job1} not scheduled.' in str(error.value)
