"use client";

import { useRef, useState, useEffect, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

interface EarthProps {
  score: number; // 0 to 100
}

// ── Seeded random & FBM generators for high-fidelity procedural fallback ─────
function createSeededRandom(seed: number) {
  let s = seed;
  return function () {
    s = (s * 9301 + 49297) % 233280;
    return s / 233280;
  };
}

const fade = (t: number) => (1 - Math.cos(t * Math.PI)) * 0.5;

function noise2D(x: number, y: number, randomHash: (i: number, j: number) => number): number {
  const X = Math.floor(x) & 255;
  const Y = Math.floor(y) & 255;
  const xf = x - Math.floor(x);
  const yf = y - Math.floor(y);

  const u = fade(xf);
  const v = fade(yf);

  const n00 = randomHash(X, Y);
  const n10 = randomHash(X + 1, Y);
  const n01 = randomHash(X, Y + 1);
  const n11 = randomHash(X + 1, Y + 1);

  const x1 = n00 * (1 - u) + n10 * u;
  const x2 = n01 * (1 - u) + n11 * u;

  return x1 * (1 - v) + x2 * v;
}

function fbm(x: number, y: number, randomHash: (i: number, j: number) => number, octaves = 5): number {
  let value = 0.0;
  let amplitude = 0.55;
  let frequency = 1.0;
  for (let i = 0; i < octaves; i++) {
    value += amplitude * noise2D(x * frequency, y * frequency, randomHash);
    frequency *= 2.0;
    amplitude *= 0.5;
  }
  return value;
}

// ── Custom Atmospheric Fresnel Shader ─────────────────────────────────────────
const AtmosphereShader = {
  vertexShader: `
    varying vec3 vNormal;
    varying vec3 vEyeVector;
    void main() {
      // Interpolate surface normals and eye direction vectors
      vNormal = normalize(normalMatrix * normal);
      vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
      vEyeVector = normalize(-mvPosition.xyz);
      gl_Position = projectionMatrix * mvPosition;
    }
  `,
  fragmentShader: `
    varying vec3 vNormal;
    varying vec3 vEyeVector;
    uniform vec3 color;
    uniform float coefficient;
    uniform float power;
    void main() {
      // Calculate realistic atmospheric edge scatter intensity via Fresnel approximation
      float intensity = pow(coefficient - dot(vNormal, vEyeVector), power);
      gl_FragColor = vec4(color, intensity);
    }
  `
};

export default function Earth({ score }: EarthProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const cloudsRef = useRef<THREE.Mesh>(null);
  const atmosphereMeshRef = useRef<THREE.Mesh>(null);
  const atmosphereRef = useRef<THREE.ShaderMaterial>(null);

  const [textures, setTextures] = useState<{
    day: THREE.Texture;
    normal: THREE.Texture;
    specular: THREE.Texture;
    clouds: THREE.Texture;
  } | null>(null);

  // 1. Load real high-resolution NASA satellite textures from local public assets (100% offline-ready)
  useEffect(() => {
    const loader = new THREE.TextureLoader();
    let active = true;

    const urls = {
      day: "/assets/earth_day.jpg",
      normal: "/assets/earth_normal.jpg",
      specular: "/assets/earth_specular.jpg",
      clouds: "/assets/earth_clouds.png"
    };

    Promise.all([
      new Promise<THREE.Texture>((resolve, reject) => loader.load(urls.day, resolve, undefined, reject)),
      new Promise<THREE.Texture>((resolve, reject) => loader.load(urls.normal, resolve, undefined, reject)),
      new Promise<THREE.Texture>((resolve, reject) => loader.load(urls.specular, resolve, undefined, reject)),
      new Promise<THREE.Texture>((resolve, reject) => loader.load(urls.clouds, resolve, undefined, reject))
    ]).then(([day, normal, specular, clouds]) => {
      if (active) {
        [day, normal, specular, clouds].forEach(t => {
          t.wrapS = THREE.RepeatWrapping;
          t.wrapT = THREE.RepeatWrapping;
        });
        setTextures({ day, normal, specular, clouds });
      }
    }).catch(err => {
      console.warn("Failed to load realistic local satellite textures, using high-fidelity procedural fallback:", err);
    });

    return () => {
      active = false;
    };
  }, []);

  // 2. High-fidelity procedural texture generator (runs strictly as offline fallback)
  const fallbackTextures = useMemo(() => {
    if (textures) return null; // Skip procedural calculation if online maps loaded successfully

    const width = 1024;
    const height = 512;
    
    const terrainCanvas = document.createElement("canvas");
    terrainCanvas.width = width;
    terrainCanvas.height = height;
    const terrainCtx = terrainCanvas.getContext("2d")!;
    
    const emissiveCanvas = document.createElement("canvas");
    emissiveCanvas.width = width;
    emissiveCanvas.height = height;
    const emissiveCtx = emissiveCanvas.getContext("2d")!;
    
    const cloudsCanvas = document.createElement("canvas");
    cloudsCanvas.width = width;
    cloudsCanvas.height = height;
    const cloudsCtx = cloudsCanvas.getContext("2d")!;
    
    const random = createSeededRandom(99);
    const hashMatrix: number[][] = [];
    for (let i = 0; i < 256; i++) {
      hashMatrix[i] = [];
      for (let j = 0; j < 256; j++) {
        hashMatrix[i][j] = random();
      }
    }
    
    const randomHash = (i: number, j: number) => {
      return hashMatrix[i & 255][j & 255];
    };

    const terrainImg = terrainCtx.createImageData(width, height);
    const emissiveImg = emissiveCtx.createImageData(width, height);
    const cloudsImg = cloudsCtx.createImageData(width, height);

    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        // Map pixel coordinates to organic FBM noise coordinates simulating continents
        const nx = (x / width) * 16.0;
        const ny = (y / height) * 8.0;
        
        const val = fbm(nx, ny, randomHash, 6);
        const cloudVal = fbm(nx + 8, ny + 8, randomHash, 5);

        let r = 0, g = 0, b = 0;
        let er = 0, eg = 0, eb = 0;

        // Water
        if (val < 0.47) {
          const shallow = val / 0.47;
          r = Math.round(2 * (1 - shallow) + 10 * shallow);
          g = Math.round(5 * (1 - shallow) + 65 * shallow);
          b = Math.round(16 * (1 - shallow) + 115 * shallow);
        }
        // Sand Beach
        else if (val >= 0.47 && val < 0.495) {
          r = 215; g = 190; b = 150;
        }
        // Continents
        else {
          const altitude = (val - 0.495) / 0.505;
          if (score < 34) {
            // Low Emissions: Healthy green forests
            r = Math.round(25 * (1 - altitude) + 12 * altitude);
            g = Math.round(145 * (1 - altitude) + 65 * altitude);
            b = Math.round(55 * (1 - altitude) + 25 * altitude);
          } else if (score < 67) {
            // Medium Emissions: Warn dry brown grassland
            r = Math.round(140 * (1 - altitude) + 105 * altitude);
            g = Math.round(135 * (1 - altitude) + 90 * altitude);
            b = Math.round(75 * (1 - altitude) + 45 * altitude);
          } else {
            // High Emissions: Severe charcoal scorching
            r = Math.round(28 * (1 - altitude) + 12 * altitude);
            g = Math.round(22 * (1 - altitude) + 10 * altitude);
            b = Math.round(20 * (1 - altitude) + 8 * altitude);
          }

          // Gold night lights strictly on landmasses
          const cityLights = Math.sin(nx * 18) * Math.cos(ny * 18) > 0.42;
          if (cityLights) {
            if (score < 34) {
              er = 255; eg = 215; eb = 100; // Warm gold
            } else if (score < 67) {
              er = 245; eg = 145; eb = 45; // Warning amber
            } else {
              er = 220; eg = 35; eb = 20; // Critical neon red
            }
          }
        }

        const idx = (y * width + x) * 4;
        terrainImg.data[idx] = r;
        terrainImg.data[idx + 1] = g;
        terrainImg.data[idx + 2] = b;
        terrainImg.data[idx + 3] = 255;

        emissiveImg.data[idx] = er;
        emissiveImg.data[idx + 1] = eg;
        emissiveImg.data[idx + 2] = eb;
        emissiveImg.data[idx + 3] = 255;

        // Clouds Density
        let cloudAlpha = 0;
        if (cloudVal > 0.46) {
          cloudAlpha = Math.round((cloudVal - 0.46) * 480);
          cloudAlpha = Math.min(Math.max(cloudAlpha, 0), 235);
        }
        cloudsImg.data[idx] = 255;
        cloudsImg.data[idx + 1] = 255;
        cloudsImg.data[idx + 2] = 255;
        cloudsImg.data[idx + 3] = cloudAlpha;
      }
    }

    terrainCtx.putImageData(terrainImg, 0, 0);
    emissiveCtx.putImageData(emissiveImg, 0, 0);
    cloudsCtx.putImageData(cloudsImg, 0, 0);

    const terrainTexture = new THREE.CanvasTexture(terrainCanvas);
    const emissiveTexture = new THREE.CanvasTexture(emissiveCanvas);
    const cloudsTexture = new THREE.CanvasTexture(cloudsCanvas);

    [terrainTexture, emissiveTexture, cloudsTexture].forEach(t => {
      t.wrapS = THREE.RepeatWrapping;
      t.wrapT = THREE.RepeatWrapping;
    });

    return {
      map: terrainTexture,
      emissiveMap: emissiveTexture,
      cloudsMap: cloudsTexture,
    };
  }, [textures, score]);

  // 3. Dynamic colors and parameters based on user's emissions score
  const targetAtmosColor = useMemo(() => {
    if (score < 34) return new THREE.Color("#0284c7"); // Healthy bright blue glow
    if (score < 67) return new THREE.Color("#f97316"); // Warning orange glow
    return new THREE.Color("#dc2626"); // Critical toxic crimson red glow
  }, [score]);

  // Diffuse overlay tint and cloud tint parameters
  const surfaceTint = useMemo(() => {
    if (score < 34) return new THREE.Color("#ffffff"); // pristine day satellite textures
    if (score < 67) return new THREE.Color("#ebdcc5"); // mild yellow-brown industrial smog tint
    return new THREE.Color("#504040"); // extreme charred soot and carbon damage tint
  }, [score]);

  const cloudsTint = useMemo(() => {
    if (score < 34) return new THREE.Color("#ffffff"); // pristine white clouds
    if (score < 67) return new THREE.Color("#fceec7"); // yellowed greenhouse gas clouds
    return new THREE.Color("#655d56"); // heavy dark smoke, smog and soot layers
  }, [score]);

  // 4. Frame-by-frame updates (rotations, pulse waves, shader lerps)
  useFrame((state, delta) => {
    // Smooth rotation of the primary Earth sphere
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.055;
    }
    
    // Cloud shell rotates slightly faster to simulate real weather winds
    if (cloudsRef.current) {
      cloudsRef.current.rotation.y += delta * 0.085;
      cloudsRef.current.rotation.x += delta * 0.015;
    }

    // Atmosphere volumetric pulse scale animation
    if (atmosphereMeshRef.current) {
      // Volumetric breathing atmosphere glow pulse
      const pulseScale = 1.025 + Math.sin(state.clock.elapsedTime * 1.6) * 0.005;
      atmosphereMeshRef.current.scale.set(pulseScale, pulseScale, pulseScale);
    }

    if (atmosphereRef.current) {
      // Update shader uniforms smoothly
      atmosphereRef.current.uniforms.color.value.lerp(targetAtmosColor, 0.04);
    }
  });

  return (
    <group>
      {/* ────────────────── LAYER 1: Core Earth Mesh ────────────────── */}
      <mesh ref={meshRef}>
        <sphereGeometry args={[2.0, 64, 64]} />
        <meshPhysicalMaterial
          // Use loaded satellite day texture, otherwise fall back to clean procedural terrain map
          map={textures ? textures.day : fallbackTextures!.map}
          // Blend with custom industrial emissions tint
          color={surfaceTint}
          
          // Surface height/normal mapping for realistic terrain shadows
          normalMap={textures ? textures.normal : null}
          normalScale={new THREE.Vector2(0.8, 0.8)}
          
          // Specular/gloss mapping so oceans glisten while continents are matte
          roughnessMap={textures ? textures.specular : null}
          roughness={textures ? 0.35 : 0.45}
          metalness={0.05}
          
          // City Night Lights (Emissive overlay)
          emissiveMap={textures ? textures.specular : fallbackTextures!.emissiveMap}
          emissive={score < 34 ? new THREE.Color("#ffdf79") : score < 67 ? new THREE.Color("#f97316") : new THREE.Color("#ef4444")}
          emissiveIntensity={textures ? (score < 34 ? 2.5 : score < 67 ? 1.5 : 1.0) : 1.2}
          
          // Dynamic photoreal clearcoat reflection
          clearcoat={score < 34 ? 0.8 : score < 67 ? 0.45 : 0.1}
          clearcoatRoughness={0.2}
        />
      </mesh>

      {/* ────────────────── LAYER 2: Moving Weather/Cloud Mesh ────────────────── */}
      <mesh ref={cloudsRef} scale={[1.015, 1.015, 1.015]}>
        <sphereGeometry args={[2.0, 64, 64]} />
        <meshStandardMaterial
          map={textures ? textures.clouds : fallbackTextures!.cloudsMap}
          color={cloudsTint}
          transparent
          opacity={score < 34 ? 0.65 : score < 67 ? 0.8 : 0.9} // smog layers thicken under high score
          roughness={1}
          depthWrite={false}
          blending={THREE.NormalBlending}
        />
      </mesh>

      {/* ────────────────── LAYER 3: Volumetric Fresnel Atmosphere Glow ────────────────── */}
      <mesh ref={atmosphereMeshRef} scale={[1.035, 1.035, 1.035]}>
        <sphereGeometry args={[2.0, 64, 64]} />
        <shaderMaterial
          ref={atmosphereRef}
          vertexShader={AtmosphereShader.vertexShader}
          fragmentShader={AtmosphereShader.fragmentShader}
          uniforms={{
            color: { value: new THREE.Color(targetAtmosColor) },
            coefficient: { value: score < 34 ? 0.16 : score < 67 ? 0.25 : 0.38 }, // Thicker, denser glow for bad scores
            power: { value: score < 34 ? 3.8 : score < 67 ? 3.0 : 2.2 } // Soft edge gradient for healthy, harsh thick warning edge for critical
          }}
          blending={THREE.AdditiveBlending}
          side={THREE.BackSide}
          transparent={true}
          depthWrite={false}
        />
      </mesh>
    </group>
  );
}
