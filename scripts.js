require([
  "esri/WebScene",
  "esri/views/SceneView",
  "esri/layers/IntegratedMesh3DTilesLayer",
  "esri/widgets/Expand",
  "esri/layers/FeatureLayer",
  "esri/widgets/LayerList",
  "esri/widgets/Legend"
], (WebScene, SceneView, IntegratedMesh3DTilesLayer, Expand, FeatureLayer, LayerList, Legend) => {
  /*************************************
   * Load webscene from ArcGIS Online
   *************************************/
  const webscene = new WebScene({
    portalItem: {
      id: "e7d41c295e844dd7a76b6d34799a30d3" // Replace with your webscene ID
    }
  });

  /*************************************
   * Create IntegratedMesh3DTilesLayer layer
   * and add it to the webscene
   ***********************************/
  const apiKey = "AIzaSyAMaPysFBi27qRN1RNqKHFq2lAbkxWlWEo"
  const google3DTilesLayer = new IntegratedMesh3DTilesLayer({
    url: `https://tile.googleapis.com/v1/3dtiles/root.json?key=${apiKey}`,
    title: "Google 3D Tiles"
  });

  webscene.add(google3DTilesLayer);

  /*************************************
   * Symbolize the 'kansai news' layer
   * using callouts
   *************************************/
  const symbol = {
    type: "point-3d", // autocasts as new PointSymbol3D()
    symbolLayers: [
      {
        type: "icon", // autocasts as new IconSymbol3DLayer()
        size: 12, // Inner size for main symbol
        resource: { primitive: "circle" },
        material: { color: "red" },
        outline: {
          color: "black",
          size: 1
        }
      }
    ],
    verticalOffset: {
      screenLength: 150, // Increase the screen length to make the leader line longer
      maxWorldLength: 750, // Increase the max world length to make the leader line longer
      minWorldLength: 150 // Increase the min world length to make the leader line longer
    },
    callout: {
      type: "line",
      color: "white",
      size: 2,
      border: {
        color: [50, 50, 50]
      }
    }
  };

  /*************************************
   * Add point layer to webscene
   *************************************/
  const kansaiNewsLayer = new FeatureLayer({
    url: "https://services1.arcgis.com/6zH0NwVwiA2oNwav/arcgis/rest/services/Kansai_News/FeatureServer",
    title: "Kansai News",
    elevationInfo: {
      mode: "relative-to-scene" // this elevation mode will place points on top of buildings or other SceneLayer 3D objects
    },
    screenSizePerspectiveEnabled: false,
    renderer: {
      type: "simple", // autocasts as new SimpleRenderer()
      symbol: symbol
    },
    popupTemplate: {
      title: "Article Content",
      content: `
        <div style="text-align: center;">
          <h2>{article_title_en}</h2>
          <p>
            <a href="{article_link}" target="_blank">
              <img style="height:auto; max-width:100%;" src="{image_link}" alt="Image not available">
            </a>
          </p>
          <p><strong>Article Summary:</strong><br>{summary_en}</p>
          <p><strong>AI Reason For Location Selection:</strong><br>{location_reason_en}</p>
        </div>
      `
    }
  });

  webscene.add(kansaiNewsLayer);

  /*************************************
   * Create the View and add expandable
   * LayerList and Legend widgets to the UI
   ***********************************/
  const view = new SceneView({
    container: "viewDiv",
    map: webscene,
    constraints: {
      altitude: {
        min: 500, // Minimum altitude in meters > 3d tile quality too low for further zoom
        max: 1000000 // Maximum altitude in meters
      }
    },
    popup: {
      dockEnabled: true,
      dockOptions: {
        buttonEnabled: true,
        breakpoint: false,
        position: "bottom-right"
      }
    }
  });

  const expandLegend = new Expand({
    content: new Legend({
      view: view
    }),
    expanded: false,
    expandTooltip: "Expand Legend",
    group: "top-right",
    view: view
  });

  const expandLayerList = new Expand({
    content: new LayerList({
      view: view
    }),
    expanded: false,
    expandTooltip: "Expand Layer List",
    group: "top-right",
    view: view
  });

  view.ui.add([expandLegend, expandLayerList], "top-right");

  /*************************************
   * Add zoom warning message
   ***********************************/
  const zoomWarning = document.createElement("div");
  zoomWarning.style.position = "absolute";
  zoomWarning.style.bottom = "20px";
  zoomWarning.style.left = "50%";
  zoomWarning.style.transform = "translateX(-50%)";
  zoomWarning.style.padding = "10px";
  zoomWarning.style.backgroundColor = "rgba(255, 0, 0, 0.8)";
  zoomWarning.style.color = "white";
  zoomWarning.style.fontSize = "14px";
  zoomWarning.style.borderRadius = "5px";
  zoomWarning.style.opacity = "0";
  zoomWarning.style.visibility = "hidden";
  zoomWarning.style.transition = "opacity 0.5s ease, visibility 0.5s ease";
  zoomWarning.innerText = "You have reached the zoom limit!";
  document.body.appendChild(zoomWarning);

  function showZoomWarning() {
    zoomWarning.style.opacity = "1";
    zoomWarning.style.visibility = "visible";
    setTimeout(() => {
      zoomWarning.style.opacity = "0";
      zoomWarning.style.visibility = "hidden";
    }, 2000);
  }

  view.watch("camera.position.z", (newValue) => {
    if (newValue < 500 || newValue > 1000000) {
      showZoomWarning();
    }
  });

  /*************************************
   * Add language toggle option
   ***********************************/
  const basemapLanguage = document.createElement("div");
  basemapLanguage.id = "basemapLanguage";
  basemapLanguage.className = "esri-widget";
  basemapLanguage.innerHTML = `
    <calcite-label style="font-size: 16px; font-weight: bold;">Language・言語</calcite-label>
    <calcite-label layout="inline">
      <calcite-radio-button value="en" checked></calcite-radio-button>
      English
    </calcite-label>
    <calcite-label layout="inline">
      <calcite-radio-button value="ja"></calcite-radio-button>
      日本語
    </calcite-label>
  `;
  document.body.appendChild(basemapLanguage);

  // Add the language toggle option to the view UI at the bottom left
  view.ui.add(basemapLanguage, "bottom-left");

  // Add event listener for radio button change
  const languageRadioGroup = document.getElementById("basemapLanguage");
  languageRadioGroup.addEventListener("calciteRadioButtonChange", (event) => {
    const selectedLanguage = event.target.value;
    const headerTitle = document.querySelector('.header');
    if (selectedLanguage === 'ja') {
      headerTitle.innerHTML = '<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/NHK_logo.svg/512px-NHK_logo.svg.png?20151101160911" /> 関西 Today';
      kansaiNewsLayer.title = "関西ニュース";
      google3DTilesLayer.title = "Google 3D タイル";
      kansaiNewsLayer.popupTemplate.content = `
        <div style="text-align: center;">
          <h2>{article_title_jp}</h2>
          <p>
            <a href="{article_link}" target="_blank">
              <img style="height:auto; max-width:100%;" src="{image_link}" alt="Image not available">
            </a>
          </p>
          <p><strong>記事の概要:</strong><br>{summary_jp}</p>
          <p><strong>場所選択のAI理由:</strong><br>{location_reason_jp}</p>
        </div>
      `;
      kansaiNewsLayer.popupTemplate.title = "記事内容";
    } else {
      headerTitle.innerHTML = '<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/NHK_logo.svg/512px-NHK_logo.svg.png?20151101160911" /> Kansai Today';
      kansaiNewsLayer.title = "Kansai News";
      google3DTilesLayer.title = "Google 3D Tiles";
      kansaiNewsLayer.popupTemplate.content = `
        <div style="text-align: center;">
          <h2>{article_title_en}</h2>
          <p>
            <a href="{article_link}" target="_blank">
              <img style="height:auto; max-width:100%;" src="{image_link}" alt="Image not available">
            </a>
          </p>
          <p><strong>Article Summary:</strong><br>{summary_en}</p>
          <p><strong>AI reason for location selection:</strong><br>{location_reason_en}</p>
        </div>
      `;
      kansaiNewsLayer.popupTemplate.title = "Article Content";
    }
    console.log("Selected language:", selectedLanguage);
    // Add your logic to handle language change here
  });
});
