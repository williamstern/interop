/**
 * Directive for 3D map view of Mission Scene.
 */


/**
 * Directive for 3D map view of Mission Scene.
 */
MissionMapView = function(MissionScene) {
    // Return the parameters for the directive.
    return {
        restrict: 'E',
        scope: {
            missionScene: '=',
        },
        templateUrl: '/static/auvsi_suas/components/mission-map-view/mission-map-view.html',
        link: MissionMapViewLinkElement
    };
};


/**
 * Initialize the directive instance.
 * @param scope The directive scope.
 * @param element The directive element.
 * @param attrs The directive attributes.
 */
MissionMapViewLinkElement = function(scope, element, attrs) {
    // TODO(pmtischler): Make actual camera.
    // Create a unique camera.
    // TODO(pmtischler): Update size based on element size.
    var width = 500; // element.innerWidth
    var height = 500;
    var camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.z = 5;

    // Create a unqiue renderer and add to directive element.
    var renderer = new THREE.WebGLRenderer();
    renderer.setSize(width, height);
    element.append(renderer.domElement);

    // Start render loop.    
    MissionMapViewRender(scope, camera, renderer);
};


/**
 * Renders the mission scene in a render loop.
 * @param scope The scope containing the MissionScene.
 * @param camera The camera to render with.
 * @param renderer The renderer to render with.
 */
MissionMapViewRender = function(scope, camera, renderer) {
    requestAnimationFrame(
            angular.bind(this, MissionMapViewRender, scope, camera, renderer));
    if (!!scope.missionScene.scene) {
        renderer.render(scope.missionScene.scene, camera);
    }
};


// Register the directive.
angular.module('auvsiSuasApp').directive('missionMapView', [
    MissionMapView
]);
