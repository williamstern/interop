/**
 * Tests for the MissionDashboardCtrl controller.
 */


describe("MissionDashboardCtrl controller", function() {
    var teams;
    var routeParams, httpBackend, interval;
    var missionDashboardCtrl;

    beforeEach(module('auvsiSuasApp'));

    beforeEach(inject(function($q, $rootScope, $interval, $httpBackend,
                               $controller, Backend) {
        teams = [
            {
                id: 1,
                on_clock: false,
                on_timeout: false,
                active: false,
                in_air: false
            },
            {
                id: 2,
                on_clock: true,
                on_timeout: false,
                active: false,
                in_air: false
            },
            {
                id: 3,
                on_clock: false,
                on_timeout: true,
                active: false,
                in_air: false
            },
            {
                id: 4,
                on_clock: false,
                on_timeout: false,
                active: true,
                in_air: false
            },
            {
                id: 5,
                on_clock: false,
                on_timeout: false,
                active: false,
                in_air: true
            },
        ];

        routeParams = {
            missionId: 1
        };

        missionDashboardCtrl = $controller('MissionDashboardCtrl', {
            $q: $q,
            $rootScope: $rootScope,
            $routeParams: routeParams,
            $interval: $interval,
            Backend: Backend
        });

        interval = $interval;
        httpBackend = $httpBackend;
        httpBackend.whenGET('/api/missions/1').respond({id: 1});
        httpBackend.whenGET('/api/teams').respond(teams);
        httpBackend.whenGET('/api/telemetry?limit=1&user=4')
            .respond([{user: 4, id: 10, latitude: 10}]);
        httpBackend.whenGET('/api/obstacles').respond({id: 300});
    }));

    it("Should get current mission", function() {
        httpBackend.flush();
        expect(missionDashboardCtrl.getMission().toJSON()).toEqual({id: 1});
    });

    it("Should get teams to display", function() {
        interval.flush(2000);
        httpBackend.flush();
        // Team 5 is not active, so expect 4.
        expect(missionDashboardCtrl.getTeamsToDisplay().length).toEqual(4);
    });
});
