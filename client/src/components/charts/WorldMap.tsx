import { MapView } from "@/components/Map";
import { Minus, Plus } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

type CountryAggregate = {
  country: string;
  value: number;
};

type CountryCoordinate = {
  lat: number;
  lng: number;
};

const COUNTRY_CENTERS: Record<string, CountryCoordinate> = {
  "Argentina": { lat: -38.4161, lng: -63.6167 },
  "Australia": { lat: -25.2744, lng: 133.7751 },
  "Bangladesh": { lat: 23.685, lng: 90.3563 },
  "Brazil": { lat: -14.235, lng: -51.9253 },
  "Canada": { lat: 56.1304, lng: -106.3468 },
  "China": { lat: 35.8617, lng: 104.1954 },
  "France": { lat: 46.2276, lng: 2.2137 },
  "Germany": { lat: 51.1657, lng: 10.4515 },
  "India": { lat: 20.5937, lng: 78.9629 },
  "Indonesia": { lat: -0.7893, lng: 113.9213 },
  "Italy": { lat: 41.8719, lng: 12.5674 },
  "Japan": { lat: 36.2048, lng: 138.2529 },
  "Mexico": { lat: 23.6345, lng: -102.5528 },
  "Netherlands": { lat: 52.1326, lng: 5.2913 },
  "Nigeria": { lat: 9.082, lng: 8.6753 },
  "Pakistan": { lat: 30.3753, lng: 69.3451 },
  "Philippines": { lat: 12.8797, lng: 121.774 },
  "Singapore": { lat: 1.3521, lng: 103.8198 },
  "South Africa": { lat: -30.5595, lng: 22.9375 },
  "South Korea": { lat: 35.9078, lng: 127.7669 },
  "Spain": { lat: 40.4637, lng: -3.7492 },
  "Sweden": { lat: 60.1282, lng: 18.6435 },
  "Switzerland": { lat: 46.8182, lng: 8.2275 },
  "United Arab Emirates": { lat: 23.4241, lng: 53.8478 },
  "United Kingdom": { lat: 55.3781, lng: -3.436 },
  "United States": { lat: 37.0902, lng: -95.7129 },
  "United States of America": { lat: 37.0902, lng: -95.7129 },
  "Vietnam": { lat: 14.0583, lng: 108.2772 },
};

function createAggregateMarker(country: string, value: number, onSelectCountry: (country: string) => void) {
  const marker = document.createElement("button");
  marker.type = "button";
  marker.className = "cs-google-country-marker";
  marker.setAttribute("aria-label", `View consented aggregate coverage for ${country}: ${value} member${value === 1 ? "" : "s"}`);
  marker.innerHTML = `<span>${value}</span><small>${country}</small>`;
  marker.addEventListener("click", () => onSelectCountry(country));
  return marker;
}

export default function ContributorAggregateMap({
  countryRows,
  onSelectCountry,
}: {
  countryRows: CountryAggregate[];
  onSelectCountry: (country: string) => void;
}) {
  const mapRef = useRef<google.maps.Map | null>(null);
  const markerRef = useRef<google.maps.marker.AdvancedMarkerElement[]>([]);
  const circleRef = useRef<google.maps.Circle[]>([]);
  const [mapReady, setMapReady] = useState(false);
  const dataSignature = useMemo(() => countryRows.map((row) => `${row.country}:${row.value}`).join("|"), [countryRows]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !window.google?.maps || !mapReady) return;

    markerRef.current.forEach((marker) => { marker.map = null; });
    circleRef.current.forEach((circle) => circle.setMap(null));
    markerRef.current = [];
    circleRef.current = [];

    const plottedRows = countryRows.filter((row) => COUNTRY_CENTERS[row.country]);
    if (!plottedRows.length) {
      map.setCenter({ lat: 19, lng: 0 });
      map.setZoom(2);
      return;
    }

    const largestValue = Math.max(...plottedRows.map((row) => row.value), 1);
    const bounds = new google.maps.LatLngBounds();
    plottedRows.forEach((row) => {
      const position = COUNTRY_CENTERS[row.country];
      bounds.extend(position);
      const intensity = row.value / largestValue;
      const circle = new google.maps.Circle({
        map,
        center: position,
        radius: 150000 + intensity * 240000,
        strokeColor: "#07845e",
        strokeOpacity: 0.6,
        strokeWeight: 1,
        fillColor: "#10b981",
        fillOpacity: 0.14 + intensity * 0.22,
        clickable: false,
      });
      circleRef.current.push(circle);
      const marker = new google.maps.marker.AdvancedMarkerElement({
        map,
        position,
        title: `${row.country}: ${row.value} consenting member${row.value === 1 ? "" : "s"}`,
        content: createAggregateMarker(row.country, row.value, onSelectCountry),
      });
      markerRef.current.push(marker);
    });
    map.fitBounds(bounds, { top: 56, right: 56, bottom: 56, left: 56 });
    window.setTimeout(() => {
      if ((map.getZoom() ?? 2) > 4) map.setZoom(4);
    }, 0);

    return () => {
      markerRef.current.forEach((marker) => { marker.map = null; });
      circleRef.current.forEach((circle) => circle.setMap(null));
    };
  }, [countryRows, dataSignature, mapReady, onSelectCountry]);

  const changeZoom = (amount: number) => {
    const map = mapRef.current;
    if (map) map.setZoom(Math.min(8, Math.max(2, (map.getZoom() ?? 2) + amount)));
  };

  return (
    <div className="cs-interactive-world-map" aria-label="Zoomable world map of consented aggregate contributor coverage">
      <MapView
        className={`cs-interactive-world-map-canvas ${countryRows.length ? "" : "is-empty"}`}
        initialCenter={{ lat: 19, lng: 0 }}
        initialZoom={2}
        onMapReady={(map) => {
          mapRef.current = map;
          map.setOptions({
            mapTypeControl: false,
            fullscreenControl: false,
            streetViewControl: false,
            zoomControl: false,
            gestureHandling: "cooperative",
            minZoom: 2,
            maxZoom: 8,
          });
          setMapReady(true);
        }}
      />
      <div className="cs-map-zoom-controls" aria-label="Map zoom controls"><button type="button" onClick={() => changeZoom(1)} aria-label="Zoom in"><Plus size={17} /></button><button type="button" onClick={() => changeZoom(-1)} aria-label="Zoom out"><Minus size={17} /></button></div>
      <p className="cs-map-privacy-label">Country-level aggregates only</p>
    </div>
  );
}
