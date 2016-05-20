/**
 * Tests for the Backend service.
 */


describe("Backend service", function() {
    var rootScope, interval, httpBackend;
    var intervalTime = 100000;
    var backend;
    var missions, teams, telemetry, obstacles, reviewTargets;

    beforeEach(module('auvsiSuasApp'));

    beforeEach(inject(function($rootScope, $interval, $httpBackend, Backend) {
        rootScope = $rootScope;
        interval = $interval;
        httpBackend = $httpBackend;
        backend = Backend;

        // Mock data, contents unimportant.
        missions = [{id: 1}];
        teams = [{id: 100}];
        telemetry = [{id: 200}];
        obstacles = {id: 300};
        reviewTargets = [{id: 200}];

        $httpBackend.whenGET('/api/missions').respond(missions);
        $httpBackend.whenGET('/api/teams').respond(teams);
        $httpBackend.whenGET('/api/telemetry?limit=1').respond(telemetry);
        $httpBackend.whenGET('/api/obstacles?log=false')
            .respond(obstacles);
        $httpBackend.whenGET('/api/targets/review').respond(reviewTargets);
        $httpBackend.whenPUT('/api/targets/review/200').respond({id: 200, approved: true});
    }));

    it("Should initially have null fields", function() {
        expect(backend.missions).toBe(null);
        expect(backend.teams).toBe(null);
        expect(backend.telemetry).toBe(null);
        expect(backend.obstacles).toBe(null);
        expect(backend.reviewTargets).toBe(null);
    });

    it("Should sync with backend", function() {
        interval.flush(intervalTime);
        httpBackend.flush();
        expect(backend.missions[0].id).toEqual(missions[0].id);
        expect(backend.teams[0].id).toEqual(teams[0].id);
        expect(backend.telemetry[0].id).toEqual(telemetry[0].id);
        expect(backend.obstacles.id).toEqual(obstacles.id);
        expect(backend.reviewTargets[0].id).toEqual(reviewTargets[0].id);
    });

    it("Should notify data updated", function() {
        var notified = false;
        rootScope.$on('Backend.dataUpdated', function() {
            notified = true;
        });

        interval.flush(intervalTime);
        httpBackend.flush();
        expect(notified).toBe(true);
    });

    it("Should update team", function() {
        interval.flush(intervalTime);
        httpBackend.flush();
        expect(backend.reviewTargets[0].approved).toBe(undefined);

        backend.reviewTargets[0].$update();
        httpBackend.flush();
        expect(backend.reviewTargets[0].approved).toBe(true);
    });
});
