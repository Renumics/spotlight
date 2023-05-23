import * as THREE from 'three';

export const postprocessMesh = (mesh: THREE.Mesh): void => {
    /*
     * Postprocesses a parsed gltf mesh to support the functionality of our viewer.
     * - Adds vertex normals if necessary.
     * - Sets sane default material parameters.
     */

    const geometry = mesh.geometry as THREE.BufferGeometry;

    // compute vertex normals for smooth shading
    geometry.computeVertexNormals();

    // set material properties for all attached materials
    const materials =
        mesh.material instanceof THREE.Material ? [mesh.material] : mesh.material;

    for (const material of materials as THREE.MeshStandardMaterial[]) {
        material.side = THREE.DoubleSide;
        material.flatShading = false;

        // adjust material color for legacy pid coloring
        material.color = new THREE.Color();
        material.metalness = 0;
    }
};
