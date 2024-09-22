import pytest
from pytest_mock import MockFixture
from agents_playground.core.scheduler import JobScheduler
from agents_playground.core.time_utilities import MS_PER_SEC, TimeUtilities

current_time = TimeUtilities.process_time_now()
IN_ONE_SECS = current_time + MS_PER_SEC
IN_FIVE_SECS = current_time + MS_PER_SEC * 5
IN_TEN_SECS = current_time + MS_PER_SEC * 10
IN_TWENTY_SECS = current_time + MS_PER_SEC * 10


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

        assert f"Job {job1} not scheduled." in str(error.value)

    def test_reschedule_jobs(self):
        js = JobScheduler()
        fake_task = lambda: True

        job1 = js.schedule(fake_task, IN_FIVE_SECS)
        job2 = js.schedule(fake_task, IN_TEN_SECS)
        job3 = js.schedule(fake_task, IN_TWENTY_SECS)

        js.reschedule(job2, IN_TWENTY_SECS)
        assert job2 in js and js.scheduled(job2) == IN_TWENTY_SECS

    def test_running_jobs(self, mocker: MockFixture):
        js = JobScheduler()
        js._current_time = mocker.MagicMock(return_value=current_time)
        job1 = mocker.MagicMock()
        job2 = mocker.MagicMock()
        job3 = mocker.MagicMock()

        js.schedule(job1, IN_ONE_SECS)
        js.schedule(job2, IN_FIVE_SECS)
        last_job_id = js.schedule(job3, IN_TEN_SECS)

        # Run everything scheduled for the next 5 seconds and older
        js.run_due_jobs(MS_PER_SEC * 5)

        assert job1.call_count == 1
        assert job2.call_count == 1
        job3.assert_not_called()
        assert last_job_id in js
        assert js.scheduled(last_job_id) == IN_TEN_SECS
