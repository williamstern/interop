/**
 * Tests for the TeamStatusView controller.
 */

describe("TeamStatusCtrl controller", function() {
    var teamStatusCtrl, team;

    beforeEach(module('auvsiSuasApp'));

    beforeEach(inject(function($controller) {
        team = {
            active: true,
            in_air: true
        };
        teamStatusCtrl = new TeamStatusCtrl();
        teamStatusCtrl.team = team;
    }));

    it("Should get the team color class", function() {
        expect(teamStatusCtrl.getTeamColorClasses())
            .toEqual('team-status-active team-status-in-air');

        team.in_air = false;
        team.active = true;
        expect(teamStatusCtrl.getTeamColorClasses())
            .toEqual('team-status-active');

        team.in_air = true;
        team.active = false;
        expect(teamStatusCtrl.getTeamColorClasses())
            .toEqual('team-status-in-air');

        team.in_air = false;
        team.active = false;
        expect(teamStatusCtrl.getTeamColorClasses())
            .toEqual('');
    });
});
