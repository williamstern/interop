/**
 * Tests for the TargetReviewCtrl controller.
 */


describe("TargetReviewCtrl controller", function() {
    var backend;
    var reviewTargets, updateFunc;
    var targetReviewCtrl;

    beforeEach(module('auvsiSuasApp'));

    beforeEach(inject(function($controller) {
        updateFunc = function() {
            this.updated = true;
            return {then: function(func) {func();}};
        };
        reviewTargets = [
             {id: 1, thumbnail_approved: null, $update: updateFunc},
             {id: 2, thumbnail_approved: true, $update: updateFunc},
             {id: 3, thumbnail_approved: false, $update: updateFunc}];
        backend = {
            missions: [{id: 1}, {id: 2}],
            obstacles: [],
            reviewTargets: reviewTargets,
        };

        targetReviewCtrl = $controller('TargetReviewCtrl',
                                       {Backend: backend});
    }));

    it("Should get review targets", function() {
        expect(targetReviewCtrl.getReviewTargets()).toEqual(reviewTargets);
    });

    it("Should get target button class", function() {
        targetReviewCtrl.setReviewTarget(reviewTargets[0]);
        expect(targetReviewCtrl.getTargetButtonClass(reviewTargets[0]))
                .toEqual('button disabled');
        expect(targetReviewCtrl.getTargetButtonClass(reviewTargets[1]))
                .toEqual('success button');
        expect(targetReviewCtrl.getTargetButtonClass(reviewTargets[2]))
                .toEqual('alert button');
    });

    it("Should get review target", function() {
        targetReviewCtrl.setReviewTarget(reviewTargets[0]);
        expect(targetReviewCtrl.getReviewTarget()).toEqual(reviewTargets[0]);
    });

    it("Should update the review", function() {
        targetReviewCtrl.setReviewTarget(reviewTargets[0]);
        targetReviewCtrl.setReview(true);
        expect(reviewTargets[0].thumbnail_approved).toBe(true);
        expect(reviewTargets[0].updated).toBe(true);
        expect(targetReviewCtrl.getReviewTarget().id)
                .toEqual(reviewTargets[1].id);
    });
});
