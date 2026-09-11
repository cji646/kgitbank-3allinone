"use strict";

var searchResultGroup = L.layerGroup().addTo(map);

var categoryIcons = {
  hospital: L.icon({
    iconUrl: "/map/icons/hospital.png",
    iconSize: [36, 36],
    iconAnchor: [18, 36],
    popupAnchor: [0, -34]
  }),

  police: L.icon({
    iconUrl: "/map/icons/police.png",
    iconSize: [36, 36],
    iconAnchor: [18, 36],
    popupAnchor: [0, -34]
  }),

  fire_station: L.icon({
    iconUrl: "/map/icons/fire%20station.png",
    iconSize: [36, 36],
    iconAnchor: [18, 36],
    popupAnchor: [0, -34]
  }),

  pharmacy: L.icon({
    iconUrl: "/map/icons/pharmacy.png",
    iconSize: [36, 36],
    iconAnchor: [18, 36],
    popupAnchor: [0, -34]
  })
};

async function showCategoryInView(category, label) {

  searchResultGroup.clearLayers();

  var bounds = map.getBounds();

  var south = bounds.getSouth();
  var west = bounds.getWest();
  var north = bounds.getNorth();
  var east = bounds.getEast();

  var query =
    '[out:json][timeout:25];' +
    '(' +
      'node["amenity"="' + category + '"](' +
        south + ',' + west + ',' + north + ',' + east +
      ');' +
      'way["amenity"="' + category + '"](' +
        south + ',' + west + ',' + north + ',' + east +
      ');' +
      'relation["amenity"="' + category + '"](' +
        south + ',' + west + ',' + north + ',' + east +
      ');' +
    ');' +
    'out center tags;';

  try {

    var response = await fetch(
      "/map/overpass.php",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          query: query
        })
      }
    );

    var data = await response.json();

    var elements = data.elements || [];

    for (var i = 0; i < elements.length; i++) {

      var item = elements[i];

      var lat =
        item.lat ||
        (item.center && item.center.lat);

      var lon =
        item.lon ||
        (item.center && item.center.lon);

      if (!lat || !lon) {
        continue;
      }

var language =
  localStorage.getItem("language") || "ko";

var name =
  (item.tags && (
    item.tags["name:" + language] ||
    item.tags.name
  )) ||
  label;

      L.marker(
        [lat, lon],
        {
          icon: categoryIcons[category]
        }
      )
      .addTo(searchResultGroup)
      .bindPopup(name);
    }

  } catch (e) {

alert(
  label + " - " +
  getTranslation("mapLoadError")
);

  }
}

function createFacilityControls() {

  var mapWrapper =
    document.getElementById("map-wrapper") ||
    document.getElementById("map");

  if (!mapWrapper) {
    return;
  }

  var oldControls =
    document.getElementById("emergency-facility-controls");

  if (oldControls) {
    oldControls.parentNode.removeChild(oldControls);
  }

  var controls = document.createElement("div");

  controls.id = "emergency-facility-controls";

  controls.style.position = "absolute";
  controls.style.right = "10px";
  controls.style.bottom = "55px";
  controls.style.zIndex = "10000";
  controls.style.width = "135px";

  function makeButton(id, icon, translationKey, category) {

    var button = document.createElement("button");

    button.id = id;
    button.type = "button";

    button.style.display = "block";
    button.style.width = "100%";
    button.style.marginBottom = "3px";
    button.style.padding = "8px 6px";
    button.style.border = "1px solid #bbbbbb";
    button.style.borderRadius = "5px";
    button.style.background = "#ffffff";
    button.style.color = "#111111";
    button.style.fontSize = "12px";
    button.style.fontWeight = "600";
    button.style.cursor = "pointer";
    button.style.boxSizing = "border-box";

    button.innerHTML =
      icon + " " + getTranslation(translationKey);

    button.addEventListener(
      "click",
      function() {
        showCategoryInView(
          category,
          getTranslation(translationKey)
        );
      }
    );

    controls.appendChild(button);
  }

  makeButton(
    "btn-hospital",
    "🏥",
    "mapHospital",
    "hospital"
  );

  makeButton(
    "btn-police",
    "🚔",
    "mapPolice",
    "police"
  );

  makeButton(
    "btn-fire",
    "🚒",
    "mapFireStation",
    "fire_station"
  );

  makeButton(
    "btn-pharmacy",
    "💊",
    "mapPharmacy",
    "pharmacy"
  );

  mapWrapper.appendChild(controls);
}

createFacilityControls();
