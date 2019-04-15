/**
 * @fileoverview Service to interact with backend.
 * The data will be synced with the backend at a regular interval. You can
 * access the data via public fields of the service. When data is updated it
 * will broadcast an 'Backend.dataUpdated' event.
 */


/**
 * Service to interact with the backend.
 * @param {!angular.Resource} $resource The resource service.
 * @final
 * @constructor
 * @struct
 * @ngInject
 */
Backend = function($resource) {
    /**
     * @export @const {!Object} Missions interface.
     */
    this.missionResource = $resource('/api/missions/:id', {id: '@id'});

    /**
     * @export @const {!Object} Teams interface.
     */
    this.teamsResource = $resource('/api/teams');

    /**
     * @export @const {!Object} Odlc review interface.
     */
    this.odlcReviewResource = $resource(
            '/api/odlcs/review/:id',
            {id: '@odlc.id'},
            {'put': {method: 'PUT'}});
};


// Register the service.
angular.module('auvsiSuasApp').service('Backend', [
    '$resource',
    Backend
]);
