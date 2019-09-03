/**
 * Controller for the Odlc Review page.
 */


/**
 * Controller for the Odlc Review page.
 * @param {!angular.Window} $window The window service.
 * @param {!Object} Backend The backend service.
 * @final
 * @constructor
 * @struct
 * @ngInject
 */
OdlcReviewCtrl = function($window, Backend) {
    /**
     * @private @const {!angular.Window} The window service.
     */
    this.window_ = $window;

    /**
     * @private{?Array<Object>} The odlcs for review.
     */
    this.odlcReviews_ = null;

    /**
     * @private {?Object} The odlc under review.
     */
    this.odlcReview_ = null;

    /**
     * @private {?Array<Object>} The odlc review details.
     */
    this.odlcDetails_ = null;

    // Query the backend for odlcs to review.
    Backend.odlcReviewResource.query({}).$promise.then(
            angular.bind(this, this.setOdlcs_));
};


/**
 * Gets the odlcs for review.
 * @return {?Array<Object>} The odlcs.
 * @export
 */
OdlcReviewCtrl.prototype.getReviewOdlcs = function() {
    return this.odlcReviews_;
};


/**
 * @return {?Object} The odlc under review.
 */
OdlcReviewCtrl.prototype.getReviewOdlc = function() {
    return this.odlcReview_;
};


/**
 * @return {?Object} The odlc details.
 */
OdlcReviewCtrl.prototype.getReviewOdlcDetails = function() {
    return this.odlcDetails_;
};


/**
 * Gets the class for the odlc.
 * @param {!Object} odlc The odlc.
 * @return {string} The class.
 * @export
 */
OdlcReviewCtrl.prototype.getOdlcButtonClass = function(odlc) {
    var thumbnailClass;
    if (odlc.thumbnailApproved == null) {
        thumbnailClass = 'btn btn-primary';
    } else if (odlc.thumbnailApproved) {
        thumbnailClass = 'btn btn-success';
    } else {
        thumbnailClass = 'btn btn-warning';
    }

    if (this.odlcReview_ && odlc.id == this.odlcReview_.odlc.id) {
        return thumbnailClass + ' disabled';
    } else {
        return thumbnailClass;
    }
};


/**
 * Sets the odlc under review.
 * @param {!Object} odlcReview The odlc review.
 * @export
 */
OdlcReviewCtrl.prototype.setReviewOdlc = function(odlcReview) {
    this.odlcReview_ = odlcReview;

    if (this.odlcReview_ == null) {
        return;
    }

    this.odlcDetails_ = [
        {'key': 'ID',
         'value': this.odlcReview_.odlc.id},
        {'key': 'Type',
         'value': this.odlcReview_.odlc.type},
    ];
    if (this.odlcReview_.odlc.type == 'STANDARD') {
        this.odlcDetails_ = this.odlcDetails_.concat([
            {'key': 'Alpha Color',
             'value': this.odlcReview_.odlc.alphanumericColor},
            {'key': 'Alpha',
             'value': this.odlcReview_.odlc.alphanumeric},
            {'key': 'Shape Color',
             'value': this.odlcReview_.odlc.shapeColor},
            {'key': 'Shape',
             'value': this.odlcReview_.odlc.shape}
        ]);
    } else {
        this.odlcDetails_ = this.odlcDetails_.concat([
            {'key': 'Desc',
             'value': this.odlcReview_.odlc.description}
        ]);
    }
};


/**
 * Saves the review status for the odlc under review. Advances to
 * the next odlc for review.
 */
OdlcReviewCtrl.prototype.saveReview = function() {
    this.odlcReview_.$put().then(
            angular.bind(this, this.nextOdlc_));
};


/**
 * @return {string} The class info for the odlc image review.
 */
OdlcReviewCtrl.prototype.getOdlcImgStyle = function() {
    if (!!this.odlcReview_) {
        return 'background-image: url(/api/odlcs/' + this.odlcReview_.odlc.id +
                '/image); height: ' + this.getOdlcImgHeight() + 'px;';
    } else {
        return '';
    }
};


/**
 * @return {number} The height of the odlc image display.
 */
OdlcReviewCtrl.prototype.getOdlcImgHeight = function() {
    return this.window_.innerHeight - 95;
};


/**
 * @param {Array<Object>} odlcs The odlcs to review.
 */
OdlcReviewCtrl.prototype.setOdlcs_ = function(odlcs) {
    this.odlcReviews_ = odlcs;
    if (this.odlcReviews_.length > 0) {
        this.setReviewOdlc(this.odlcReviews_[0]);
    } else {
        this.setReviewOdlc(null);
    }
};


/**
 * Advances to the next odlc.
 */
OdlcReviewCtrl.prototype.nextOdlc_ = function() {
    var odlcReviews = this.getReviewOdlcs();

    for (var i = 0; i < odlcReviews.length-1; i++) {
        if (odlcReviews[i].odlc.id == this.odlcReview_.odlc.id) {
            this.setReviewOdlc(odlcReviews[i+1]);
            return;
        }
    }

    this.setReviewOdlc(odlcReviews[odlcReviews.length-1]);
};


// Register controller with app.
angular.module('auvsiSuasApp').controller('OdlcReviewCtrl', [
    '$window',
    'Backend',
    OdlcReviewCtrl
]);
