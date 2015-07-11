/**
 * Service to perform unit calculations.
 */


/**
 * Service to perform unit calculations.
 */
Units = function() {
};


/**
 * Converts degrees to radians.
 * @param deg The degree to convert.
 * @return The value in radians.
 */
Units.prototype.degToRad = function(deg) {
    return deg * (Math.PI/180);
};


/**
 * Converts kilometers to feet.
 * @param km The distance in kilometers.
 * @return The distance in feet.
 */
Units.prototype.kmToFt = function(km) {
    return km * 3280.8399;
};


// Register the service.
angular.module('auvsiSuasApp').service('Units', [
    Units
]);
