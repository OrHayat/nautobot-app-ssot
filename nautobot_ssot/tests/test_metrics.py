"""Tests for the framework-level Prometheus metric generators."""

import datetime
from unittest.mock import patch

from django.utils import timezone
from nautobot.apps.testing import TestCase
from nautobot.extras.choices import JobResultStatusChoices
from nautobot.extras.models import JobResult

from nautobot_ssot.jobs.examples import ExampleDataSource
from nautobot_ssot.metrics import (
    metric_memory_usage,
    metric_ssot_jobs,
    metric_sync_operations,
    metric_syncs,
)
from nautobot_ssot.models import Sync
from nautobot_ssot.tests.utils.job_helpers import get_test_job_model


class TestSSoTMetrics(TestCase):
    """Exercise the SSoT metric generators against a fully populated Sync."""

    def setUp(self):
        """Create an SSoT Job model and a Sync with every timing/memory field populated."""
        self.job_model = get_test_job_model(ExampleDataSource)
        self.job_result = JobResult.objects.create(
            name="ExampleDataSource",
            job_model=self.job_model,
            task_name="nautobot_ssot.jobs.examples.ExampleDataSource",
            worker="default",
        )
        self.job_result.set_status(JobResultStatusChoices.STATUS_SUCCESS)
        if not self.job_result.date_done:
            self.job_result.date_done = timezone.now()
        self.job_result.save()
        self.sync = Sync.objects.create(
            source="Example Data Source",
            target="Nautobot",
            start_time=timezone.now() - datetime.timedelta(seconds=5),
            dry_run=False,
            diff={},
            summary={"create": 1, "update": 2, "delete": 0},
            job_result=self.job_result,
            source_load_time=datetime.timedelta(seconds=1),
            target_load_time=datetime.timedelta(seconds=2),
            diff_time=datetime.timedelta(seconds=1),
            sync_time=datetime.timedelta(seconds=3),
            source_load_memory_final=1024,
            source_load_memory_peak=2048,
        )

    def test_metric_ssot_jobs_emits_each_phase(self):
        """metric_ssot_jobs emits a gauge sample for every populated timing field."""
        families = list(metric_ssot_jobs())
        self.assertEqual(len(families), 1)
        phases = {sample.labels["phase"] for sample in families[0].samples}
        self.assertEqual(
            phases,
            {"source_load_time", "target_load_time", "diff_time", "sync_time", "sync_duration"},
        )

    def test_metric_syncs_counts_totals(self):
        """metric_syncs emits a total-syncs sample plus one per JobResult status."""
        families = list(metric_syncs())
        self.assertEqual(len(families), 1)
        sync_types = {sample.labels["sync_type"] for sample in families[0].samples}
        self.assertIn("total_syncs", sync_types)

    def test_metric_sync_operations_emits_summary(self):
        """metric_sync_operations emits a sample per diff-summary operation."""
        families = list(metric_sync_operations())
        operations = {sample.labels["operation"] for sample in families[0].samples}
        self.assertIn("create", operations)
        self.assertIn("update", operations)

    @patch("nautobot_ssot.metrics.get_data_jobs", return_value=([], []))
    def test_metric_sync_operations_no_data_jobs(self, _mock_get_data_jobs):
        """When no data jobs exist, a single empty placeholder sample is emitted."""
        families = list(metric_sync_operations())
        samples = list(families[0].samples)
        self.assertTrue(any(sample.labels.get("job") == "" for sample in samples))

    def test_metric_memory_usage_emits_samples(self):
        """metric_memory_usage emits a sample per summary entry for memory-profiled syncs."""
        families = list(metric_memory_usage())
        self.assertEqual(len(families), 1)
        self.assertTrue(list(families[0].samples))


def _samples(family):
    """Map each sample's label values to its value, for exact assertions."""
    return {tuple(sample.labels.values()): sample.value for sample in family.samples}


class TestSSoTMetricValues(TestCase):
    """Assert the values the metric generators report, not just which labels exist."""

    def setUp(self):
        """Create one successful and one failed Sync with known timings and memory usage."""
        self.job_model = get_test_job_model(ExampleDataSource)
        self.job_label = ".".join(self.job_model.natural_key())
        start = timezone.now() - datetime.timedelta(minutes=5)
        self.failed_sync = self._create_sync(JobResultStatusChoices.STATUS_FAILURE, start)
        self.sync = self._create_sync(
            JobResultStatusChoices.STATUS_SUCCESS,
            start + datetime.timedelta(minutes=1),
            source_load_time=datetime.timedelta(seconds=1),
            target_load_time=datetime.timedelta(days=1),
            diff_time=datetime.timedelta(seconds=2, microseconds=500000),
            sync_time=datetime.timedelta(seconds=3),
            source_load_memory_final=1024,
            source_load_memory_peak=2048,
        )

    def _create_sync(self, status, start_time, **fields):
        """Create a Sync whose JobResult has the given status and finished 10s after start_time."""
        job_result = JobResult.objects.create(
            name="ExampleDataSource",
            job_model=self.job_model,
            task_name="nautobot_ssot.jobs.examples.ExampleDataSource",
            worker="default",
        )
        job_result.set_status(status)
        job_result.date_done = start_time + datetime.timedelta(seconds=10)
        job_result.save()
        return Sync.objects.create(
            source="Example Data Source",
            target="Nautobot",
            start_time=start_time,
            dry_run=False,
            diff={},
            summary={"create": 1, "update": 2, "delete": 0},
            job_result=job_result,
            **fields,
        )

    def test_sync_total_counts_successful_syncs(self):
        """success_syncs counts the Sync whose JobResult is SUCCESS."""
        samples = _samples(next(metric_syncs()))
        self.assertEqual(samples[("total_syncs",)], 2)
        self.assertEqual(samples[("success_syncs",)], 1, f"all samples: {samples}")

    def test_sync_total_counts_failed_syncs(self):
        """failure_syncs counts the Sync whose JobResult is FAILURE."""
        samples = _samples(next(metric_syncs()))
        self.assertEqual(samples[("failure_syncs",)], 1, f"all samples: {samples}")

    def test_duration_seconds_reports_seconds(self):
        """A 3 second sync phase is reported as 3.0, matching the metric's name and help text."""
        samples = _samples(next(metric_ssot_jobs()))
        self.assertEqual(samples[("sync_time", self.job_label)], 3.0)

    def test_duration_seconds_keeps_microseconds(self):
        """A 2.5 second diff phase is reported as 2.5."""
        samples = _samples(next(metric_ssot_jobs()))
        self.assertEqual(samples[("diff_time", self.job_label)], 2.5)

    def test_duration_seconds_source_load_time_matches_other_phases(self):
        """A 1 second source load is reported on the same scale as every other phase."""
        samples = _samples(next(metric_ssot_jobs()))
        self.assertEqual(samples[("source_load_time", self.job_label)], 1.0)

    def test_duration_seconds_includes_days(self):
        """A 1 day target load is not reported as zero."""
        samples = _samples(next(metric_ssot_jobs()))
        self.assertEqual(samples[("target_load_time", self.job_label)], 86400.0)

    def test_memory_usage_reports_recorded_bytes(self):
        """The memory gauge reports the profiled byte counts, not the diff summary."""
        samples = _samples(next(metric_memory_usage()))
        self.assertTrue({1024, 2048} <= set(samples.values()), f"all samples: {samples}")
