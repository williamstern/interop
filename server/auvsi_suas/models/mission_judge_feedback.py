"""Feedback from judges on mission performance."""

from mission_config import MissionConfig
from django.conf import settings
from django.db import models


class MissionJudgeFeedback(models.Model):
    """Stores feedback from judges on a team's mission performance.

    Attributes:
        mission: The mission for which this is feedback.
        user: The user for which this is feedback.
        flight_time: Time spent occupying runway and airspace.
        post_process_time: Time spent handling data on mission clock.
        used_timeout: Whether the team used their single timeout.
        safety_pilot_takeovers: The number of times the pilot took over.
        manual_flight_time: Time spent in manual flight by safety pilot.
        waypoints_captured: Number of waypoints that were captured.
        out_of_bounds: Number of times the UAS went out of bounds.
        unsafe_out_of_bounds: Number of times out of bounds compromised safety.
        air_delivery_accuracy_ft: Accuracy of delivery in feet.
        operational_excellence_percent: Grade of team performance [0, 100].

    """
    mission = models.ForeignKey(MissionConfig)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    flight_time = models.DurationField()
    post_process_time = models.DurationField()
    used_timeout = models.BooleanField()

    safety_pilot_takeovers = models.IntegerField()
    manual_flight_time = models.DurationField()
    waypoints_captured = models.IntegerField()
    out_of_bounds = models.IntegerField()
    unsafe_out_of_bounds = models.IntegerField()

    air_delivery_accuracy_ft = models.FloatField()

    operational_excellence_percent = models.FloatField()

    class Meta:
        unique_together = (('mission', 'user'), )
