import React, { useState, useRef, useEffect } from 'react';
import 'mapbox-gl/dist/mapbox-gl.css'
import mapboxgl, { GeoJSONFeature, GeoJSONSource } from 'mapbox-gl';
import './mapbox.scss'
import { FaMap } from "react-icons/fa";
import { FaMapPin } from "react-icons/fa6";
import { MdFullscreen, MdFullscreenExit, MdKeyboardArrowUp, MdKeyboardArrowDown, MdOutlineClose, MdOutlineDelete } from "react-icons/md";
import { TRANSACTION_POINT_SOURCE_ID, TRANSACTION_POINT_SOURCE_SETTINGS,
    DEFAULT_DATA, TRANSACTION_POINT_LAYER_ID, createTransactionMarker, TRANSACTION_POINT_CLUSTER_TEXT_LAYER_ID, 
    TRANSACTION_POINT_CLUSTER_CIRCLE_LAYER_ID, TRANSACTION_POINT_DOT_LAYER_ID,
    TRANSACTION_POINT_BASE_FILTER, TRANSACTION_POINT_CLUSTER_BASE_FILTER, createNewTransactionMarker
  } from './mapboxConfig';
import './env.d.ts'
import { useTheme } from './theme-context.tsx'
import dayjs from 'dayjs';
import advancedFormat from "dayjs/plugin/advancedFormat";



dayjs.extend(advancedFormat);
mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN

interface MapboxProps {
    selectedTransaction: any | null;
    setSelectedTransaction: (transaction: any, options?: {updateFlag?: boolean, deleteFlag?: boolean}) => void;
    transactionData: any[];
    setFullscreenMap: (v: boolean | any) => void;
    fullscreenMap: boolean;
}


function mapbox(props: MapboxProps) {
  const mapContainerRef = useRef<HTMLDivElement | null>(null)
  const mapRef = useRef<mapboxgl.Map | null>(null)
  const styleReadyRef = useRef(false);
  const pinMarkerRef = useRef<mapboxgl.Marker | null>(null);
  const activeId = useRef<number | null>(null);
  const [acceptanceData, setAcceptanceData] = useState<{lng:number,lat:number} | null>(null);
  const geojsonRef = useRef<GeoJSON.FeatureCollection>(DEFAULT_DATA);
  const { theme } = useTheme();
  const {
    selectedTransaction, 
    setSelectedTransaction: setSelectedTransaction, 
    transactionData,
    setFullscreenMap,
    fullscreenMap
  } = props
  const selectedTransactionRef = useRef(selectedTransaction);

  //Modals
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [stylePanelOpen, setStylePanelOpen] = useState(false)
  const [detailPanelOpen, setDetailPanelOpen] = useState(false)
  const [mobileDetailPanelMinimised, setMobileDetailPanelMinimised] = useState(true)

  //Map style configs
  const [mapSize, setMapSize] = useState('small')
  const [timeOfDay, setTimeOfDay] = useState<'day' | 'dusk' | 'night'>(theme == 'dark' ? 'night' : 'day')
  const [mapStyle, setMapStyle] = useState('standard')
  const [poiLabelVisible, setPOILabelVisible] = useState(true)
  const [placeLabelVisible, setPlaceLabelVisible] = useState(true)
  const [roadLabelVisible, setRoadLabelVisible] = useState(true)
  const [transitLabelVisible, setTransitLabelVisible] = useState(true)

  const loadSources = (map: mapboxgl.Map) => { //Load default sources
    map.addSource(TRANSACTION_POINT_SOURCE_ID, {
        ...TRANSACTION_POINT_SOURCE_SETTINGS,
        data: DEFAULT_DATA
    })
  }

  const loadLayers = (map: mapboxgl.Map, isDark: boolean) => { // Load layers
    map.addLayer({
        id: TRANSACTION_POINT_CLUSTER_CIRCLE_LAYER_ID,
        type: 'circle',
        source: TRANSACTION_POINT_SOURCE_ID,
        filter: TRANSACTION_POINT_CLUSTER_BASE_FILTER,
        paint: {
            'circle-color': '#9ca3af',
            'circle-opacity': 0.5,
            'circle-radius': [
                'interpolate',
                ['linear'],
                ['zoom'],
                10, 18,
                18, 14
            ],
            'circle-stroke-width': 3,
            'circle-emissive-strength': 1,
            'circle-stroke-color': [
                'case',
                ['boolean', isDark, false],
                '#ffffff',
                '#000000'
            ],
            'circle-stroke-opacity': 1,
            'circle-pitch-alignment': 'map'
        }
    });

    map.addLayer({
        id: TRANSACTION_POINT_CLUSTER_TEXT_LAYER_ID,
        type: 'symbol',
        source: TRANSACTION_POINT_SOURCE_ID,
        filter: TRANSACTION_POINT_CLUSTER_BASE_FILTER,
        layout: {
            'text-field': '{point_count_abbreviated}', // shorthand like 1.2k
            'text-font': ['Inter Bold', 'Arial Unicode MS Bold'],
            'text-size': 14,
            'text-allow-overlap': true
        },
        paint: {
            'text-color': [
                'case',
                ['boolean', isDark, false],
                '#ffffff',
                '#000000'
            ],
            'text-halo-blur': 0
        }
    });

    map.addLayer({
        id: TRANSACTION_POINT_DOT_LAYER_ID,
        type: 'circle',
        source: TRANSACTION_POINT_SOURCE_ID,
        filter: TRANSACTION_POINT_BASE_FILTER,
        maxzoom: 13,
        paint: {
            'circle-color': [
                'case',
                ['!=',['get','colour'],'null'],
                ['get','colour'],
                '#9ca3af'
            ],
            'circle-opacity': 0.5,
            'circle-radius': 3,
            'circle-stroke-width': 1,
            'circle-emissive-strength': 1,
            'circle-stroke-color': [
                'case',
                ['boolean', isDark, false],
                '#ffffff',
                '#000000'
            ],
            'circle-stroke-opacity': 1,
            'circle-pitch-alignment': 'map',
            'circle-translate': [0,-5]
        }
    });

    map.addLayer({
        id: TRANSACTION_POINT_LAYER_ID,
        type: "symbol",
        filter: TRANSACTION_POINT_BASE_FILTER,
        source: TRANSACTION_POINT_SOURCE_ID,
        minzoom: 13,
        layout: {
            'icon-image': [
                'case',
                ['==', ['get', 'active'], true],
                ['concat', ['get', 'icon'], '-active'],
                ['get', 'icon']
            ],
            'icon-allow-overlap': true,
            'icon-anchor': 'bottom',
            'icon-size': [
                'case',
                ['get','active'],
                1.5,
                1
            ]
            
        }
    })
  }

  const createTransactionFeatures = ( // Create features and update source
    map: mapboxgl.Map,
    transactionData: any[]
  ) => {
    if (!map || !transactionData) return


    let features: GeoJSON.Feature[] = []
    let points: GeoJSON.Feature[] = []

    transactionData.forEach(item => {
        if (!item.latitude || !item.longitude || !item.transactionID) return
        features.push({
            type: "Feature",
            id: item.transactionID,
            properties: {
                active: false,
                transactionID: item.transactionID,
                icon: `tx-${item.transactionID}`,
                amount: item.amount,
                title: item.title,
                categoryID: item.categoryID,
                details: item.details,
                particulars: item.particulars,
                code: item.code,
                reference: item.reference,
                date: item.date,
                type: item.type,
                colour: item.colour,
                hasCoordinates: item.longitude != null && item.latitude != null
            },
            geometry: {
                type: "Point",
                coordinates: [item.longitude, item.latitude]
            }
        })
    })

    points = features.filter(f => f.geometry.type === "Point")

    const pointSource: GeoJSONSource | undefined = map.getSource(TRANSACTION_POINT_SOURCE_ID)
    const data: GeoJSON.FeatureCollection = {
        type: "FeatureCollection",
        features: points,
    }
    pointSource?.setData(data)
    geojsonRef.current = data
  }

    async function loadTransactionImages( // Create icons
    map: mapboxgl.Map,
    transactions: any[]
    ) {
    for (const tx of transactions) {

        const imageId = `tx-${tx.transactionID}`
        if (map.hasImage(imageId)) return

        const colour = tx.colour ?? '#6b7280';
        const canvas = createTransactionMarker(colour);
        const bitmap = await createImageBitmap(canvas);
        const activeCanvas = createTransactionMarker(colour, true);
        const activeBitmap = await createImageBitmap(activeCanvas);

        map.addImage(imageId, bitmap, { pixelRatio: 2 });
        map.addImage(imageId+'-active', activeBitmap, { pixelRatio: 2 });

    }
    }

    const loadMapManager = (map: mapboxgl.Map) => { // Register map event listners

    map.on("mousemove", TRANSACTION_POINT_LAYER_ID, (e) => {
    if (!e.features?.length) return;
    const featureId = e.features[0].id as number;

    const source = map.getSource(TRANSACTION_POINT_SOURCE_ID) as GeoJSONSource;
    if (!source) return;

    const data = geojsonRef.current;
    data.features.forEach(f => {
        if (f.id == activeId.current) return
        f.properties!.active = f.id === featureId;
    });

    source.setData(data);
    });


    map.on("mouseleave", TRANSACTION_POINT_LAYER_ID, () => {
    const source = map.getSource(TRANSACTION_POINT_SOURCE_ID) as GeoJSONSource;
    if (!source) return;

    const data = geojsonRef.current;
    data.features.forEach(f => {
        if (f.id == activeId.current) return
        f.properties!.active = false;
    });

    source.setData(data);
    });


    map.on("click", TRANSACTION_POINT_LAYER_ID, (e) => {
        e.preventDefault()
        if (!e.features?.length) return;
        const feature = e.features[0]
        const id = feature.id as number;
        if (activeId.current === id) {
            resetSelectedTransaction()
        } else{
            const geo = (feature.geometry as GeoJSON.Point).coordinates
             // No delay over resetting selected transaction
            // if (selectedTransactionRef.current) loadTransactionImages(map,[selectedTransactionRef.current],false)
            setSelectedTransaction({...feature.properties, longitude:geo[0], latitude:geo[1]})
        }
    });

    map.on('click', TRANSACTION_POINT_CLUSTER_CIRCLE_LAYER_ID, (e) => {
        const features = map.queryRenderedFeatures(e.point, {
            layers: [TRANSACTION_POINT_CLUSTER_CIRCLE_LAYER_ID],
        });

        if (!features.length) return;

        const cluster = features[0];
        const clusterId = cluster.properties?.cluster_id;

        const source = map.getSource(
            TRANSACTION_POINT_SOURCE_ID
        ) as mapboxgl.GeoJSONSource;

        source.getClusterExpansionZoom(clusterId, (err, zoom) => {
            if (err || zoom === null) return;

            map.easeTo({
            center: (cluster.geometry as GeoJSON.Point).coordinates as [number, number],
            zoom,
            duration: 800,
            });
        });
    });

    map.on('mouseenter', TRANSACTION_POINT_CLUSTER_CIRCLE_LAYER_ID, () => {
        map.getCanvas().style.cursor = 'pointer';
        map.setPaintProperty(TRANSACTION_POINT_CLUSTER_CIRCLE_LAYER_ID,'circle-opacity',0.7)
    });
    map.on('mouseleave', TRANSACTION_POINT_CLUSTER_CIRCLE_LAYER_ID, () => {
        map.getCanvas().style.cursor = '';
        map.setPaintProperty(TRANSACTION_POINT_CLUSTER_CIRCLE_LAYER_ID,'circle-opacity',0.5)
    });

    };

    useEffect(() => { // Transaction data incoming
    const map = mapRef.current;
    if (!map || !styleReadyRef.current) return;

    const source = map.getSource(
        TRANSACTION_POINT_SOURCE_ID
    ) as GeoJSONSource | undefined;

    if (!source) return;

    createTransactionFeatures(map, transactionData);
    loadTransactionImages(map, transactionData)
    }, [transactionData]);

    useEffect(() => { // Create map
    if (!mapContainerRef.current || mapRef.current) return;

    const map = new mapboxgl.Map({
        container: mapContainerRef.current,
        style: 'mapbox://styles/mapbox/standard',
        center: [174.7633, -36.8485],
        zoom: 13,
    });

    map.addControl(new mapboxgl.NavigationControl(), 'top-right');
    mapRef.current = map;

    return () => {
        map.remove();
        mapRef.current = null;
    };
    }, []);

    useEffect(() => { // Load map config on style load
    const map = mapRef.current;
    if (!map) return;

    styleReadyRef.current = false;

    const onStyleLoad = async () => {
        await loadTransactionImages(map, transactionData);
        const isDark = mapStyle === 'standard' &&
         (timeOfDay === 'night' || timeOfDay === 'dusk')

        loadSources(map);
        loadLayers(map, isDark);
        loadMapManager(map); // Only call once
        createTransactionFeatures(map, transactionData);

        if (mapStyle === 'standard') {
        map.setConfigProperty('basemap', 'lightPreset', timeOfDay);
        map.setConfigProperty('basemap', 'showPointOfInterestLabels', poiLabelVisible);
        }

        styleReadyRef.current = true;
    };

    map.once('style.load', onStyleLoad);
    map.setStyle(`mapbox://styles/mapbox/${mapStyle}`);

    return () => {
        map.off('style.load', onStyleLoad);
    };
    }, [mapStyle]);

    useEffect(() => { // Update map styles
    const map = mapRef.current;
    if (!map || mapStyle !== 'standard') return;
    const isDark = timeOfDay === 'night' || timeOfDay === 'dusk';

    const apply = () => {
        map.setConfigProperty('basemap', 'lightPreset', timeOfDay);
        map.setConfigProperty('basemap', 'showPointOfInterestLabels', poiLabelVisible);
        map.setConfigProperty('basemap', 'showRoadLabels', roadLabelVisible);
        map.setConfigProperty('basemap', 'showPlaceLabels', placeLabelVisible);
        map.setConfigProperty('basemap', 'showTransitLabels', transitLabelVisible);

        if (!map.getLayer(TRANSACTION_POINT_CLUSTER_TEXT_LAYER_ID) ||
            !map.getLayer(TRANSACTION_POINT_CLUSTER_CIRCLE_LAYER_ID) ||
            !map.getLayer(TRANSACTION_POINT_DOT_LAYER_ID)
        ) return
        map.setPaintProperty(TRANSACTION_POINT_CLUSTER_TEXT_LAYER_ID,'text-color',isDark ? '#ffffff' : '#000000');
        map.setPaintProperty(TRANSACTION_POINT_CLUSTER_TEXT_LAYER_ID,'text-halo-color',isDark ? '#000000' : 'rgba(0,0,0,0)');
        map.setPaintProperty(TRANSACTION_POINT_CLUSTER_TEXT_LAYER_ID,'text-halo-width',isDark ? 1.25 : 0);
        map.setPaintProperty(TRANSACTION_POINT_CLUSTER_CIRCLE_LAYER_ID,'circle-stroke-color',isDark ? '#ffffff' : '#000000');
        map.setPaintProperty(TRANSACTION_POINT_DOT_LAYER_ID,'circle-stroke-color', isDark ? '#ffffff' : '#000000');
    };

    styleReadyRef.current ? apply() : map.once('style.load', apply);
    }, [mapStyle, timeOfDay, poiLabelVisible, placeLabelVisible, roadLabelVisible, transitLabelVisible]);

    function addDraggablePin(map: mapboxgl.Map) { // Add a pin to place transaction
        // Remove existing pin
        pinMarkerRef.current?.remove();
        setDetailPanelOpen(false)

        const el = createNewTransactionMarker()

        const marker = new mapboxgl.Marker({
            element: el,
            draggable: true,
            anchor: 'bottom'
        })
            .setLngLat(map.getCenter())
            .addTo(map);
        
        map.flyTo({
            center: map.getCenter(),
            zoom: 14,
            duration: 1000
        })

        marker.on("dragstart", () => {
            setIsConfirmOpen(false)
        });

        marker.on("dragend", () => {
            const { lng, lat } = marker.getLngLat();
            setAcceptanceData({
                lng: lng,
                lat: lat
            })
            setIsConfirmOpen(true)
        });

        pinMarkerRef.current = marker;
    }

    function onPinDropped( // Update API and page data
        map: mapboxgl.Map,
        status: boolean,
        data: {lng:number, lat: number},
        ) {
        if (status) {
            const [lng, lat] = [data.lng, data.lat]
            const updatedTransaction = { ...selectedTransaction, longitude: lng, latitude: lat };
            setSelectedTransaction(updatedTransaction, {updateFlag: true});
        } 
        // remove draggable marker
        pinMarkerRef.current?.remove();
        pinMarkerRef.current = null;
    }

    const validatePlacement = (status: boolean) => { // Confirm pin position
        const map = mapRef.current
        if (!map) return
        setIsConfirmOpen(false)
        onPinDropped(map, status, acceptanceData!)
    }

    const resetSelectedTransaction = (feature: GeoJSONFeature | null = null) => {
        const map = mapRef.current
        if (!map) return
        activeId.current = null
        setDetailPanelOpen(false)
        // loadTransactionImages(map,[feature ? feature?.properties : selectedTransactionRef.current],false)
        setSelectedTransaction(null)
    }

    const updateSelectedTransaction = () => {
        const map = mapRef.current
        if (!map) return
        addDraggablePin(map)
    }

    useEffect(() => { // Active styles
    const map = mapRef.current;
    if (!map) return;
    selectedTransactionRef.current = selectedTransaction;
    
    // Stop any ongoing placement

    if (pinMarkerRef.current) {
        setIsConfirmOpen(false)
        pinMarkerRef.current.remove()
        setAcceptanceData(null)
        pinMarkerRef.current = null
    }
    
    //Set active or reset transaction

    const source = map.getSource(
        TRANSACTION_POINT_SOURCE_ID
    ) as GeoJSONSource;

    if (!source) return;

    const data = geojsonRef.current;
    activeId.current = selectedTransaction?.transactionID
    data.features.forEach(f => {
        f.properties!.active = f.id === selectedTransaction?.transactionID;
    });

    source.setData(data);

    if (selectedTransaction && (selectedTransaction.longitude===null ||
        selectedTransaction.latitude===null)
    ) {
        addDraggablePin(mapRef.current!)
        return
    }

    if (!selectedTransaction) return // Dont progress if a reset process
    setDetailPanelOpen(true)

    //Fly if not in current view
    if (map.getBounds()?.contains([selectedTransaction.longitude,selectedTransaction.latitude])) return

    if (!styleReadyRef.current) {
        // Wait once, then fly
        const onStyleLoad = () => {
        styleReadyRef.current = true;
        map.flyTo({
            center: [
            selectedTransaction.longitude,
            selectedTransaction.latitude,
            ],
            zoom: 14,
            duration: 1000,
        });
        };

        map.once('style.load', onStyleLoad);
        return;
    }

    // Style is already ready → fly immediately
    map.flyTo({
        center: [
        selectedTransaction.longitude,
        selectedTransaction.latitude,
        ],
        zoom: 14,
        duration: 1000,
    });

    // Open detail panel
    }, [selectedTransaction]);

    useEffect(() => { // Rerender map on container size change
    const map = mapRef.current;
    if (!map) return;

    requestAnimationFrame(() => {
        map.resize();
    });
    }, [fullscreenMap]);

    useEffect(() => {
        if (mapStyle === 'standard') setTimeOfDay(theme == 'dark' ? 'night' : 'day')
    }, [theme])

  return (
    <div className={`map-wrapper ${mapSize}` }>
    <div ref={mapContainerRef} className="map" />

        <div className='map-panel'>
            <div className='map-actions'>
                <div className="map-style-control">
                    <button
                    className="map-button"
                    onClick={() => setStylePanelOpen(v => !v)}
                    >
                    <FaMap/>
                    </button>
                </div>

                <div className="map-fullscreen-control">
                    <button
                        className="map-button"
                        onClick={() => {
                            setFullscreenMap((v: boolean) => !v)
                        }}
                        >
                        {fullscreenMap ? <MdFullscreenExit />: <MdFullscreen />}
                    </button>
                </div>
            </div>

            {stylePanelOpen && (
                <div className="map-style-panel">
                    <p>Map style</p>
                    <div className="section">
                    {[
                        ['standard', 'Standard'],
                        ['streets-v12', 'Streets'],
                        ['outdoors-v12', 'Outdoors'],
                        ['satellite-streets-v12', 'Satellite'],
                    ].map(([value, label]) => (
                        <label key={value}>
                        <input
                            type="radio"
                            name="style"
                            checked={mapStyle === value}
                            onChange={() => setMapStyle(value)}
                        />
                        <p className={mapStyle === value ? "active" : ""}>{label}</p>
                        </label>
                    ))}
                    </div>

                    {mapStyle === 'standard' && (
                    <>
                        <p>Time of day</p>
                        <div className="section">
                        {[
                            ['day', 'Day'],
                            ['dusk', 'Dusk'],
                            ['night', 'Night']
                        ].map(([value, label]) => (
                            <label key={value}>
                            <input
                                type="radio"
                                name="time"
                                checked={timeOfDay === value}
                                onChange={() => setTimeOfDay(value as any)}
                            />
                            <p className={timeOfDay === value ? "active" : ""}>{label}</p>
                            </label>
                        ))}
                        </div>
                    </>
                    )}
                    
                    <div className='switch-section'>
                        <div>
                            <p>POI labels</p>
                            <label className="switch">
                            <input type='checkbox' checked={poiLabelVisible} onChange={() => setPOILabelVisible(!poiLabelVisible)}></input>
                                <span className="slider round"></span>
                            </label>
                        </div>
                        <div>
                            <p>Road labels</p>
                            <label className="switch">
                            <input type='checkbox' checked={roadLabelVisible} onChange={() => setRoadLabelVisible(!roadLabelVisible)}></input>
                                <span className="slider round"></span>
                            </label>
                        </div>
                        <div>
                            <p>Place labels</p>
                            <label className="switch">
                            <input type='checkbox' checked={placeLabelVisible} onChange={() => setPlaceLabelVisible(!placeLabelVisible)}></input>
                                <span className="slider round"></span>
                            </label>
                        </div>
                        <div>
                            <p>Transit labels</p>
                            <label className="switch">
                            <input type='checkbox' checked={transitLabelVisible} onChange={() => setTransitLabelVisible(!transitLabelVisible)}></input>
                                <span className="slider round"></span>
                            </label>
                        </div>
                    </div>
                </div>
            )}
        </div>

        {isConfirmOpen && (
            <div className="map-confirm-panel">
                <p className='title'>Confirm Placement</p>
                <div className='help'>
                <p>Press confirm to update transaction</p>
                <p>Press cancel to stop placement</p>
                </div>

                <div className="actions">
                <button onClick={() => {
                    validatePlacement(false)
                }}>Cancel</button>
                <button className="primary" onClick={() => {
                    validatePlacement(true)
                }}>
                    Confirm
                </button>
                </div>
            </div>
        )}

        {detailPanelOpen && selectedTransaction && (
            <div className={`map-detail-panel ${mobileDetailPanelMinimised ? 'min' : ''}`}>
                <div className='buttons'>
                    <button onClick={() => resetSelectedTransaction()}>
                        <MdOutlineClose />
                    </button>
                    <button className="minimise" onClick={() => setMobileDetailPanelMinimised(!mobileDetailPanelMinimised)}>
                        {mobileDetailPanelMinimised ? <MdKeyboardArrowUp /> : <MdKeyboardArrowDown/> }
                    </button>
                </div>
                <p className='amount'>{selectedTransaction.amount}</p>
                <div className='section'>
                <p className='title'>{selectedTransaction.title}</p>
                <p className='date'>{dayjs(selectedTransaction.date).format("dddd Do MMMM YYYY")}</p>
                </div>
                <div className='section trans-details'>
                    {selectedTransaction.type && (
                        <>
                            <p className='info'>Type</p>
                            <p className='type'>{selectedTransaction.type}</p>
                        </>
                    )}
                    {selectedTransaction.details && (
                        <>
                            <p className='info'>Details</p>
                            <p className='details'>{selectedTransaction.details}</p>
                        </>
                    )}
                    {selectedTransaction.particulars && (
                        <>
                            <p className='info'>Particulars</p>
                            <p className='particulars'>{selectedTransaction.particulars}</p>
                        </>
                    )}
                    {selectedTransaction.reference && (
                        <>
                            <p className='info'>Reference</p>
                            <p className='reference'>{selectedTransaction.reference}</p>
                        </>
                    )}
                    <div className='update-buttons'>
                        <button className='delete' onClick={() => {
                                setSelectedTransaction(selectedTransaction, {deleteFlag: true})
                            }}>
                            Delete <MdOutlineDelete />
                        </button>
                        <button className='delete' onClick={() => {
                                updateSelectedTransaction()
                            }}>
                            Update <FaMapPin />
                        </button>
                    </div>
                </div>
            </div>
        )}
    </div>
  )
}

export default mapbox