/**
 * Controller for the Mission List page.
 */



/**
 * Controller for the Mission List page.
 * @param Backend The backend service.
 */
MissionListCtrl = function(Backend) {
    /**
     * The backend service.
     */
    this.Backend = Backend;
};


/**
 * Determines whether there are missions.
 * @return Whether there are missions.
 */
MissionListCtrl.prototype.hasMissions = function() {
    return !!this.Backend.missions && this.Backend.missions.length != 0;
};
 


// Register controller with app.
angular.module('auvsiSuasApp').controller('MissionListCtrl', [
    'Backend',
    MissionListCtrl
]);
