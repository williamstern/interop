/**
 * @fileoverview Navigation controller for main application navigation.
 */


/**
 * Navigation controller for main application navigation.
 * @param {!angular.$routeParams} $routeParams The routeParams service.
 * @final
 * @constructor
 * @struct
 * @ngInject
 */
NavigationCtrl = function($routeParams) {
    /**
     * The routeParams used to obtain the mission ID.
     */
    this.routeParams = $routeParams;
};


/**
 * Whether to show mission-specific links.
 * @return {!boolean} Whether a mission is specified and links should be showed.
 * @export
 */
NavigationCtrl.prototype.shouldShowMissionLinks = function() {
    return !!this.routeParams['missionId'];
};


// Register controller with app.
angular.module('auvsiSuasApp').controller('NavigationCtrl', [
    '$routeParams',
    NavigationCtrl
]);
