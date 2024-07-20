import streamlit as st
import folium
from folium.plugins import Draw, MousePosition
from streamlit_folium import folium_static
import io
import uuid

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
    """
    m.get_root().html.add_child(folium.Element(js))

def main():
    st.title("Interactive Map with Drawing and Text")

    # Initialize the map
    m = folium.Map(location=[0, 0], zoom_start=2)

    # Add draw control to the map
    draw = Draw(
        draw_options={
            'polyline': True,
            'rectangle': True,
            'polygon': True,
            'circle': True,
            'marker': True,
            'circlemarker': True
        },
        edit_options={'edit': True}
    )
    m.add_child(draw)

    # Add mouse position display
    MousePosition().add_to(m)

    # Add custom text control
    add_text_to_map(m)

    # Add custom CSS for text labels
    css = """
    <style>
    .text-label {
        background-color: white;
        border: 1px solid #ccc;
        padding: 5px;
        font-weight: bold;
    }
    </style>
    """
    m.get_root().html.add_child(folium.Element(css))

    # Display the map
    map_data = folium_static(m, width=700, height=500)

    # Export map button
    if st.button("Export Map"):
        # Save the map to a string buffer
        buffer = io.BytesIO()
        m.save(buffer, close_file=False)
        
        btn = st.download_button(
            label="Download Map",
            data=buffer.getvalue().decode(),
            file_name=f"interactive_map_{uuid.uuid4().hex[:8]}.html",
            mime="text/html"
        )

if __name__ == "__main__":
    main()
