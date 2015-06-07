/**
 * Service to interact with backend.
 */


/**
 * Service to interact with backend.
 * @param $resource The resource service.
 * @param $interval The interval service.
 */
Backend = function($resource, $interval) {
    /**
     * Missions backend interface.
     */
    this.Missions = $resource('/api/missions');

    /**
     * Teams backend interface.
     */
    this.Teams = $resource('/api/teams');

    /**
     * Obstacles backend interface.
     */
    this.Obstacles = $resource('/api/interop/obstacles', {log: false});

    /**
     * Telemetry backend interface.
     */
    this.Telemetry = $resource('/api/telemetry');

    /**
     * The missions. 
     */
    this.missions = null;

    /**
     * The teams.
     */
    this.teams = null;

    /**
     * The obstacles.
     */
    this.obstacles = null;

    /**
     * The telemetry.
     */
    this.telemetry = null;

    /**
     * The update which syncs with the backend periodically (1s).
     */
    this.update = $interval(angular.bind(this, this.update), 1000);
};


/**
 * Executes asynchronous updates with the backend.
 */
Backend.prototype.update = function() {
    // Execute all asynchronous background syncs.
    var missions = this.Missions.query({},
            angular.bind(this, this.setMissions, missions));
    var teams = this.Teams.query({},
            angular.bind(this, this.setTeams, teams));
    var obstacles = this.Obstacles.get({},
            angular.bind(this, this.setObstacles, obstacles));
    var telemetry = this.Telemetry.query({},
            angular.bind(this, this.setTelemetry, telemetry));
};


/**
 * Sets the missions.
 * @param missions The missions to set.
 */
Backend.prototype.setMissions = function(missions) {
    this.missions = missions;
};


/**
 * Sets the teams.
 * @param teams The teams to set.
 */
Backend.prototype.setTeams = function(teams) {
    this.teams = teams;
};


/**
 * Sets the obstacles.
 * @param obstacles The obstacles to set.
 */
Backend.prototype.setObstacles = function(obstacles) {
    this.obstacles = obstacles;
};


/**
 * Sets the telemetry.
 * @param telemetry The telemetry to set.
 */
Backend.prototype.setTelemetry = function(telemetry) {
    this.telemetry = telemetry;
};


// Register the service.
angular.module('auvsiSuasApp').service('Backend', [
    '$resource',
    '$interval',
    Backend
]);
