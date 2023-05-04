import streamlit as st
import pandas as pd
from google.cloud import storage
import gcsfs
gcs = storage.Client()
from google.cloud import vision
import urllib.request
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import png


# n = f"""<style>div.stButton > button:third-child {{ background-color: #6A6C6D; font-size:16px; color:powderblue; border: 2px solid #117E88; border radius:50px 50px 50px 50px; }}<style>"""

#st.markdown(n, unsafe_allow_html=True)

def header1(url): 
    st.markdown(f'<p style="color:#117E88;font-size:48px;border-radius:2%;"><center><strong>{url}</strong></center></p>', unsafe_allow_html=True)

def list_product_sets(project_id, location):
    """List all product sets.
    Args:
        project_id: Id of the project.
        location: A compute region name.
    """
    client = vision.ProductSearchClient()

    # A resource that represents Google Cloud Platform location.
    location_path = f"projects/{project_id}/locations/{location}"

    # List all the product sets available in the region.
    product_sets = client.list_product_sets(parent=location_path)

    # Display the product set information.
    products = []
    for product_set in product_sets:
        products.append(product_set.name.split('/')[-1])
    
    return products

def get_similar_products_file(project_id, location, product_set_id, product_category,file_path, filter):
    """Search similar products to image.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_set_id: Id of the product set.
        product_category: Category of the product.
        file_path: Local file path of the image to be searched.
        filter: Condition to be applied on the labels.
        Example for filter: (color = red OR color = blue) AND style = kids
        It will search on all products with the following labels:
        color:red AND style:kids
        color:blue AND style:kids
    """
    # product_search_client is needed only for its helper methods.
    product_search_client = vision.ProductSearchClient()
    image_annotator_client = vision.ImageAnnotatorClient()

    # Read the image as a stream of bytes.
    with open(file_path, 'rb') as image_file:
        content = image_file.read()

    # Create annotate image request along with product search feature.
    image = vision.Image(content=content)

    # product search specific parameters
    product_set_path = product_search_client.product_set_path(
        project=project_id, location=location,
        product_set=product_set_id)
    product_search_params = vision.ProductSearchParams(
        product_set=product_set_path,
        product_categories=[product_category],
        filter=filter)
    image_context = vision.ImageContext(
        product_search_params=product_search_params)

    # Search products similar to the image.
    response = image_annotator_client.product_search(image, image_context=image_context)

    index_time = response.product_search_results.index_time

    results = response.product_search_results.results

    header1('Top 5 Recommendations')
    
    for i in range(0,5):
        product = results[i].product
        
        s = product.name
        urllib.request.urlretrieve('https://storage.googleapis.com/product_search_data/apparel_images/{}.jpg'.format(s.split("/")[-1]),"/api_returned_images/new{}.jpg".format(i))
  
        
def file_selector():
    storage_client = storage.Client()
    bucket_name='product_search_data'
    bucket = storage_client.get_bucket(bucket_name)
    prefix='test_images/'
    iterator = bucket.list_blobs(delimiter='/', prefix=prefix)
    response = iterator._get_next_page_response()
    data=[]
    for i in response['items']:
        z='gs://'+bucket_name+'/'+i['name']
        data.append(z)
    data=data[1:]
    return data  

def predict():
    st.title("Product Search API")
    
    uploaded_file = st.file_uploader("Upload Image Files",type=['jpg','png','jpeg'])
        
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        path = '/api_images/{name}'.format(name=uploaded_file.name)
        image.save(path)
        gcs.get_bucket('product_search_data').blob('test_images/{name1}'.format(name1= uploaded_file.name)).upload_from_filename('/api_images/{name}'.format(name=uploaded_file.name))
     
    filenames=file_selector() 
    filenames = filenames[::-1]
    filenames.append("-")
    filenames = filenames[::-1]
    filename = st.selectbox('Select the file', filenames)
    
    if filename != "-":
        path = '/api_images/{}'.format(filename.split("/")[-1])
        image = Image.open(path)
        newsize = (500, 500)
        img = image.resize(newsize)
#         my_expander = st.beta_expander("View selected image", expanded=False)
#         with my_expander:
#             st.image(img)
        
        stroke_width = st.sidebar.slider("Stroke width: ", 1, 25, 3)
        stroke_color = st.sidebar.color_picker("Stroke color hex: ")
        bg_color = st.sidebar.color_picker("Background color hex: ", "#eee")

        drawing_mode = st.sidebar.selectbox(
            "Drawing tool:", ("rect", "freedraw", "line","circle", "transform")
        )
        realtime_update = st.sidebar.checkbox("Update in realtime", True)
        # Create a canvas component
        width, height = image.size
        
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            background_color=bg_color,
            background_image=Image.open(path),
            update_streamlit=realtime_update,
            height=500,
            width = 500,
            drawing_mode=drawing_mode,
            key="canvas",
        )


        if canvas_result.json_data is not None:
            data = canvas_result.json_data

            for i in range(len(data["objects"])):
                left = data["objects"][i]["left"]
                top = data["objects"][i]["top"]
                right = left+data["objects"][i]["width"]
                bottom = top+data["objects"][i]["height"]

                new_image = img.crop((left,top,right,bottom))
                st.image(new_image)
                new_image.save("/api_images/cropped_{}".format(filename.split("/")[-1]))
        
        project_id = st.text_input("Enter the Project ID","autoaiproject01")
        location = st.text_input("Enter the Location","us-west1")
        cat = st.selectbox("Choose the product category", ["-","apparel-v2"])
    
        if cat != "-":
            y = list_product_sets(project_id, location)
            y.append("-")
            prod_type = st.selectbox("Choose the product type",y[::-1])
            
    
            if prod_type!="-":
                filter = " "
                
                col1,col2 = st.columns([1,1])
                
                with col1:
                    orig = st.button("Get Recommendations (Original Image)")
                with col2:
                    crop = st.button("Get Recommendations (Cropped Image) ")
                    
                if orig:
            
                    get_similar_products_file(project_id, location, prod_type, cat, path,filter)

                    col1,col2 = st.columns([1,1])

                    with col1:
                        img = Image.open("/api_returned_images/new0.jpg")
                        newsize = (300, 300)
                        img = img.resize(newsize)
                        st.image(img)

                    with col2:
                        img = Image.open("/api_returned_images/new1.jpg")
                        newsize = (300, 300)
                        img = img.resize(newsize)
                        st.image(img)

                    col1,col2 = st.columns([1,1])

                    with col1:
                        img = Image.open("/api_returned_images/new2.jpg")
                        newsize = (300, 300)
                        img = img.resize(newsize)
                        st.image(img)

                    with col2:
                        img = Image.open("/api_returned_images/new3.jpg")
                        newsize = (300, 300)
                        img = img.resize(newsize)
                        st.image(img)

                    col1,col2,col3 = st.columns([1,1,1])

                    with col1:
                        st.write(" ")

                    with col2:
                        img = Image.open("/api_returned_images/new4.jpg")
                        newsize = (300, 300)
                        img = img.resize(newsize)
                        st.image(img)

                    with col3:
                        st.write(" ")
            
                if crop:
                    new_path ="/api_images/cropped_{}".format(filename.split("/")[-1])
                    get_similar_products_file(project_id, location, prod_type, cat, new_path,filter)

                    col1,col2 = st.columns([1,1])

                    with col1:
                        img = Image.open("/api_returned_images/new0.jpg")
                        newsize = (300, 300)
                        img = img.resize(newsize)
                        st.image(img)

                    with col2:
                        img = Image.open("/api_returned_images/new1.jpg")
                        newsize = (300, 300)
                        img = img.resize(newsize)
                        st.image(img)

                    col1,col2 = st.columns([1,1])

                    with col1:
                        img = Image.open("/api_returned_images/new2.jpg")
                        newsize = (300, 300)
                        img = img.resize(newsize)
                        st.image(img)

                    with col2:
                        img = Image.open("/api_returned_images/new3.jpg")
                        newsize = (300, 300)
                        img = img.resize(newsize)
                        st.image(img)

                    col1,col2,col3 = st.columns([1,1,1])

                    with col1:
                        st.write(" ")

                    with col2:
                        img = Image.open("/api_returned_images/new4.jpg")
                        newsize = (300, 300)
                        img = img.resize(newsize)
                        st.image(img)

                    with col3:
                        st.write(" ")
                      
                    
if __name__ == "__main__":
    predict()