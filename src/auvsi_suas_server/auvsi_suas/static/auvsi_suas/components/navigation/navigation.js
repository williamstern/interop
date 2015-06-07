/**
 * Navigation controller for main application navigation.
 */


/**
 * Navigation controller for main application navigation.
 * @param $routeParams The routeParams service.
 */
NavigationCtrl = function($routeParams) {
    /**
     * The routeParams used to obtain the mission ID.
     */
    this.routeParams = $routeParams;
};


/**
 * Whether to show mission-specific links.
 * @returns Whether a mission is specified and links should be showed.
 */
NavigationCtrl.prototype.shouldShowMissionLinks = function() {
    return !!this.routeParams['missionId'];
};


// Register controller with app.
angular.module('auvsiSuasApp').controller('NavigationCtrl', [
    '$routeParams',
    NavigationCtrl
]);
