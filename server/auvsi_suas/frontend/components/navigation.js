/**
 * @fileoverview Navigation controller for main application navigation.
 */


/**
 * Navigation controller for main application navigation.
 * @param {!angular.$routeParams} $routeParams The routeParams service.
 * @final
 * @constructor
 * @struct
 * @ngInject
 */
NavigationCtrl = function($routeParams) {
    /**
     * @private {!angular.$routeParams} The routeParams service.
     */
    this.routeParams_ = $routeParams;

    /**
     * @export {?Array<!Object>} The generic links.
     */
    this.links_ = [
        {
            text: "Live View (KML)",
            url: "/api/missions/live.kml",
            target: "_blank"
        },
        {
            text: "Export Data (KML)",
            url: "/api/missions/export.kml",
            target: "_blank"
        },
        {
            text: "GPS Conversion",
            url: "/#!/gps_conversion",
            target: "_self"
        },
        {
            text: "Bulk Create Teams",
            url: "/#!/bulk_create_teams",
            target: "_self"
        },
        {
            text: "Edit Data",
            url: "/admin",
            target: "_blank"
        },
    ];

    /**
     * @private {?Number} The current mission ID.
     */
    this.mission_ = null;

    /**
     * @private {?Array<!Object>} The mission links.
     */
    this.missionLinks_ = null;
};


/**
 * Gets the generic links for the navigation.
 * @return {!Array<!Object>} The list of links.
 * @export
 */
NavigationCtrl.prototype.getLinks = function() {
    return this.links_;
};


/**
 * Whether to show mission-specific links.
 * @return {!boolean} Whether a mission is specified and links should be showed.
 * @export
 */
NavigationCtrl.prototype.shouldShowMissionLinks = function() {
    return !!this.routeParams_['missionId'];
};


/**
 * Updates the mission links.
 */
NavigationCtrl.prototype.updateMissionLinks_ = function() {
    this.missionLinks_ = [
        {
            text: "Dashboard",
            url: "/#!/mission/" + this.mission_,
            target: "_self",
        },
        {
            text: "Review Odlcs",
            url: "/#!/mission/" + this.mission_ + "/odlcs",
            target: "_self"
        },
        {
            text: "Evaluate Teams",
            url: "/#!/mission/" + this.mission_ + "/evaluate",
            target: "_self"
        },
        {
            text: "Printable Details",
            url: "/api/missions/" + this.mission_ + "/mission.html",
            target: "_blank",
        },
    ];
};


/**
 * Gets the mission specific links for the navigation.
 * @return {!Array<!Object>} The list of links.
 * @export
 */
NavigationCtrl.prototype.getMissionLinks = function() {
    var mission = this.routeParams_['missionId'];
    if (this.mission_ != mission) {
        this.mission_ = mission;
        this.updateMissionLinks_();
    }
    return this.missionLinks_;
};


// Register controller with app.
angular.module('auvsiSuasApp').controller('NavigationCtrl', [
    '$routeParams',
    NavigationCtrl
]);
