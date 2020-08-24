import json

from urllib.parse import urlparse

import pytest

from data import model, database
from data.secscan_model.secscan_v4_model import V4SecurityScanner
from data.registry_model import registry_model
from workers.securityscanningnotificationworker import SecurityScanningNotificationWorker
from util.secscan.v4.fake import fake_security_scanner
from test.fixtures import *

from app import app, secscan_notification_queue, notification_queue


@pytest.mark.parametrize(
    "issue", [None, "wrong_id", "no_event_registered", "severity_too_low", "no_matching_manifest"]
)
def test_notification(issue, initialized_db):
    worker = SecurityScanningNotificationWorker(secscan_notification_queue)

    hostname = urlparse(app.config["SECURITY_SCANNER_V4_ENDPOINT"]).netloc
    with fake_security_scanner(hostname=hostname) as fake:
        repository_ref = registry_model.lookup_repository("devtable", "simple")

        # Add a security notification event to the repository.
        if issue != "no_event_registered":
            model.notification.create_repo_notification(
                repository_ref.id,
                "vulnerability_found",
                "webhook",
                {},
                {
                    "vulnerability": {
                        "priority": "Low" if issue != "severity_too_low" else "Critical",
                    },
                },
            )

        tag = registry_model.get_repo_tag(repository_ref, "latest")
        manifest = registry_model.get_manifest_for_tag(tag)

        # Add a notification to the scanner, matching the manifest.
        notification_id = "somenotificationid"
        fake.add_notification(
            notification_id if issue != "wrong_id" else "wrongid",
            manifest.digest if issue != "no_matching_manifest" else "sha256:incorrect",
            "added",
            {
                "Severity": "High",
                "Description": "Some description",
                "Package": "FooBar",
                "Name": "BarBaz",
                "Link": "http://example.com",
            },
        )

        # Add the notification to the queue.
        name = ["with_id", notification_id]
        secscan_notification_queue.put(
            name, json.dumps({"notification_id": notification_id}),
        )

        # Process the notification via the worker.
        worker.poll_queue()

        # Ensure the repository notification was enqueued.
        found = notification_queue.get()
        if issue:
            assert found is None
            return
        assert found is not None

        body = json.loads(found["body"])
        assert body["event_data"]["repository"] == "devtable/simple"
        assert body["event_data"]["namespace"] == "devtable"
        assert body["event_data"]["name"] == "simple"
        assert body["event_data"]["tags"] == ["latest"]
        assert body["event_data"]["vulnerability"]["id"] == "BarBaz"
        assert body["event_data"]["vulnerability"]["description"] == "Some description"
        assert body["event_data"]["vulnerability"]["priority"] == "High"
