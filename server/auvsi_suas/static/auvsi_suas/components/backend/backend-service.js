/**
 * @fileoverview Service to interact with backend.
 * The data will be synced with the backend at a regular interval. You can
 * access the data via public fields of the service. When data is updated it
 * will broadcast an 'Backend.dataUpdated' event.
 */


/**
 * Service to interact with the backend.
 * @param {!angular.Scope} $rootScope The root scope service.
 * @param {!angular.Resource} $resource The resource service.
 * @param {!angular.$interval} $interval The interval service.
 * @final
 * @constructor
 * @struct
 * @ngInject
 */
Backend = function($rootScope, $resource, $interval) {
    /**
     * @export {?Object} The missions data.
     */
    this.missions = null;

    /**
     * @export {?Object} The teams data.
     */
    this.teams = null;

    /**
     * @export {?Object} The obstacles data.
     */
    this.obstacles = null;

    /**
     * @export {!Object} Map from user to telemetry data.
     */
    this.telemetry = {};

    /**
     * @export {?Array<Object>} The targets for review.
     */
    this.reviewTargets = null;

    /**
     * @private @const {!angular.Scope} The root scope service.
     */
    this.rootScope_ = $rootScope;

    /**
     * @private @const {!Object} Missions interface.
     */
    this.missionResource_ = $resource('/api/missions');

    /**
     * @private @const {!Object} Teams interface.
     */
    this.teamsResource_ = $resource('/api/teams');

    /**
     * @private @const {!Object} Obstacles interface.
     */
    this.obstaclesResource_ = $resource('/api/obstacles', {log: false});

    /**
     * @private @const {!Object} Telemetry interface.
     */
    this.telemetryResource_ = $resource('/api/telemetry');

    /**
     * @private @const {!Object} Target review interface.
     */
    this.targetReviewResource_ = $resource(
            '/api/targets/review/:id',
            {id: '@id'},
            {'update': {method: 'PUT'}});

    /**
     * @private @const {!Object} Real time data sync every 1s.
     */
    this.realTimeInterval_ = $interval(
            angular.bind(this, this.realTimeUpdate_), 1000);

    /**
     * @private @const {!Object} Batch data sync every 10s.
     */
    this.nonRealTimeInterval_ = $interval(
            angular.bind(this, this.nonRealTimeUpdate_), 10000);

    // Perform initial sync.
    this.realTimeUpdate_();
    this.nonRealTimeUpdate_();
};


/**
 * Executes asynchronous updates for real-time data.
 * @private
 */
Backend.prototype.realTimeUpdate_ = function() {
    this.teamsResource_.query({}).$promise
        .then(angular.bind(this, this.setTeams_))
        .then(angular.bind(this, this.updateTelemetry_));
    this.obstaclesResource_.get({}).$promise.then(
            angular.bind(this, this.setObstacles_));
};


/**
 * Executes asynchronous updates for non-real-time data.
 * @private
 */
Backend.prototype.nonRealTimeUpdate_ = function() {
    this.missionResource_.query({}).$promise.then(
            angular.bind(this, this.setMissions_));
    this.targetReviewResource_.query({}).$promise.then(
            angular.bind(this, this.setReviewTargets_));
};


/**
 * Notifies others of data change by broadcasting an event.
 * @private
 */
Backend.prototype.notifyDataUpdated_ = function() {
    this.rootScope_.$broadcast('Backend.dataUpdated');
};


/**
 * Sets the missions.
 * @param {!Object} missions The missions to set.
 * @private
 */
Backend.prototype.setMissions_ = function(missions) {
    this.missions = missions;
    this.notifyDataUpdated_();
};


/**
 * Sets the teams.
 * @param {!Object} teams The teams to set.
 * @private
 */
Backend.prototype.setTeams_ = function(teams) {
    this.teams = teams;
    this.notifyDataUpdated_();
};


/**
 * Sets the obstacles.
 * @param {!Object} obstacles The obstacles to set.
 * @private
 */
Backend.prototype.setObstacles_ = function(obstacles) {
    this.obstacles = obstacles;
    this.notifyDataUpdated_();
};


/**
 * Updates the telemetry for active teams.
 * @private
 */
Backend.prototype.updateTelemetry_ = function() {
    for (var i = 0; i < this.teams.length; i++) {
        if (this.teams[i].active) {
            var query = this.telemetryResource_.query({
                limit: 1,
                user: this.teams[i].id
            });
            query.$promise.then(angular.bind(this, this.setTelemetry_));
        }
    }
}


/**
 * Sets the telemetry.
 * @param {!Object} telemetry The telemetry to set.
 * @private
 */
Backend.prototype.setTelemetry_ = function(telemetry) {
    for (var i = 0; i < telemetry.length; i++) {
        this.telemetry[telemetry[i].user] = telemetry[i];
    }
    this.notifyDataUpdated_();
};


/**
 * Sets the review targets.
 * @param {!Array<Object>} reviewTargets The targets to set.
 * @private
 */
Backend.prototype.setReviewTargets_ = function(reviewTargets) {
    this.reviewTargets = reviewTargets;
    this.notifyDataUpdated_();
};


// Register the service.
angular.module('auvsiSuasApp').service('Backend', [
    '$rootScope',
    '$resource',
    '$interval',
    Backend
]);
