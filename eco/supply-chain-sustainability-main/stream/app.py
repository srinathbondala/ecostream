import streamlit as st
import pandas as pd
from co2 import process_data
import folium
from streamlit_folium import folium_static
from model2 import function1, function2



# Function to process data for Model 3
def process_data_model3(input1, input2, input3):
    # Your data processing code for Model 3 here
    
    return "model3"

# UI for Model 1
def model1_ui():
    st.title("Optimal Means Of Transpoting")
    uploaded_file = st.file_uploader("Upload Order Lines CSV", type=['csv'])
    if uploaded_file is not None:
        # Read CSV file
            df_lines = pd.read_csv(uploaded_file)
            # Process data for Model 1
            df_agg = process_data(df_lines)
            st.title("Order Lines Data Analysis")
            # Process data
            df_agg = process_data(df_lines)
            # Display final report
            st.subheader("Final Report")
            st.write(df_agg)
    # Add specific UI elements for Model 1 here

# UI for Model 2
def model2_ui():
    product_type_options = ["electronics", "ceramics", "plastic", "wood", "fabric", "glass", "metal"]
    new_product_type = st.selectbox("Enter the new product type:", product_type_options)
    new_product_weight = st.number_input("Enter the weight of the new product:", value=0.0)
    new_product_length = st.number_input("Enter the length of the new product:", value=0.0)
    new_product_width = st.number_input("Enter the width of the new product:", value=0.0)
    new_product_height = st.number_input("Enter the height of the new product:", value=0.0)
    new_product_surface_area = 2*(new_product_length*new_product_width + new_product_width*new_product_height + new_product_height*new_product_length)
    new_product_volume = abs(new_product_length*new_product_width*new_product_height)
    new_product_padding_thickness = (new_product_weight*0.5)/100

    if st.button("Predict"):
        new_product_features = {
            'product_type': new_product_type,
            'weight': new_product_weight,
            'length': new_product_length,
            'width': new_product_width,
            'height': new_product_height,
            'surface_area': new_product_surface_area,
            'volume': new_product_volume,
            'padding_thickness': new_product_padding_thickness
        }
        predicted_padding = function1(new_product_features,new_product_features['product_type'],new_product_features["weight"])
        st.write("Padding Model Output")
        st.write(f"Predicted padding type for '{new_product_type}' with weight {new_product_weight}: {predicted_padding}")
        st.write("Predicted padding thickness:", new_product_features['padding_thickness'])
        pt=function2(new_product_features,predicted_padding)
        st.write(pt)

# UI for Model 3
def model3_ui():
    st.write("Model 3 UI")
    # Add specific UI elements for Model 2 here
    input1 = st.text_input("Input 1")
    input2 = st.text_input("Input 2")
    if st.button("Run Model 2"):
        # Add a title
        st.title("Map Locating The Warehouses")

        # Create a map object
        m = folium.Map(location=[37.7749, -122.4194], zoom_start=10)

        # Add markers for two locations
        locations = [[37.7749, -122.4194], [34.0522, -118.2437]]  # Coordinates of two locations
        tooltips = ['San Francisco', 'Los Angeles']  # Tooltip for each marker

        for loc, tooltip in zip(locations, tooltips):
            folium.Marker(loc, tooltip=tooltip).add_to(m)

        # Display the map using streamlit
        folium_static(m)
def main():
    # Title and file upload
    st.title("Supply Chain Sustainability Models")
    
    # Sidebar with model selection
    model = st.sidebar.selectbox("Select Model", ("Model 1", "Model 2"))
    
    if model == "Model 1":
        # Display UI for Model 1
        model1_ui()
    elif model == "Model 2":
        # Display UI for Model 2
        model2_ui()
    # elif model == "Model 3":
    #     # Display UI for Model 3
    #     model3_ui()

if __name__ == "__main__":
    main()