# External Interactions

This document describes external dependencies and prerequisites for this App to operate, including system requirements, API endpoints, interconnection or integrations to other applications or services, and similar topics.

## External System Integrations

* When using SSoT to build a custom job, be mindful that, depending on how you are retrieving information from a remote data source, you may need to access over specific ports.

## Prometheus Metrics

Nautobot SSoT will add Prometheus metrics for multiple pieces of data that might be of interest in your environment to the `/api/plugins/capacity-metrics/app-metrics` output if the [Nautobot Capacity Metrics](https://github.com/nautobot/nautobot-app-capacity-metrics) app is installed and configured. The following metrics are added:

The Nautobot SSoT app has the Nautobot Capacity Metrics app as a dependency, but it is up to the admin to enable it in the `nautobot_config.py` configuration.

### Registered Metrics

Below are the currently registered metrics for the Nautobot SSoT App:

| Metric Name                           | Type  | Labels         | Description                                                        |
| ------------------------------------- | ----- | -------------- | ------------------------------------------------------------------ |
| nautobot_ssot_duration_seconds        | Gauge | job, phase     | Duration in seconds of each phase of a Job's latest Sync           |
| nautobot_ssot_syncs                   | Gauge | sync_type      | Count of all Syncs, and of Syncs per Job Result status             |
| nautobot_ssot_sync_operations         | Gauge | job, operation | Number of objects for each operation in a Job's latest Sync        |
| nautobot_ssot_sync_memory_usage_bytes | Gauge | job, phase     | Final and peak bytes of each phase of a Job's latest profiled Sync |

### Sample Prometheus Metrics

```prometheus
# HELP nautobot_ssot_duration_seconds Nautobot SSoT Job Phase Duration in seconds
# TYPE nautobot_ssot_duration_seconds gauge
nautobot_ssot_duration_seconds{job="nautobot_ssot.jobs.examples.ExampleDataSource",phase="source_load_time"} 5.314937
nautobot_ssot_duration_seconds{job="nautobot_ssot.jobs.examples.ExampleDataSource",phase="target_load_time"} 28.241297
nautobot_ssot_duration_seconds{job="nautobot_ssot.jobs.examples.ExampleDataSource",phase="diff_time"} 1.405652
nautobot_ssot_duration_seconds{job="nautobot_ssot.jobs.examples.ExampleDataSource",phase="sync_time"} 21.921814
nautobot_ssot_duration_seconds{job="nautobot_ssot.jobs.examples.ExampleDataSource",phase="sync_duration"} 98.35103
# HELP nautobot_ssot_syncs Nautobot SSoT Sync Totals
# TYPE nautobot_ssot_syncs gauge
nautobot_ssot_syncs{sync_type="total_syncs"} 4.0
nautobot_ssot_syncs{sync_type="failure_syncs"} 1.0
nautobot_ssot_syncs{sync_type="pending_syncs"} 0.0
nautobot_ssot_syncs{sync_type="received_syncs"} 0.0
nautobot_ssot_syncs{sync_type="retry_syncs"} 0.0
nautobot_ssot_syncs{sync_type="revoked_syncs"} 0.0
nautobot_ssot_syncs{sync_type="started_syncs"} 0.0
nautobot_ssot_syncs{sync_type="success_syncs"} 3.0
# HELP nautobot_ssot_sync_operations Nautobot SSoT operations by Job
# TYPE nautobot_ssot_sync_operations gauge
nautobot_ssot_sync_operations{job="nautobot_ssot.jobs.examples.ExampleDataSource",operation="skip"} 0.0
nautobot_ssot_sync_operations{job="nautobot_ssot.jobs.examples.ExampleDataSource",operation="create"} 2.0
nautobot_ssot_sync_operations{job="nautobot_ssot.jobs.examples.ExampleDataSource",operation="delete"} 0.0
nautobot_ssot_sync_operations{job="nautobot_ssot.jobs.examples.ExampleDataSource",operation="update"} 0.0
nautobot_ssot_sync_operations{job="nautobot_ssot.jobs.examples.ExampleDataSource",operation="no-change"} 1731.0
# HELP nautobot_ssot_sync_memory_usage_bytes Nautobot SSoT Sync Memory Usage
# TYPE nautobot_ssot_sync_memory_usage_bytes gauge
nautobot_ssot_sync_memory_usage_bytes{job="nautobot_ssot.jobs.examples.ExampleDataSource",phase="source_load_memory_final"} 1.8874368e+07
nautobot_ssot_sync_memory_usage_bytes{job="nautobot_ssot.jobs.examples.ExampleDataSource",phase="source_load_memory_peak"} 2.2020096e+07
nautobot_ssot_sync_memory_usage_bytes{job="nautobot_ssot.jobs.examples.ExampleDataSource",phase="target_load_memory_final"} 3.145728e+07
nautobot_ssot_sync_memory_usage_bytes{job="nautobot_ssot.jobs.examples.ExampleDataSource",phase="target_load_memory_peak"} 3.6700160e+07
nautobot_ssot_sync_memory_usage_bytes{job="nautobot_ssot.jobs.examples.ExampleDataSource",phase="diff_memory_final"} 4.194304e+06
nautobot_ssot_sync_memory_usage_bytes{job="nautobot_ssot.jobs.examples.ExampleDataSource",phase="diff_memory_peak"} 8.388608e+06
nautobot_ssot_sync_memory_usage_bytes{job="nautobot_ssot.jobs.examples.ExampleDataSource",phase="sync_memory_final"} 2.097152e+06
nautobot_ssot_sync_memory_usage_bytes{job="nautobot_ssot.jobs.examples.ExampleDataSource",phase="sync_memory_peak"} 6.291456e+06
```
