var wms_layers = [];


        var lyr_GoogleSatellite_0 = new ol.layer.Tile({
            'title': 'Google Satellite',
            'opacity': 1.000000,
            
            
            source: new ol.source.XYZ({
            attributions: ' &middot; <a href="https://www.google.at/permissions/geoguidelines/attr-guide.html">Map data ©2015 Google</a>',
                url: 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'
            })
        });
var format_Point_counts_1 = new ol.format.GeoJSON();
var features_Point_counts_1 = format_Point_counts_1.readFeatures(json_Point_counts_1, 
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'});
var jsonSource_Point_counts_1 = new ol.source.Vector({
    attributions: ' ',
});
jsonSource_Point_counts_1.addFeatures(features_Point_counts_1);
var lyr_Point_counts_1 = new ol.layer.Vector({
                declutter: false,
                source:jsonSource_Point_counts_1, 
                style: style_Point_counts_1,
                popuplayertitle: "Point_counts",
                interactive: true,
    title: 'Point_counts<br />\
    <img src="styles/legend/Point_counts_1_0.png" /> 0 - 18<br />\
    <img src="styles/legend/Point_counts_1_1.png" /> 18 - 60<br />\
    <img src="styles/legend/Point_counts_1_2.png" /> 60 - 128<br />\
    <img src="styles/legend/Point_counts_1_3.png" /> 128 - 232<br />\
    <img src="styles/legend/Point_counts_1_4.png" /> 232 - 568<br />'
        });
var format_COMMUNE_BR_unique_2 = new ol.format.GeoJSON();
var features_COMMUNE_BR_unique_2 = format_COMMUNE_BR_unique_2.readFeatures(json_COMMUNE_BR_unique_2, 
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'});
var jsonSource_COMMUNE_BR_unique_2 = new ol.source.Vector({
    attributions: ' ',
});
jsonSource_COMMUNE_BR_unique_2.addFeatures(features_COMMUNE_BR_unique_2);
var lyr_COMMUNE_BR_unique_2 = new ol.layer.Vector({
                declutter: false,
                source:jsonSource_COMMUNE_BR_unique_2, 
                style: style_COMMUNE_BR_unique_2,
                popuplayertitle: "COMMUNE_BR_unique",
                interactive: true,
                title: '<img src="styles/legend/COMMUNE_BR_unique_2.png" /> COMMUNE_BR_unique'
            });
var lyr_Typologiedesclimatsfranais_3 = new ol.layer.Image({
                            opacity: 1,
                            title: "Typologie des climats français",
                            
                            
                            source: new ol.source.ImageStatic({
                               url: "./layers/Typologiedesclimatsfranais_3.png",
    attributions: ' ',
                                projection: 'EPSG:3857',
                                alwaysInRange: true,
                                imageExtent: [-620985.841593, 5150243.688084, 960284.595006, 6644218.298817]
                            })
                        });

lyr_GoogleSatellite_0.setVisible(true);lyr_Point_counts_1.setVisible(true);lyr_COMMUNE_BR_unique_2.setVisible(true);lyr_Typologiedesclimatsfranais_3.setVisible(true);
var layersList = [lyr_GoogleSatellite_0,lyr_Point_counts_1,lyr_COMMUNE_BR_unique_2,lyr_Typologiedesclimatsfranais_3];
lyr_Point_counts_1.set('fieldAliases', {'NOM': 'NOM', 'NUMPOINTS': 'NUMPOINTS', });
lyr_COMMUNE_BR_unique_2.set('fieldAliases', {'ID_GEOFLA': 'ID_GEOFLA', 'CODE_COM': 'CODE_COM', 'INSEE_COM': 'INSEE_COM', 'NOM_COM': 'NOM_COM', 'STATUT': 'STATUT', 'X_CHF_LIEU': 'X_CHF_LIEU', 'Y_CHF_LIEU': 'Y_CHF_LIEU', 'X_CENTROID': 'X_CENTROID', 'Y_CENTROID': 'Y_CENTROID', 'Z_MOYEN': 'Z_MOYEN', 'SUPERFICIE': 'SUPERFICIE', 'POPULATION': 'POPULATION', 'CODE_ARR': 'CODE_ARR', 'CODE_DEPT': 'CODE_DEPT', 'NOM_DEPT': 'NOM_DEPT', 'CODE_REG': 'CODE_REG', 'NOM_REG': 'NOM_REG', });
lyr_Point_counts_1.set('fieldImages', {'NOM': 'TextEdit', 'NUMPOINTS': 'TextEdit', });
lyr_COMMUNE_BR_unique_2.set('fieldImages', {'ID_GEOFLA': '', 'CODE_COM': '', 'INSEE_COM': '', 'NOM_COM': '', 'STATUT': '', 'X_CHF_LIEU': '', 'Y_CHF_LIEU': '', 'X_CENTROID': '', 'Y_CENTROID': '', 'Z_MOYEN': '', 'SUPERFICIE': '', 'POPULATION': '', 'CODE_ARR': '', 'CODE_DEPT': '', 'NOM_DEPT': '', 'CODE_REG': '', 'NOM_REG': '', });
lyr_Point_counts_1.set('fieldLabels', {'NOM': 'inline label - visible with data', 'NUMPOINTS': 'inline label - visible with data', });
lyr_COMMUNE_BR_unique_2.set('fieldLabels', {'ID_GEOFLA': 'no label', 'CODE_COM': 'no label', 'INSEE_COM': 'no label', 'NOM_COM': 'no label', 'STATUT': 'no label', 'X_CHF_LIEU': 'no label', 'Y_CHF_LIEU': 'no label', 'X_CENTROID': 'no label', 'Y_CENTROID': 'no label', 'Z_MOYEN': 'no label', 'SUPERFICIE': 'no label', 'POPULATION': 'no label', 'CODE_ARR': 'no label', 'CODE_DEPT': 'no label', 'NOM_DEPT': 'no label', 'CODE_REG': 'no label', 'NOM_REG': 'no label', });
lyr_COMMUNE_BR_unique_2.on('precompose', function(evt) {
    evt.context.globalCompositeOperation = 'normal';
});