/**
 * Service to interact with backend.
 * The data will be synced with the backend at a regular interval. You can
 * access the data via public fields of the service. When data is updated it
 * will broadcast an 'Backend.dataUpdated' event.
 */


/**
 * Service to interact with backend.
 * @param $resource The resource service.
 * @param $interval The interval service.
 * @param $rootScope The root scope service.
 */
Backend = function($resource, $interval, $rootScope) {
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
    this.updateInterval = $interval(angular.bind(this, this.update), 1000);

    /**
     * The root scope service.
     */
    this.rootScope_ = $rootScope;
};


/**
 * Executes asynchronous updates with the backend.
 */
Backend.prototype.update = function() {
    // Execute all asynchronous background syncs.
    this.Missions.query({}).$promise.then(
            angular.bind(this, this.setMissions));
    this.Teams.query({}).$promise.then(
            angular.bind(this, this.setTeams));
    this.Obstacles.get({}).$promise.then(
            angular.bind(this, this.setObstacles));
    this.Telemetry.query({limit: 1}).$promise.then(
            angular.bind(this, this.setTelemetry));
};


/**
 * Notifies others of data change by broadcasting an event.
 */
Backend.prototype.notifyDataUpdated_ = function() {
    this.rootScope_.$broadcast('Backend.dataUpdated');
};


/**
 * Sets the missions.
 * @param missions The missions to set.
 */
Backend.prototype.setMissions = function(missions) {
    this.missions = missions;
    this.notifyDataUpdated_();
};


/**
 * Sets the teams.
 * @param teams The teams to set.
 */
Backend.prototype.setTeams = function(teams) {
    this.teams = teams;
    this.notifyDataUpdated_();
};


/**
 * Sets the obstacles.
 * @param obstacles The obstacles to set.
 */
Backend.prototype.setObstacles = function(obstacles) {
    this.obstacles = obstacles;
    this.notifyDataUpdated_();
};


/**
 * Sets the telemetry.
 * @param telemetry The telemetry to set.
 */
Backend.prototype.setTelemetry = function(telemetry) {
    this.telemetry = telemetry;
    this.notifyDataUpdated_();
};


// Register the service.
angular.module('auvsiSuasApp').service('Backend', [
    '$resource',
    '$interval',
    '$rootScope',
    Backend
]);
