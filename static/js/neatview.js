var camera, scene, renderer;
var geometry, material, mesh;

//initNV();
//animateNV();

function initNV() {

  camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 1, 10000 );
  camera.position.z = 1000;

  scene = new THREE.Scene();

  geometry = new THREE.CubeGeometry( 200, 200, 200 );
  material = new THREE.MeshBasicMaterial( { color: 0xff0000, wireframe: true } );

  mesh = new THREE.Mesh( geometry, material );
  scene.add( mesh );

  renderer = new THREE.WebGLRenderer({
    canvas: document.getElementById('three_canvas')
  });
  //renderer.setSize( window.innerWidth, window.innerHeight );
  //renderer.domElement.id = "three";

  //document.body.appendChild( renderer.domElement );


}

function animateNV() {

  // note: three.js includes requestAnimationFrame shim
  requestAnimationFrame( animateNV );

  mesh.rotation.x += 0.01;
  mesh.rotation.y += 0.02;

  renderer.render( scene, camera );

}
