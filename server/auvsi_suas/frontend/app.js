/**
 * @fileoverview Main application definition. This sets up the angular module
 * and the routes.
 */


/**
 * @export {!angular.Module} Application module.
 */
var auvsiSuasApp = angular.module('auvsiSuasApp', [
    'ngResource',
    'ngRoute'
]);


// Configure routes to templates and controllers.
auvsiSuasApp.config(['$routeProvider', function($routeProvider) {
    $routeProvider.
        when('/', {
            templateUrl: '/static/pages/mission-list.html',
            controller: 'MissionListCtrl',
            controllerAs: 'missionListCtrl'
        }).
        when('/mission/:missionId', {
            templateUrl: '/static/pages/mission-dashboard.html',
            controller: 'MissionDashboardCtrl',
            controllerAs: 'missionDashboardCtrl'
        }).
        when('/mission/:missionId/odlcs', {
            templateUrl: '/static/pages/odlc-review.html',
            controller: 'OdlcReviewCtrl',
            controllerAs: 'odlcReviewCtrl'
        }).
        when('/mission/:missionId/evaluate', {
            templateUrl: '/static/pages/evaluate-teams.html',
            controller: 'EvaluateTeamsCtrl',
            controllerAs: 'evaluateTeamsCtrl'
        }).
        when('/gps_conversion', {
            templateUrl: '/static/pages/gps-conversion.html',
            controller: 'GpsConversionCtrl',
            controllerAs: 'gpsConversionCtrl'
        }).
        when('/bulk_create_teams', {
            templateUrl: '/static/pages/bulk-create-teams.html',
        }).
        otherwise({
            redirectTo: '/'
        });
}]);
