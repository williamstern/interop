from django.contrib import admin
from auvsi_suas.models import AerialPosition
from auvsi_suas.models import FlyZone
from auvsi_suas.models import GpsPosition
from auvsi_suas.models import MissionConfig
from auvsi_suas.models import MovingObstacle
from auvsi_suas.models import ObstacleAccessLog
from auvsi_suas.models import ServerInfo
from auvsi_suas.models import ServerInfoAccessLog
from auvsi_suas.models import StationaryObstacle
from auvsi_suas.models import TakeoffOrLandingEvent
from auvsi_suas.models import Target
from auvsi_suas.models import UasTelemetry
from auvsi_suas.models import Waypoint


# Define model admin which has better defaults for large amounts of data.
class LargeDataModelAdmin(admin.ModelAdmin):
    show_full_result_count = False

# Register models for admin page

# Only display raw ID fields for ForeignKeys which may contain large amounts
# of data.


@admin.register(AerialPosition)
class AerialPositionModelAdmin(LargeDataModelAdmin):
    raw_id_fields = ("gps_position", )


@admin.register(MissionConfig)
class MissionConfigModelAdmin(admin.ModelAdmin):
    raw_id_fields = ("home_pos", "emergent_last_known_pos",
                     "off_axis_target_pos", "sric_pos",
                     "ir_primary_target_pos", "ir_secondary_target_pos",
                     "air_drop_pos")


@admin.register(StationaryObstacle)
class StationaryObstacleModelAdmin(LargeDataModelAdmin):
    raw_id_fields = ("gps_position", )


@admin.register(Target)
class TargetModelAdmin(LargeDataModelAdmin):
    raw_id_fields = ("location", )


@admin.register(UasTelemetry)
class UasTelemetryModelAdmin(LargeDataModelAdmin):
    raw_id_fields = ("uas_position", )


@admin.register(Waypoint)
class WaypointModelAdmin(LargeDataModelAdmin):
    raw_id_fields = ("position", )

# These don't require any raw fields.
admin.site.register(FlyZone)
admin.site.register(GpsPosition, LargeDataModelAdmin)
admin.site.register(MovingObstacle)
admin.site.register(ObstacleAccessLog, LargeDataModelAdmin)
admin.site.register(ServerInfo)
admin.site.register(ServerInfoAccessLog, LargeDataModelAdmin)
admin.site.register(TakeoffOrLandingEvent)
