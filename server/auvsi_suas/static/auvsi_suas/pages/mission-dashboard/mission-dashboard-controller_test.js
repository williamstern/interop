/**
 * Tests for the MissionDashboardCtrl controller.
 */


describe("MissionDashboardCtrl controller", function() {
    var routeParams, backend;
    var missionDashboardCtrl;

    beforeEach(module('auvsiSuasApp'));

    beforeEach(inject(function($rootScope, $controller) {
        routeParams = {
            missionId: 1
        };
        backend = {
            missions: [{id: 1}, {id: 2}],
            obstacles: [],
        };

        missionDashboardCtrl = $controller('MissionDashboardCtrl',
                                           {$rootScope: $rootScope,
                                            $routeParams: routeParams,
                                            Backend: backend});
    }));

    it("Should get current mission", function() {
        expect(missionDashboardCtrl.getCurrentMission()).toEqual({id: 1});

        routeParams.missionId = 1000;
        expect(missionDashboardCtrl.getCurrentMission()).toBe(null);

        missions = backend.missions;
        backend.missions = null;
        expect(missionDashboardCtrl.getCurrentMission()).toBe(null);
        backend.missions = missions;

        routeParams.missionId = null;
        expect(missionDashboardCtrl.getCurrentMission()).toBe(null);
    });

    it("Should get teams to display", function() {
        var teams = [
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
        teams_to_display = [teams[1], teams[2], teams[3], teams[4]];
        backend.teams = teams;

        expect(missionDashboardCtrl.getTeamsToDisplay())
            .toEqual(teams_to_display);
    });
});
