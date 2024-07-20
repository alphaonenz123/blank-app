import streamlit as st
import folium
from folium.plugins import Draw
from streamlit_folium import folium_static
import io

def main():
    st.title("Interactive Map Marker")

    # Initialize the map
    m = folium.Map(location=[0, 0], zoom_start=2)

    # Add draw control to the map
    draw = Draw(
        draw_options={
            'polyline': False,
            'rectangle': False,
            'polygon': False,
            'circle': False,
            'circlemarker': False,
        },
        edit_options={'edit': False}
    )
    m.add_child(draw)

    # Display the map
    map_data = folium_static(m, width=700, height=500)

    # Create a button to add markers
    if st.button("Add Marker"):
        st.session_state.markers = st.session_state.get('markers', []) + [None]

    # Display input fields for each marker
    for i, marker in enumerate(st.session_state.get('markers', [])):
        col1, col2, col3 = st.columns(3)
        with col1:
            lat = st.number_input(f"Latitude for Marker {i+1}", value=marker[0] if marker else 0.0, key=f"lat_{i}")
        with col2:
            lon = st.number_input(f"Longitude for Marker {i+1}", value=marker[1] if marker else 0.0, key=f"lon_{i}")
        with col3:
            name = st.text_input(f"Name for Marker {i+1}", value=marker[2] if marker and len(marker) > 2 else "", key=f"name_{i}")
        
        st.session_state.markers[i] = (lat, lon, name)

    # Add markers to the map
    for marker in st.session_state.get('markers', []):
        if marker[0] and marker[1]:
            folium.Marker(
                location=[marker[0], marker[1]],
                popup=marker[2] if marker[2] else None
            ).add_to(m)

    # Display the updated map
    map_data = folium_static(m, width=700, height=500)

    # Export map button
    if st.button("Export Map"):
        # Save the map to a string buffer
        buffer = io.BytesIO()
        m.save(buffer, close_file=False)
        
        btn = st.download_button(
            label="Download Map",
            data=buffer.getvalue().decode(),
            file_name="interactive_map.html",
            mime="text/html"
        )

if __name__ == "__main__":
    main()
