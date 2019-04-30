/**
 * Controller for the Mission Dashboard page.
 */


/**
 * Controller for the Mission Dashboard page.
 * @param {!angular.$routeParams} $routeParams The route parameter service.
 * @param {!angular.$interval} $interval The interval service.
 * @param {!angular.Scope} $scope The scope of the controller to listen for events.
 * @param {!Object} Backend The backend service.
 * @final
 * @constructor
 * @struct
 * @ngInject
 */
MissionDashboardCtrl = function($routeParams, $interval, $scope, Backend) {
    /**
     * @export {?Object} The teams data.
     */
    this.teams = null;

    /**
     * @private @const {!angular.$routeParams} The route params service.
     */
    this.routeParams_ = $routeParams;

    /**
     * @private {!angular.$interval} $interval The interval service.
     */
    this.interval_ = $interval;

    /**
     * @private @const {!Object} The backend service.
     */
    this.backend_ = Backend;

    /**
     * @private @const {!Object} Data sync every 1s.
     */
    this.updateInterval_ = this.interval_(
            angular.bind(this, this.update_), 1000);
    $scope.$on("$destroy", angular.bind(this, function() {
        this.interval_.cancel(this.updateInterval_);
        this.updateInterval_ = null;
    }));
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
    '$routeParams',
    '$interval',
    '$scope',
    'Backend',
    MissionDashboardCtrl
]);
