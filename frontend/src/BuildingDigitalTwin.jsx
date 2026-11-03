import { useEffect, useRef, useState } from 'react'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { Building2, Info, Rotate3D, ZoomIn, Zap, Layers } from 'lucide-react'
import './BuildingDigitalTwin.css'

const FLOORS = [1, 2, 3, 4, 5, 6]

function ThreeBuilding({ selectedFloor, onSelectFloor }) {
  const mountRef = useRef(null)
  const selectFloorRef = useRef(onSelectFloor)

  useEffect(() => {
    selectFloorRef.current = onSelectFloor
  }, [onSelectFloor])

  useEffect(() => {
    const container = mountRef.current
    if (!container) return

    const scene = new THREE.Scene()
    scene.background = new THREE.Color('#eaf1f8')

    const camera = new THREE.PerspectiveCamera(
      42,
      container.clientWidth / container.clientHeight,
      0.1,
      1000
    )
    camera.position.set(11, 9, 13)

    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: false,
    })

    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.setSize(container.clientWidth, container.clientHeight)
    renderer.shadowMap.enabled = true
    renderer.shadowMap.type = THREE.PCFSoftShadowMap
    renderer.outputColorSpace = THREE.SRGBColorSpace
    renderer.toneMapping = THREE.ACESFilmicToneMapping
    renderer.toneMappingExposure = 1.15

    container.appendChild(renderer.domElement)

    const controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true
    controls.dampingFactor = 0.06
    controls.enablePan = true
    controls.minDistance = 7
    controls.maxDistance = 25
    controls.maxPolarAngle = Math.PI * 0.48
    controls.target.set(0, 3.1, 0)

    // Lighting
    const ambient = new THREE.AmbientLight('#ffffff', 2.0)
    scene.add(ambient)

    const sunlight = new THREE.DirectionalLight('#ffffff', 3.0)
    sunlight.position.set(8, 14, 10)
    sunlight.castShadow = true
    sunlight.shadow.mapSize.set(2048, 2048)
    scene.add(sunlight)

    const fillLight = new THREE.DirectionalLight('#b8d8ff', 1.0)
    fillLight.position.set(-8, 6, -8)
    scene.add(fillLight)

    // Materials
    const groundMaterial = new THREE.MeshStandardMaterial({
      color: '#d5dce3',
      roughness: 0.95,
    })

    const floorMaterials = [
      new THREE.MeshStandardMaterial({ color: '#b9cbd4', roughness: 0.8 }),
      new THREE.MeshStandardMaterial({ color: '#a9c1cc', roughness: 0.8 }),
      new THREE.MeshStandardMaterial({ color: '#c0d0d8', roughness: 0.8 }),
      new THREE.MeshStandardMaterial({ color: '#afc5cf', roughness: 0.8 }),
      new THREE.MeshStandardMaterial({ color: '#c0d0d8', roughness: 0.8 }),
      new THREE.MeshStandardMaterial({ color: '#a9c1cc', roughness: 0.8 }),
    ]

    const selectedMaterial = new THREE.MeshStandardMaterial({
      color: '#55c7bd',
      roughness: 0.7,
      emissive: '#123d3b',
      emissiveIntensity: 0.12,
    })

    const sideMaterial = new THREE.MeshStandardMaterial({
      color: '#91b6c3',
      roughness: 0.8,
    })

    const roofMaterial = new THREE.MeshStandardMaterial({
      color: '#34465f',
      roughness: 0.85,
    })

    const trimMaterial = new THREE.MeshStandardMaterial({
      color: '#e7eef2',
      roughness: 0.7,
    })

    const windowMaterial = new THREE.MeshStandardMaterial({
      color: '#547d91',
      roughness: 0.3,
      metalness: 0.15,
    })

    const equipmentMaterial = new THREE.MeshStandardMaterial({
      color: '#899cac',
      roughness: 0.8,
    })

    // Ground
    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(30, 30),
      groundMaterial
    )
    ground.rotation.x = -Math.PI / 2
    ground.position.y = -0.12
    ground.receiveShadow = true
    scene.add(ground)

    // Building dimensions
    const width = 6
    const depth = 4
    const floorHeight = 1.05
    const buildingHeight = FLOORS.length * floorHeight

    const floorMeshes = []

    // Main building floors
    FLOORS.forEach((floor) => {
      const geometry = new THREE.BoxGeometry(
        width,
        floorHeight - 0.045,
        depth
      )

      const material = floor === selectedFloor
        ? selectedMaterial
        : floorMaterials[floor - 1]

      const mesh = new THREE.Mesh(geometry, material)

      mesh.position.set(
        0,
        (floor - 0.5) * floorHeight,
        0
      )

      mesh.castShadow = true
      mesh.receiveShadow = true
      mesh.userData.floorNumber = floor

      scene.add(mesh)
      floorMeshes.push(mesh)
    })

    // Floor separation bands
    for (let floor = 0; floor <= FLOORS.length; floor++) {
      const band = new THREE.Mesh(
        new THREE.BoxGeometry(width + 0.12, 0.055, depth + 0.12),
        trimMaterial
      )

      band.position.y = floor * floorHeight
      band.castShadow = true
      scene.add(band)
    }

    // Side facade
    const sideFacade = new THREE.Mesh(
      new THREE.BoxGeometry(0.06, buildingHeight, depth),
      sideMaterial
    )

    sideFacade.position.set(width / 2 + 0.04, buildingHeight / 2, 0)
    sideFacade.castShadow = true
    scene.add(sideFacade)

    // Front facade windows
    const windowRows = FLOORS.length
    const windowsPerFloor = 7

    for (let floor = 1; floor <= windowRows; floor++) {
      for (let i = 0; i < windowsPerFloor; i++) {
        const windowMesh = new THREE.Mesh(
          new THREE.BoxGeometry(0.53, 0.48, 0.045),
          windowMaterial
        )

        const x = -2.45 + i * 0.81
        const y = (floor - 0.5) * floorHeight

        windowMesh.position.set(x, y, depth / 2 + 0.035)
        scene.add(windowMesh)
      }
    }

    // Vertical facade divisions
    for (let i = 0; i <= windowsPerFloor; i++) {
      const divider = new THREE.Mesh(
        new THREE.BoxGeometry(0.065, buildingHeight, 0.08),
        trimMaterial
      )

      divider.position.set(
        -3 + i * (width / windowsPerFloor),
        buildingHeight / 2,
        depth / 2 + 0.075
      )

      scene.add(divider)
    }

    // Roof slab
    const roof = new THREE.Mesh(
      new THREE.BoxGeometry(width + 0.4, 0.28, depth + 0.4),
      roofMaterial
    )

    roof.position.y = buildingHeight + 0.16
    roof.castShadow = true
    roof.receiveShadow = true
    scene.add(roof)

    // Rooftop equipment blocks
    for (let i = 0; i < 4; i++) {
      const equipment = new THREE.Mesh(
        new THREE.BoxGeometry(0.75, 0.55, 0.7),
        equipmentMaterial
      )

      equipment.position.set(
        -2.15 + i * 1.35,
        buildingHeight + 0.55,
        -0.65
      )

      equipment.castShadow = true
      scene.add(equipment)
    }

    // Roof solar-panel-style structures (illustrative)
    const panelMaterial = new THREE.MeshStandardMaterial({
      color: '#142e48',
      metalness: 0.3,
      roughness: 0.35,
    })

    for (let i = 0; i < 3; i++) {
      const panel = new THREE.Mesh(
        new THREE.BoxGeometry(1.25, 0.045, 0.55),
        panelMaterial
      )

      panel.position.set(
        -1.3 + i * 1.35,
        buildingHeight + 0.34,
        1.1
      )

      panel.rotation.x = -0.12
      scene.add(panel)
    }

    // Base platform
    const base = new THREE.Mesh(
      new THREE.BoxGeometry(width + 0.35, 0.18, depth + 0.35),
      new THREE.MeshStandardMaterial({ color: '#52677e' })
    )

    base.position.y = -0.02
    base.castShadow = true
    scene.add(base)

    // Raycasting for floor selection
    const raycaster = new THREE.Raycaster()
    const pointer = new THREE.Vector2()

    function handleClick(event) {
      const rect = renderer.domElement.getBoundingClientRect()

      pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
      pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1

      raycaster.setFromCamera(pointer, camera)

      const intersections = raycaster.intersectObjects(floorMeshes)

      if (intersections.length > 0) {
        const floor = intersections[0].object.userData.floorNumber
        selectFloorRef.current(floor)
      }
    }

    renderer.domElement.addEventListener('click', handleClick)

    // Responsive renderer
    const resizeObserver = new ResizeObserver(() => {
      if (!container.clientWidth || !container.clientHeight) return

      camera.aspect = container.clientWidth / container.clientHeight
      camera.updateProjectionMatrix()

      renderer.setSize(
        container.clientWidth,
        container.clientHeight
      )
    })

    resizeObserver.observe(container)

    let animationFrame

    function animate() {
      animationFrame = requestAnimationFrame(animate)
      controls.update()
      renderer.render(scene, camera)
    }

    animate()

    return () => {
      cancelAnimationFrame(animationFrame)
      resizeObserver.disconnect()
      renderer.domElement.removeEventListener('click', handleClick)
      controls.dispose()

      scene.traverse((object) => {
        if (object.geometry) object.geometry.dispose()

        if (object.material) {
          if (Array.isArray(object.material)) {
            object.material.forEach((material) => material.dispose())
          } else {
            object.material.dispose()
          }
        }
      })

      renderer.dispose()

      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement)
      }
    }
  }, [])

  // Update selected floor without rebuilding the 3D scene
  useEffect(() => {
    const container = mountRef.current
    if (!container) return

    // The scene stores floor meshes on the renderer canvas owner.
    // Selection is handled by the scene update below through a custom event.
    container.dispatchEvent(
      new CustomEvent('nexus-floor-change', {
        detail: { selectedFloor },
      })
    )
  }, [selectedFloor])

  return <div ref={mountRef} className="three-building-canvas" />
}

export default function BuildingDigitalTwin({ data }) {
  const [view, setView] = useState('twin')
  const [selectedFloor, setSelectedFloor] = useState(6)

  const baseline = data.scenarios.find(
    (item) => item.Scenario === 'Baseline'
  )

  const buildingDemand = Number(baseline?.Average_Demand || 0)

  return (
    <div className="digital-twin-page">
      <div className="welcome-section">
        <div>
          <p className="eyebrow">BUILDING VISUALIZATION</p>
          <h1>Building Digital Twin</h1>
          <p className="welcome-description">
            Explore an interactive 3D representation of Panther Education – Vincent.
          </p>
        </div>
      </div>

      <section className="twin-header">
        <div>
          <h2>Panther Education Building</h2>
          <p>Panther Site · Vincent · Building-level electricity data</p>
        </div>

        <div className="twin-tabs">
          <button
            className={view === 'twin' ? 'selected' : ''}
            onClick={() => setView('twin')}
          >
            <Rotate3D size={15} /> 3D Twin
          </button>

          <button
            className={view === 'energy' ? 'selected' : ''}
            onClick={() => setView('energy')}
          >
            <Zap size={15} /> Energy Map
          </button>

          <button
            className={view === 'zones' ? 'selected' : ''}
            onClick={() => setView('zones')}
          >
            <Layers size={15} /> Zones
          </button>
        </div>
      </section>

      <section className="twin-stage">
        {view === 'twin' && (
          <>
            <div className="twin-status">
              <span className="online-dot" />
              INTERACTIVE 3D MODEL
              <small>Drag to rotate · Scroll to zoom</small>
            </div>

            <div className="twin-floor-info">
              <strong>Floor {selectedFloor}</strong>
              <p>Selected building floor</p>
              <small>Illustrative floor representation</small>
            </div>

            <ThreeBuilding
              selectedFloor={selectedFloor}
              onSelectFloor={setSelectedFloor}
            />

            <div className="twin-controls-hint">
              <span><Rotate3D size={15} /> Drag to rotate</span>
              <span><ZoomIn size={15} /> Scroll to zoom</span>
            </div>
          </>
        )}

        {view === 'energy' && (
          <div className="energy-map-content">
            <h2>Building Energy Overview</h2>
            <p>
              The available dataset provides one building-level electricity
              demand series.
            </p>

            <div className="energy-total">
              <span>AVERAGE BASELINE PREDICTED DEMAND</span>
              <strong>{buildingDemand.toFixed(2)}</strong>
              <small>Dataset measurement units · Building-level value</small>
            </div>

            <div className="energy-building-map">
              {[6, 5, 4, 3, 2, 1].map((floor) => (
                <button
                  key={floor}
                  className={`energy-floor ${
                    selectedFloor === floor ? 'active' : ''
                  }`}
                  onClick={() => setSelectedFloor(floor)}
                >
                  <span>Floor {floor}</span>
                  <span>
                    {selectedFloor === floor
                      ? 'Selected floor'
                      : 'Illustrative zone'}
                  </span>
                </button>
              ))}
            </div>

            <p className="twin-disclaimer">
              Floor colors are illustrative only; no floor-wise electricity
              values are present in the dataset.
            </p>
          </div>
        )}

        {view === 'zones' && (
          <div className="energy-map-content">
            <h2>Building Zones</h2>
            <p>Select a floor to explore its place in the illustrative model.</p>

            <div className="zone-selector">
              {[6, 5, 4, 3, 2, 1].map((floor) => (
                <button
                  key={floor}
                  className={`zone-button ${
                    selectedFloor === floor ? 'active' : ''
                  }`}
                  onClick={() => setSelectedFloor(floor)}
                >
                  Floor {floor}
                </button>
              ))}
            </div>

            <div className="selected-zone">
              <Building2 size={38} />
              <div>
                <span>SELECTED ILLUSTRATIVE ZONE</span>
                <h3>Floor {selectedFloor}</h3>
                <p>
                  Floor representation for Panther Education – Vincent.
                </p>
              </div>
            </div>

            <div className="zone-data-note">
              <Info size={18} />
              <p>
                Actual floor-wise electricity consumption, occupancy, HVAC
                readings and sensor measurements are not available. NEXUS
                currently uses building-level electricity data.
              </p>
            </div>
          </div>
        )}
      </section>

      <section className="twin-energy-footer">
        <div>
          <span>BUILDING BASELINE DEMAND</span>
          <strong>{buildingDemand.toFixed(2)}</strong>
          <small>Dataset measurement units</small>
        </div>

        <div>
          <span>BUILDING AREA</span>
          <strong>11,248.1 m²</strong>
          <small>Panther Education – Vincent</small>
        </div>

        <div>
          <span>MODEL INTERACTION</span>
          <strong>3D Enabled</strong>
          <small>Rotatable building model</small>
        </div>
      </section>

      <p className="twin-global-disclaimer">
        The building geometry, floor divisions and rooftop equipment are
        illustrative. They do not represent measured floor plans, live sensors,
        or actual floor-wise energy distribution.
      </p>
    </div>
  )
}