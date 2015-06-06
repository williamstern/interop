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


// Register controller with app.
angular.module('auvsiSuasApp').controller('MissionListCtrl', [
    'Backend',
    MissionListCtrl
]);
