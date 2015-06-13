/**
 * Controller for the Mission Dashboard page.
 */



/**
 * Controller for the Mission Dashboard page.
 * @param $rootScope The root scope to listen for events.
 * @param Backend The backend service.
 * @param MissionScene The mission scene building service.
 */
MissionDashboardCtrl = function($rootScope, Backend, MissionScene) {
    /**
     * The backend service.
     */
    this.Backend = Backend;

    /**
     * The mission scene buildling service.
     */
    this.MissionScene = MissionScene;

    // Whenever the backend data is updated, rebuild the scene.
    $rootScope.$on(
            'Backend.dataUpdated',
            angular.bind(this, this.rebuildMissionScene));
};


/**
 * Rebuild the mission scene using the backend data.
 */
MissionDashboardCtrl.prototype.rebuildMissionScene = function() {
    this.MissionScene.rebuildScene(
            this.Backend.mission, this.Backend.obstacles,
            this.Backend.telemetry);
};


/**
 * Determines whether a team is active or in-air.
 * @param team The team to test.
 * @returns Whether team is active or in-air.
 */
MissionDashboardCtrl.prototype.isTeamActiveOrInAir = function(team) {
    return team.active || team.in_air;
};


/**
 * Gets the class used to color a team's display on the dashboard.
 * @param team The team to get the color class for.
 * @returns The color class.
 */
MissionDashboardCtrl.prototype.getTeamColorClass = function(team) {
    if (team.active && team.in_air) {
        return 'mission-dashboard-team-active-and-in-air';
    } else if (team.active) {
        return 'mission-dashboard-team-active';
    } else if (team.in_air) {
        return 'mission-dashboard-team-in-air';
    } else {
        return 'mission-dashboard-team-inactive-and-not-in-air';
    }

};


/**
 * Gets a list of teams which are active or in-air.
 * @returns A list of teams which are active or in-air.
 */
MissionDashboardCtrl.prototype.getActiveOrInAirTeams = function() {
    // Check that data has been loaded.
    if (!this.Backend.teams || this.Backend.teams.length == 0) {
        return [];
    }

    // Get all teams which are relevant.
    teams = [];
    for (var i = 0; i < this.Backend.teams.length; i++) {
        if (this.isTeamActiveOrInAir(this.Backend.teams[i])) {
            teams.push(this.Backend.teams[i]);
        }
    }
    return teams;
};


// Register controller with app.
angular.module('auvsiSuasApp').controller('MissionDashboardCtrl', [
    '$rootScope',
    'Backend',
    'MissionScene',
    MissionDashboardCtrl
]);
