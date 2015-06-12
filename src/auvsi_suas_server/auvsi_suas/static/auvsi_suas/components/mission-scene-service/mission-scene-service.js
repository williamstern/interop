/**
 * Service to build 3D scenes representing missions.
 * The built scene can be accessed via public fields of the service. When the
 * scene is rebuilt it will broadcast an 'MissionScene.sceneUpdated' event.
 */


/**
 * Service to build 3D scenes representing missions.
 * @param $rootScope The root scope service.
 */
MissionScene = function($rootScope) {
    /**
     * The root scope service.
     */
    this.rootScope_ = $rootScope;

    /**
     * The scene that is built by the service.
     */
    this.scene = null;

    /**
     * The ground plane.
     */
    this.groundTexture = THREE.ImageUtils.loadTexture(
            '/static/auvsi_suas/components/mission-scene-service/img/ground.jpg');
    this.groundTexture.wrapS = THREE.RepeatWrapping;
    this.groundTexture.wrapT = THREE.RepeatWrapping;
    this.groundTexture.magFilter = THREE.LinearFilter;
    this.groundTexture.minFilter = THREE.LinearFilter;
    this.groundTexture.repeat.set(1000, 1000);
    this.groundMaterial = new THREE.MeshBasicMaterial({color: 0x526f35, map: this.groundTexture});
    this.groundGeometry = new THREE.PlaneBufferGeometry(1, 1);
    this.ground = new THREE.Mesh(this.groundGeometry, this.groundMaterial);
    this.ground.scale.set(100000, 100000, 100000);
};


/**
 * Rebuild the scene with the given mission data.
 * @param mission The mission configuration.
 * @param obstacles The obstacles data.
 * @param telemetry The UAS telemetry data.
 */
MissionScene.prototype.rebuildScene = function(mission, obstacles, telemetry) {
    // Create fresh scene for rebuild.
    var scene = new THREE.Scene();

    // Add the ground plane.
    scene.add(this.ground);

    // TODO(pmtischler): Make a real scene with the data.
    var geometry = new THREE.BoxGeometry( 1, 1, 1 );
    var material = new THREE.MeshBasicMaterial( { color: 0x00ff00 } );
    var cube = new THREE.Mesh( geometry, material );
    cube.scale.set(10,10,10);
    scene.add( cube );

    // Update the scene and notify others.
    this.scene = scene;
    this.rootScope_.$broadcast('MissionScene.sceneUpdated');
};


// Register the service.
angular.module('auvsiSuasApp').service('MissionScene', [
    '$rootScope',
    MissionScene
]);
