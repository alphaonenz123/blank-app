import streamlit as st
import folium
from folium.plugins import Draw, MousePosition, MarkerCluster
from streamlit_folium import folium_static
import io
import uuid
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import base64
import time

def add_text_to_map(m):
    js = """
    var text = L.control({position: 'topright'});
    text.onAdd = function (map) {
        var div = L.DomUtil.create('div', 'info');
        div.innerHTML = '<input type="text" id="textInput" placeholder="Enter text">' +
                        '<button onclick="addText()">Add Text</button>';
        return div;
    };
    text.addTo(map);

    function addText() {
        var input = document.getElementById('textInput');
        var text = input.value;
        if (text) {
            var center = map.getCenter();
            L.marker(center, {
                icon: L.divIcon({
                    className: 'text-label',
                    html: text,
                    iconSize: [100, 40]
                })
            }).addTo(map);
            input.value = '';
        }
    }

    map.on('click', function(e) {
        var text = prompt("Enter text for this location:");
        if (text) {
            L.marker(e.latlng, {
                icon: L.divIcon({
                    className: 'text-label',
                    html: text,
                    iconSize: [100, 40]
                })
            }).addTo(map);
        }
    });
    """
    m.get_root().html.add_child(folium.Element(js))

def add_location_button(m):
    js = """
    L.Control.LocationButton = L.Control.extend({
        onAdd: function(map) {
            var btn = L.DomUtil.create('button', 'location-button');
            btn.innerHTML = 'My Location';
            btn.style.backgroundColor = 'white';
            btn.style.padding = '5px';
            btn.style.border = '2px solid #ccc';
            btn.style.borderRadius = '4px';
            btn.onclick = function() {
                map.locate({setView: true, maxZoom: 16});
            };
            return btn;
        }
    });
    L.control.locationButton = function(opts) {
        return new L.Control.LocationButton(opts);
    }
    L.control.locationButton({ position: 'topleft' }).addTo(map);

    map.on('locationfound', function(e) {
        var radius = e.accuracy / 2;
        L.marker(e.latlng).addTo(map)
            .bindPopup("You are within " + radius + " meters from this point").openPopup();
        L.circle(e.latlng, radius).addTo(map);
    });

    map.on('locationerror', function(e) {
        alert(e.message);
    });
    """
    m.get_root().html.add_child(folium.Element(js))

def add_contours(m):
    # This is a simplified example. In a real-world scenario, you'd use actual contour data.
    contour_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"elevation": 100},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[-5, 40], [5, 40]]
                }
            },
            {
                "type": "Feature",
                "properties": {"elevation": 200},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[-5, 45], [5, 45]]
                }
            }
        ]
    }
    
    folium.GeoJson(
        contour_data,
        name="Contours",
        style_function=lambda feature: {
            "color": "red",
            "weight": 2,
            "opacity": 0.7
        }
    ).add_to(m)

def geocode_address(address):
    url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
        return None
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error connecting to geocoding service: {str(e)}")
    except (KeyError, IndexError, ValueError) as e:
        raise Exception(f"Error parsing geocoding response: {str(e)}")

def capture_map_image(map_html):
    # Set up Selenium to run in headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Save the map HTML to a temporary file
    with open("temp_map.html", "w") as f:
        f.write(map_html)
    
    # Open the temporary HTML file
    driver.get("file://" + os.path.abspath("temp_map.html"))
    
    # Wait for the map to load
    time.sleep(5)
    
    # Capture the screenshot
    screenshot = driver.get_screenshot_as_png()
    
    driver.quit()
    
    # Remove the temporary file
    os.remove("temp_map.html")
    
    return Image.open(io.BytesIO(screenshot))

def main():
    st.title("Interactive Map with Layers, Location, Drawing, and Text")

    # Add CSS directly in the Streamlit app
    st.markdown("""
    <style>
    .text-label {
        background-color: white;
        border: 1px solid #ccc;
        padding: 5px;
        font-weight: bold;
    }
    .custom-marker-icon {
        background-color: white;
        border: 2px solid #3388ff;
        border-radius: 50%;
        text-align: center;
        color: #3388ff;
        font-weight: bold;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize the map
    initial_lat = st.number_input("Enter latitude", value=0.0, min_value=-90.0, max_value=90.0)
    initial_lon = st.number_input("Enter longitude", value=0.0, min_value=-180.0, max_value=180.0)
    zoom_level = st.slider("Zoom level", min_value=1, max_value=18, value=2)
    marker_text = st.text_input("Enter text for the marker", value="My Marker")

    m = folium.Map(location=[initial_lat, initial_lon], zoom_start=zoom_level, control_scale=True)

    # ... (rest of your map setup code)

    # Add a marker at the specified coordinates with custom text
    folium.Marker(
        [initial_lat, initial_lon],
        popup=f"{marker_text}<br>Lat: {initial_lat}, Lon: {initial_lon}",
        tooltip=marker_text,
        icon=folium.DivIcon(
            html=f'<div class="custom-marker-icon">{marker_text}</div>',
            icon_size=(100, 40),
            icon_anchor=(50, 20),
        )
    ).add_to(m)

    # Display the map
    try:
        map_data = folium_static(m, width=700, height=500)
    except Exception as e:
        st.error(f"An error occurred while displaying the map: {str(e)}")
        st.info("Please try refreshing the page or check your internet connection.")

    # Export options
    export_format = st.selectbox("Select export format", ["HTML", "PNG"])
    
    if st.button("Export Map"):
        try:
            if export_format == "HTML":
                # Save the map to a string buffer
                buffer = io.BytesIO()
                m.save(buffer, close_file=False)
                map_html = buffer.getvalue().decode()
                
                btn = st.download_button(
                    label="Download Map (HTML)",
                    data=map_html,
                    file_name=f"interactive_map_{uuid.uuid4().hex[:8]}.html",
                    mime="text/html"
                )
            elif export_format == "PNG":
                # Export the map as a PNG image
                img = export_map_image(m)
                img_buffer = io.BytesIO()
                img.save(img_buffer, format="PNG")
                btn = st.download_button(
                    label="Download Map (PNG)",
                    data=img_buffer.getvalue(),
                    file_name=f"interactive_map_{uuid.uuid4().hex[:8]}.png",
                    mime="image/png"
                )
        except Exception as e:
            st.error(f"An error occurred while exporting the map: {str(e)}")
            st.info("Please try again or check your internet connection.")

if __name__ == "__main__":
    main()
