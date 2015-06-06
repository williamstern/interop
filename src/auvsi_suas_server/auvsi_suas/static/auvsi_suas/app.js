/**
 * Main application definition for frontend of the AUVSI SUAS server.
 */



/**
 * Application module.
 */
var auvsiSuasApp = angular.module('auvsiSuasApp', [
    'ngRoute'
]);



// Configure route to template and controller.
auvsiSuasApp.config(['$routeProvider', function($routeProvider) {
    $routeProvider.
        when('/', {
            templateUrl: '/static/auvsi_suas/pages/mission-list/mission-list.html',
            controller: 'MissionListCtrl',
            controllerAs: 'missionListCtrl'
        }).
        when('/mission/:missionId', {
            templateUrl: '/static/auvsi_suas/pages/mission-dashboard/mission-dashboard.html',
            controller: 'MissionDashboardCtrl',
            controllerAs: 'missionDashboardCtrl'
        }).
        otherwise({
            redirectTo: '/'
        });
}]);

