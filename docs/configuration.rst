Configuration
=============

This section describes how to configure the interop server. Additional steps
for deployment can be found in `Django's Deployment Docs
<https://docs.djangoproject.com/en/1.8/howto/deployment/>`__.


**Create a New Admin**. The automated system setup will create a default
administrator account with username ``testadmin`` and password ``testpass``.
This account can be used to login to the admin interfaces or authenticate any
requests. If you would like to create another administrator account, the
Django management program can be used to create an administrator account.
Execute the following from a bash shell inside the server's container.

.. code-block:: bash

    cd /interop/server
    python manage.py createsuperuser



Object Configuration
--------------------

The following describes the individual model objects in greater
detail than what is presented in :doc:`getting_started`.

.. autoclass:: auvsi_suas.models.GpsPosition
.. autoclass:: auvsi_suas.models.AerialPosition
.. autoclass:: auvsi_suas.models.UasTelemetry
.. autoclass:: auvsi_suas.models.Target
.. autoclass:: auvsi_suas.models.Waypoint
.. autoclass:: auvsi_suas.models.StationaryObstacle
.. autoclass:: auvsi_suas.models.MovingObstacle
.. autoclass:: auvsi_suas.models.FlyZone
.. autoclass:: auvsi_suas.models.MissionConfig
.. autoclass:: auvsi_suas.models.MissionClockEvent
.. autoclass:: auvsi_suas.models.TakeoffOrLandingEvent
