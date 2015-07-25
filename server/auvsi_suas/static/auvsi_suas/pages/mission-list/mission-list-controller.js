/**
 * @fileoverview Controller for the Mission List page.
 */



/**
 * Controller for the Mission List page.
 * @param {!Object} Backend The backend service.
 * @final
 * @constructor
 * @struct
 * @ngInject
 */
MissionListCtrl = function(Backend) {
    /**
     * @private @const {!Object} The backend service.
     */
    this.backend_ = Backend;
};


/**
 * Determines whether there are missions.
 * @return {!boolean} Whether there are missions.
 * @export
 */
MissionListCtrl.prototype.hasMissions = function() {
    return !!this.backend_.missions && this.backend_.missions.length != 0;
};


// Register controller with app.
angular.module('auvsiSuasApp').controller('MissionListCtrl', [
    'Backend',
    MissionListCtrl
]);
