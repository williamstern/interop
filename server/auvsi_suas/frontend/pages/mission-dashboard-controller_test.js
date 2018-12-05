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
                team: 'user1',
                inAir: false
            },
            {
                team: 'user2',
                inAir: false
            },
            {
                team: 'user3',
                inAir: false
            },
            {
                team: 'user4',
                inAir: false
                telemetry: {
                    latitude: 38,
                    longitude: -76,
                    altitude: 0,
                    heading: 90
                },
                telemetry_timestamp: '3000-10-01T00:00:00+00:00',
            },
            {
                team: 'user5',
                inAir: true
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
        httpBackend.whenGET('/api/obstacles').respond({id: 300});
    }));

    it("Should get current mission", function() {
        httpBackend.flush();
        expect(missionDashboardCtrl.getMission().toJSON()).toEqual({id: 1});
    });

    it("Should get teams", function() {
        interval.flush(2000);
        httpBackend.flush();
        for (var i = 0; i < teams.length; i++) {
            expect(missionDashboardCtrl.teams[i].toJSON()).toEqual(teams[i]);
        }
    });
});
