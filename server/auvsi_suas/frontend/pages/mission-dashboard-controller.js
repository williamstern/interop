/**
 * Controller for the Mission Dashboard page.
 */


/**
 * Controller for the Mission Dashboard page.
 * @param {!angular.Scope} $rootScope The root scope to listen for events.
 * @param {!angular.$routeParams} $routeParams The route parameter service.
 * @param {!angular.$interval} $interval The interval service.
 * @param {!Object} Backend The backend service.
 * @final
 * @constructor
 * @struct
 * @ngInject
 */
MissionDashboardCtrl = function($rootScope, $routeParams, $interval, Backend) {
    /**
     * @export {?Object} The teams data.
     */
    this.teams = null;

    /**
     * @private @const {!angular.$routeParams} The route params service.
     */
    this.routeParams_ = $routeParams;

    /**
     * @private @const {!Object} The backend service.
     */
    this.backend_ = Backend;

    /**
     * @private @const {!Object} Data sync every 1s.
     */
    this.updateInterval_ = $interval(
            angular.bind(this, this.update_), 1000);
};

/**
 * Executes asynchronous updates for data.
 * @private
 */
MissionDashboardCtrl.prototype.update_ = function() {
    this.backend_.teamsResource.query({}).$promise
        .then(angular.bind(this, this.setTeams_));
};


/**
 * Sets the teams.
 * @param {Array<Object>} teams The teams to set.
 * @private
 */
MissionDashboardCtrl.prototype.setTeams_ = function(teams) {
    this.teams = teams;
};


// Register controller with app.
angular.module('auvsiSuasApp').controller('MissionDashboardCtrl', [
    '$rootScope',
    '$routeParams',
    '$interval',
    'Backend',
    MissionDashboardCtrl
]);
