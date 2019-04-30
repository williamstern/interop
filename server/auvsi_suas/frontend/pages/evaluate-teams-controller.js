/**
 * Controller for the Evaluate Teams page.
 */


/**
 * Controller for the Evaluate Teams page.
 * @param {!angular.$window} $window The window service.
 * @param {!Object} Backend The backend service.
 * @final
 * @constructor
 * @struct
 * @ngInject
 */
EvaluateTeamsCtrl = function($window, $routeParams, Backend) {
    /**
     * @export {?Array<Object>} The teams for evaluation.
     */
    this.teams = null;

    /**
     * @export {!string} The ID of the selected team.
     */
    this.selectedTeamId = "-1";

    /**
     * @private @const {!angular.$window} The window service.
     */
    this.window_ = $window;

    /**
     * @private @const {integer} The mission ID for evaluation.
     */
    this.missionId_ = $routeParams['missionId'];

    // Get the teams to display.
    Backend.teamsResource.query({}).$promise.then(
            angular.bind(this, this.setTeams_));
};


/**
 * Evaluates the teams and renders the result.
 * @export
 */
EvaluateTeamsCtrl.prototype.evaluate = function() {
    // Determine query from selected team.
    var id = parseInt(this.selectedTeamId, 10);
    var query = '';
    if (id != -1) {
        query = '?team=' + id;
    }

    // Open evaluation in new tab.
    this.window_.open('/api/missions/' + this.missionId_ + '/evaluate.zip'+ query,
                      '_blank');
};


/**
 * Sets the teams.
 * @param {Array<Object>} teams The teams to set.
 * @private
 */
EvaluateTeamsCtrl.prototype.setTeams_ = function(teams) {
    this.teams = teams;
};


// Register controller with app.
angular.module('auvsiSuasApp').controller('EvaluateTeamsCtrl', [
    '$window',
    '$routeParams',
    'Backend',
    EvaluateTeamsCtrl
]);
