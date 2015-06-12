/**
 * Directive for 3D map view of Mission Scene.
 */


/**
 * Directive for 3D map view of Mission Scene.
 */
MissionMapView = function($window, MissionScene) {
    /**
     * The window service.
     */
    this.window_ = $window;

    /**
     * The mission scene service.
     */
    this.missionScene_ = MissionScene;

    /**
     * The element scope.
     */
    this.scope_ = null;

    /**
     * The element.  */
    this.element_ = null;

    /**
     * The element attributes.
     */
    this.attrs_ = null;

    /**
     * The width of the view.
     */
    this.width_ = null;

    /**
     * The height of the view.
     */
    this.height_ = null;

    /**
     * The WebGL renderer.
     */
    this.renderer_ = null;

    /**
     * The camera.
     */
    this.camera_ = null;

    /**
     * Raycaster for view.
     */
    this.raycaster_ = new THREE.Raycaster();

    /**
     * The mouse down position.
     */
    this.mouseDownPos_ = new THREE.Vector2();

    /**
     * The mouse move position.
     */
    this.mouseMovePos_ = new THREE.Vector2();

    /**
     * The mouse down position in world coordinates.
     */
    this.mouseDownWorldPos_ = new THREE.Vector3();

    /**
     * The mouse move position in world coordinates.
     */
    this.mouseMoveWorldPos_ = new THREE.Vector3();
};


/**
 * Initialize the directive instance.
 * @param scope The directive scope.
 * @param element The directive element.
 * @param attrs The directive attributes.
 */
MissionMapView.prototype.link = function(scope, element, attrs) {
    // Store directive information.
    this.scope_ = scope;
    this.element_ = element;
    this.attrs_ = attrs;

    // Create a renderer and add to directive element.
    this.renderer_ = new THREE.WebGLRenderer({antialias: true});
    element.append(this.renderer_.domElement);
    // Create a camera and configure it.
    var fieldOfView = 60;
    var aspectRatio = 1;
    var nearClipPlane = 0.1;
    var farClipPlane = 100000;
    this.camera_ = new THREE.PerspectiveCamera(
            fieldOfView, aspectRatio, nearClipPlane, farClipPlane);

    // Set camera and renderer sizes.
    this.setCameraAndRendererSize_();

    // Start the camera above the ground, with 45deg azimuth, looking at origin.
    this.camera_.position.set(0, -300, 300);
    this.camera_.up = new THREE.Vector3(0, 0, 1);
    this.camera_.lookAt(new THREE.Vector3(0, 0, 0));

    // Whenever the window resizes, update the camera and renderer.
    angular.element(this.window_).on(
            'resize', angular.bind(this, this.setCameraAndRendererSize_));

    // Whenever mouse is pressed/moved/scrolled, update camera.
    angular.element(element).on(
            'mousedown', angular.bind(this, this.mouseUpDown_, true));
    angular.element(element).on(
            'mouseup', angular.bind(this, this.mouseUpDown_, false));
    angular.element(element).on(
            'mousemove', angular.bind(this, this.mouseMoved_));
    angular.element(element).on(
            'mousewheel', angular.bind(this, this.mouseScrolled_));
    
    // Start render loop.    
    this.render_();
};


/**
 * Sets the camera and renderer to match the view.
 */
MissionMapView.prototype.setCameraAndRendererSize_ = function() {
    this.width_ = this.element_[0].offsetWidth - this.scope_.offsetWidth;
    this.height_ = this.window_.innerHeight - this.scope_.offsetHeight;
    // Set renderer size.
    this.renderer_.setSize(this.width_, this.height_);
    // Set camera aspect ratio.
    this.camera_.aspect = this.width_ / this.height_;
    this.camera_.updateProjectionMatrix();
};


/**
 * Gets the normalized device coordinates for the position.
 * @param offsetX The screen X coordinate.
 * @param offsetY The screen Y coordinate.
 * @return The normalized device coordinates.
 */
MissionMapView.prototype.getNormalizedDeviceCoords_ = function(
        offsetX, offsetY, pos) {
    var pos = new THREE.Vector2();
    pos.x = (event.offsetX / this.width_) * 2 - 1;
    pos.y = (event.offsetY / this.height_) * -2 + 1;
    return pos;
};


/**
 * Gets the mouse world position for a click on the ground.
 * @param mousePos The mouse position.
 * @return The mouse world position, or null if no intersection was found.
 */
MissionMapView.prototype.getMousePositionOnGround_ = function(
        mousePos, mouseWorldPos) {
    this.raycaster_.setFromCamera(mousePos, this.camera_);
    var intersects = this.raycaster_.intersectObject(this.missionScene_.ground);
    if (intersects.length == 0) {
        return null;
    }
    return intersects[0].point;
};


/**
 * Updates the state of the mouse click.
 * @param mouseDown Whether the mouse is down.
 */
MissionMapView.prototype.mouseUpDown_ = function(mouseDown, event) {
    this.mouseDown_ = mouseDown;

    if(mouseDown) {
        // Track the mouse down position in world coordinates.
        this.mouseDownPos_ = this.getNormalizedDeviceCoords_(
                event.offsetX, event.offsetY);
        this.mouseDownWorldPos_ = this.getMousePositionOnGround_(
                this.mouseDownPos_);
    }
};


/**
 * Updates the mouse position and camera.
 * @param event The event containing mouse details.
 */
MissionMapView.prototype.mouseMoved_ = function(event) {
    event.preventDefault();
    // If mouse is not down, ignore.
    if (!this.mouseDown_) {
        return;
    }

    // Get mouse position in world coordinates to compare against mouse down.
    this.mouseMovePos_ = this.getNormalizedDeviceCoords_(
            event.offsetX, event.offsetY);
    this.mouseMoveWorldPos_ = this.getMousePositionOnGround_(
            this.mouseMovePos_);

    // Apply offset to move position under mouse back to position at mouse down.
    if (!!this.mouseDownWorldPos_ && !!this.mouseMoveWorldPos_) {
        var mouseWorldMovement = new THREE.Vector3();
        mouseWorldMovement.subVectors(this.mouseDownWorldPos_, this.mouseMoveWorldPos_);
        this.camera_.position.x += mouseWorldMovement.x;
        this.camera_.position.y += mouseWorldMovement.y;
        this.camera_.updateMatrixWorld();
    }
};


/**
 * Updates the mouse scroll and camera.
 * @param event The event containing mouse details.
 */
MissionMapView.prototype.mouseScrolled_ = function(event) {
    this.camera_.position.z += event.originalEvent.deltaY;
    if (this.camera_.position.z < 1) {
        this.camera_.position.z = 1;
    }
    if (this.camera_.position.z > 10000) {
        this.camera_.position.z = 10000;
    }
};


/**
 * Renders the mission scene in a render loop.
 */
MissionMapView.prototype.render_ = function() {
    requestAnimationFrame(angular.bind(this, this.render_));

    if (!!this.missionScene_.scene) {
        this.renderer_.render(this.missionScene_.scene, this.camera_);
    }
};


// Register the directive.
angular.module('auvsiSuasApp').directive('missionMapView', [
    '$window',
    'MissionScene',
    function($window, MissionScene) {
        var mapView = new MissionMapView($window, MissionScene);
        return {
            restrict: 'E',
            scope: {
                offsetWidth: '=',
                offsetHeight: '='
            },
            templateUrl: '/static/auvsi_suas/components/mission-map-view/mission-map-view.html',
            link: angular.bind(mapView, mapView.link)
        };
    }
]);
