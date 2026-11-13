import { useEffect, useMemo, useState } from 'react'
import {
  Map, MapControls, MapFillLayer, MapLineLayer, MapMarker, MarkerContent, geojsonBasemapStyle, useMap,
} from '@pgmaps/geo-toolkit/map'
import { escapeHtml } from '@pgmaps/geo-toolkit/ui'
import '@pgmaps/geo-toolkit/styles.css'
import { setWorkerUrl } from 'maplibre-gl'
import maplibreWorker from 'maplibre-gl/dist/maplibre-gl-worker.mjs?url'
import { useSiteTheme } from '../site/useTheme.js'
import { featureBounds, isInside, isSmall, padBounds } from './mapGeometry.js'

// The map's colours, per theme; the same values as the --hm-* tokens in healthStory.css, which
// MapLibre cannot read.
const PALETTE = {
  light: {
    sea: '#dfe7ea', land: '#f3f1ec', edge: '#ffffff', select: '#b4471f',
    regions: ['#9fc3b1', '#e6c27a', '#a9b8da', '#dba3a0', '#c3d48c', '#c9a9cf'],
  },
  dark: {
    sea: '#1a2226', land: '#2a2620', edge: '#161310', select: '#f0915f',
    regions: ['#3f6e58', '#85692c', '#4b5c86', '#84504c', '#66763a', '#6c4f73'],
  },
}
const OVERLAY_INK = '#b4471f'

// MapLibre 6 looks for its worker beside its own script, which a bundle does not keep; point it at
// the copy Vite emits.
setWorkerUrl(maplibreWorker)
const BC = [[-139.1, 48.2], [-114, 60]]

const regionFill = (colours) => ['match', ['coalesce', ['get', 'colour'], 0], ...colours.flatMap((colour, index) => [index, colour]), colours[0]]
const tooltip = (properties) => `<div class="hm-tip">${escapeHtml(properties.name)}</div>`

// Frames the province or the selection, and brings a newly selected area into view when it is off
// screen or too small to see; otherwise the reader's view is left alone.
function Camera({ regions, selected, command }) {
  const { map, isLoaded } = useMap()
  const all = useMemo(() => featureBounds(regions?.features ?? []) ?? BC, [regions])
  const fit = (bounds, duration = 450) => map?.fitBounds(padBounds(bounds), { padding: 24, duration, maxZoom: 9 })
  useEffect(() => { if (map && isLoaded) fit(all, 0) }, [map, isLoaded]) // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => {
    if (!map || !isLoaded || !selected) return
    const bounds = featureBounds([selected])
    if (bounds && (!isInside(bounds, map.getBounds()) || isSmall(bounds, map))) fit(bounds)
  }, [map, isLoaded, selected?.properties.id]) // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => {
    if (!command || !map || !isLoaded) return
    if (command.to === 'province') fit(all)
    else if (selected) fit(featureBounds([selected]) ?? all)
  }, [command]) // eslint-disable-line react-hooks/exhaustive-deps
  return null
}

// Map numbers (or names, where the printed map had none), placed on each area's label point.
// The offline basemap has no glyphs, so labels are markers rather than a symbol layer.
function Labels({ features, selectedId, onSelect }) {
  const { map, isLoaded } = useMap()
  const [zoom, setZoom] = useState(null)
  useEffect(() => {
    if (!map || !isLoaded) return undefined
    const update = () => setZoom(map.getZoom())
    update()
    map.on('zoomend', update)
    return () => { map.off('zoomend', update) }
  }, [map, isLoaded])
  if (zoom === null) return null
  return features.map((feature) => {
    const { id, legendNumber, name, labelPoint } = feature.properties
    if (!labelPoint) return null
    const chosen = id === selectedId
    // Small areas get a label once they are big enough on screen to hold one.
    if (!chosen && !legendNumber && isSmall(featureBounds([feature]), map, 40)) return null
    return <MapMarker key={id} longitude={labelPoint[0]} latitude={labelPoint[1]} onClick={() => onSelect(id)}>
      <MarkerContent><span className={`hm-marker${legendNumber ? ' is-number' : ''}${chosen ? ' is-selected' : ''}`}>{legendNumber ?? name}</span></MarkerContent>
    </MapMarker>
  })
}

// Province map for one historical framework, drawn with geo-toolkit (MapLibre) on an offline
// basemap built from the province outline. Region shapes come from the boundary files; the
// optional overlay is the printed source map, georectified.
export function HealthAtlasMap({ base, regions, overlay, overlayOpacity = .75, selectedId, onSelect, frameworkLabel }) {
  const { name: theme } = useSiteTheme()
  const palette = PALETTE[theme] ?? PALETTE.light
  const styles = useMemo(() => {
    const style = (colours) => geojsonBasemapStyle({ land: base, water: colours.sea, landColor: colours.land, borderWidth: 0 })
    return { light: style(PALETTE.light), dark: style(PALETTE.dark) }
  }, [base])
  const features = regions?.features ?? []
  const selected = features.find((feature) => feature.properties.id === selectedId) ?? null
  const [command, setCommand] = useState(null)
  const [failed, setFailed] = useState(false)
  const overlayOn = Boolean(overlay?.features?.length)

  if (failed) {
    return <div className="hm-map hm-map--failed" role="alert">
      <p>This browser could not start the map (it needs WebGL). The list below and the downloads still work.</p>
    </div>
  }

  return <div className="hm-map">
    <div className="hm-map-tools" role="group" aria-label="Map view">
      <button type="button" onClick={() => setCommand({ to: 'province', at: Date.now() })}>Province</button>
      <button type="button" disabled={!selected} onClick={() => setCommand({ to: 'selection', at: Date.now() })}>Selected area</button>
    </div>
    <Map
      className="hm-gl"
      theme={theme}
      styles={styles}
      bounds={BC}
      minZoom={3}
      maxZoom={11}
      attributionControl={false}
      rtlTextPlugin={false}
      showLoadingOverlay={false}
      onCreateError={() => setFailed(true)}
      containerProps={{ role: 'region', 'aria-label': `${frameworkLabel} map of British Columbia` }}
      controls={<MapControls position="top-right" showZoom showCompass={false} showLocate={false} showFullscreen={false} />}
    >
      {overlayOn && <>
        <MapFillLayer
          data={overlay}
          filter={['!=', ['get', 'kind'], 'line']}
          fillColor={['case', ['==', ['get', 'kind'], 'water'], '#bfe7f2', ['coalesce', ['get', 'fill'], '#cdcdcd']]}
          fillOpacity={overlayOpacity}
          lineWidth={0}
          layerOrder={1}
          idProperty="kind"
        />
        <MapLineLayer data={overlay} filter={['==', ['get', 'kind'], 'line']} color="#222222" width={.6} opacity={overlayOpacity} layerOrder={2} interactive={false} />
      </>}
      <MapFillLayer
        data={regions}
        idProperty="id"
        layerOrder={3}
        fillColor={overlayOn ? palette.select : regionFill(palette.regions)}
        fillOpacity={overlayOn ? 0 : 1}
        hoverFillOpacity={overlayOn ? .15 : .7}
        lineColor={overlayOn ? OVERLAY_INK : palette.edge}
        lineWidth={overlayOn ? 1.2 : 1}
        lineOpacity={1}
        selectedId={selectedId ?? null}
        selectionStyle="line"
        selectionColor={palette.select}
        selectionWidth={2.5}
        sourceKey="hm-regions"
        hoverHtml={tooltip}
        onFeatureClick={(id) => onSelect(String(id))}
      />
      {/* The selected area in the highlight colour. A 'fill' selection style would reuse the
          regions' own colours, so the highlight is its own layer over the same source. */}
      <MapFillLayer
        data={regions}
        idProperty="id"
        sourceKey="hm-regions"
        layerOrder={4}
        filter={['==', ['get', 'id'], selectedId ?? '']}
        fillColor={palette.select}
        fillOpacity={overlayOn ? .3 : .82}
        hoverFillOpacity={overlayOn ? .3 : .82}
        lineWidth={0}
        onFeatureClick={(id) => onSelect(String(id))}
      />
      <Labels features={features} selectedId={selectedId} onSelect={onSelect} />
      <Camera regions={regions} selected={selected} command={command} />
    </Map>
    <div className="hm-readout" aria-live="polite">{selected?.properties.name ?? 'Select an area on the map'}</div>
  </div>
}

export default HealthAtlasMap
