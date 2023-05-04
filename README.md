# **Product-Search-Streamlit-app**
## **Product Search API from Google**

This code allows users to upload an image and search for similar products using the Google Cloud Vision Product Search API. The API allows you to search for products that match images by features such as color, style, and texture.

## **Requirements**
### **The following packages are required to run this code:**

- streamlit
- pandas
- google-cloud-storage
- gcsfs
- google-cloud-vision
- urllib
- PIL
- streamlit_drawable_canvas
- png

To install the required packages, run the following command in your terminal:
```pip install streamlit pandas google-cloud-storage gcsfs google-cloud-vision urllib Pillow streamlit_drawable_canvas png```

## **Usage**
- Ensure that you have access to the Google Cloud Vision Product Search API. You will need to create a project and set up authentication. For more information on how to do this, please refer to the official documentation.
- Set the following environment variable in your terminal:
```export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"```
- Run the code using the following command:
```streamlit run app.py```
- Upload an image of the product you wish to search for, and select a file from the dropdown menu that appears.
- Draw a bounding box around the product using the drawing tool on the left. You can adjust the stroke width and color as needed.
- Click the "Search" button to search for similar products. The top 5 recommended products will be displayed.

## **References**
For more information on how to use the Google Cloud Vision Product Search API, please refer to the official documentation.
