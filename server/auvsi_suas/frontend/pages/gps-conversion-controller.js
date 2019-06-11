/**
 * Controller for the GPS Conversion page.
 */

/**
 * Controller for the GPS Conversion page.
 * @param {!angular.$http} $http The http service.
 * @final
 * @construct
 * @struct
 * @ngInject
 */
GpsConversionCtrl = function($http) {
    /**
     * @export {!string} The latitude string.
     */
    this.latitudeStr = '';

    /**
     * @export {!string} The longitude string.
     */
    this.longitudeStr = '';

    /**
     * @export {!number} The latitude converted.
     */
    this.latitude = 0;

    /**
     * @export {!number} The longitude converted.
     */
    this.longitude = 0;

    /**
     * @private {!angular.$http} The http service.
     */
    this.http_ = $http;
};

GpsConversionCtrl.prototype.update = function() {
    this.http_.post('/api/utils/gps_conversion', {
        latitude: this.latitudeStr,
        longitude: this.longitudeStr,
    }).then(angular.bind(this, this.setConversion_));
};

GpsConversionCtrl.prototype.setConversion_ = function(response) {
    this.latitude = response.data.latitude;
    this.longitude = response.data.longitude;
};

// Register controller with app.
angular.module('auvsiSuasApp').controller('GpsConversionCtrl', [
    '$http',
    GpsConversionCtrl
]);
