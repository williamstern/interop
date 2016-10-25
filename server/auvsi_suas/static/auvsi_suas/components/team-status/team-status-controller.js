/**
 * @fileoverview Directive for team status view.
 */


/**
 * Directive for the team status view.
 * @final
 * @constructor
 * @struct
 * @ngInject
 */
TeamStatusCtrl = function() {
    /**
     * @export {?Object} The team object, injected by directive.
     */
    this.team;
};


/**
 * Gets the classes used to color a team's display on the dashboard.
 * @return {!string} The color classes.
 * @export
 */
TeamStatusCtrl.prototype.getTeamColorClasses = function() {
    classes = [];
    if (this.isActive()) {
        classes.push('team-status-active');
    }
    if (this.team.in_air) {
        classes.push('team-status-in-air');
    }
    return classes.join(' ');
};


/**
 * @return {!boolean} Whether the team is active.
 * @export
 */
TeamStatusCtrl.prototype.isActive = function() {
    return !!this.team.telemetry &&
        new Date() - new Date(this.team.telemetry.timestamp) < 3000;
};


/**
 * @return {!boolean} Whether to show the team.
 * @export
 */
TeamStatusCtrl.prototype.shouldShow = function() {
    return this.isActive() || this.team.in_air || this.team.on_clock ||
           this.team.on_timeout;
};


// Register the directive.
angular.module('auvsiSuasApp').directive('teamStatus', [
    function() {
        return {
            restrict: 'E',
            scope: {},
            bindToController: {
                team: '='
            },
            controller: TeamStatusCtrl,
            controllerAs: 'teamStatusCtrl',
            templateUrl: ('/static/auvsi_suas/components/' +
                          'team-status/team-status.html'),
        };
    }
]);
