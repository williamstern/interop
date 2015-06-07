/**
 * Controller for the Mission Dashboard page.
 */



/**
 * Controller for the Mission Dashboard page.
 * @param Backend The backend service.
 */
MissionDashboardCtrl = function(Backend) {
    /**
     * The backend service.
     */
    this.Backend = Backend;
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
    'Backend',
    MissionDashboardCtrl
]);
