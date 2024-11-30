/*
 * Function for reading OBJ files and saving them in a list of arrays (JSON)
 *
 * Luis Daniel Filorio Luna A01028418
 * José Antonio González Martínez A01028517
 * 2024-11-15
 */

function loadObj(objContent) {
    const lines = objContent.split('\n');
    const pos = [[0, 0, 0]]; // lista de listas temporal de posiciones de vertices
    const apos = [];
    const normals = [[0, 0, 0]]; // lista de listas temporal de normales
    const anorm = [];
    const texCoords = [];
    const faces = [];
    const colors = [];
    
    lines.forEach(line => {
      const parts = line.trim().split(/\s+/);
      const type = parts[0];
      switch (type) {
        case 'v':
            pos.push(parts.slice(1).map(parseFloat));
            break;
        case 'vn':
            normals.push(parts.slice(1).map(parseFloat));
            break;
        case 'c':
            colors.push(...parts.slice(1).map(parseFloat));
            break;
        case 'vt':
            texCoords.push(parts.slice(1).map(parseFloat));
            break;
        case 'f':
            faces.push(...parts.slice(1).map(parseFloat));
            for (let part of parts.slice(1)){
                const parts2 = part.split("/").map(parseFloat);
                apos.push(...pos[parts2[0]]);
                anorm.push(...normals[parts2[2]]);
            }
            break;
      }
    });
  
    let arrays = {
      a_position: {
        numComponents: 3,
        data: apos
      },
      a_color_: {
        numComponents: 4,
        data: colors
      },
      a_normal_: {
        numComponents: 3,
        data: anorm
      },
      a_texCoord_: {
        numComponents: 2,
        data: texCoords
      }
    };
    
    console.log(arrays);
    return arrays;
  };

  export { loadObj };