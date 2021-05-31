from fastapi import FastAPI, Form, Response
from utils import initiat_exchange, create_image_from_clusters, create_image_from_input, clustering, get_sample_of_cluster, del_prev_session, remove_corrupt_images, remove_duplicate_images, get_sample_of_cluster, get_images_from_web
import os

app = FastAPI(title='Image Clustering and Sampling',
              description='<b>API for grouping images on similarity.<br><br> In addition you can sample your image set based on created clusters. Sampling your images makes sense if you have a hugh amount of them and wanna label only a subset by using an image labeling tool.<br><br>If you don`t have an image set you can download images by using the web image download.<br><br><br>Contact the developer:<br><font color="#808080">Kay Wünsche: <a href="mailto:">kay.wuensche@gmx.de</a>')

input = os.path.join('/exchange', 'input', '')
output = os.path.join('/exchange', 'output', '')
initiat_exchange(input)
initiat_exchange(output)
ALLOWED_EXTENSIONS = set(['.png', '.jpg', '.jpeg'])

@app.post('/download_web_images', tags=['Web Image Download'])
async def download_web_images(
    search_query: str = Form(..., description="Search query for web search engines, e.g. 'germany':"),
):
    """
    This endpoint takes a search query and downloads corresponding images from google, bing and yahoo.

    Images will be saved to the mounted input directory:

        ├──exchange/
            ├── input/
                ├── *.jpg
                ├── *.jpeg
                ├── *.png

    The endpoint returns an overview of all downloaded images.
    """
    del_prev_session(input)
    del_prev_session(output)
    searchquery = search_query.strip().lower()
    get_images_from_web(searchquery, input)
    buf = create_image_from_input(input)
    return Response(content=buf.getvalue(), media_type="image/png")

@app.get('/get_amount_of_clusters', tags=['Image Clustering'])
async def get_amount_of_clusters():
    """
    This endpoint takes the image set from the mounted input directory and returns the result of the elbow method for choosing the best amount of clusters.

    Please place files in the input folder:

        ├──exchange/
            ├── input/
                ├── *.jpg
                ├── *.jpeg
                ├── *.png
    """
    images = [file for file in os.scandir(input) if os.path.splitext(file.name)[1] in ALLOWED_EXTENSIONS]
    if len(images) == 0:
        return "images not found in mounted input directory '/exchange/input/'"
    del_prev_session(output)
    remove_corrupt_images(input, output)
    remove_duplicate_images(output)
    buf = clustering(output, None, 'elbow')
    return Response(content=buf.getvalue(), media_type="image/png")

@app.post('/cluster_images', tags=['Image Clustering'])
async def cluster_images(
    amount_of_clusters: int = Form(None, description="Amount of centers for clustering, e.g. '10'. Will be calculated automaticly if value is missing: "),
    sampel_of_cluster: float = Form(None, description="Percentage of images in a cluster for sampling, e.g. '0.2'. Sampling will be not performed if value is missing: ")
):
    """
    This endpoint takes the image set from the mounted input directory and groups them based on similarity.

    In addition you have the opportunity to get a sample of your image set by choosing x percentage of each image cluster.

    Please place files in the input directory. The output directory will be generated automaticly:

        ├──exchange/
            ├── input/
            │   ├── *.jpg
            │   ├── *.jpeg
            │   ├── *.png
            │
            ├──output/
                ├── cluster_0/
                │   ├── *.jpg
                │   ├── *.jpeg
                │   ├── *.png
                ├── cluster_1/
                │   ├── *.jpg
                │   ├── *.jpeg
                │   ├── *.png
                ├── sample/
                    ├── *.jpg
                    ├── *.jpeg
                    ├── *.png
    The endpoint returns an overview of the image clusters.
    """
    images = [file for file in os.scandir(input) if os.path.splitext(file.name)[1] in ALLOWED_EXTENSIONS]
    if len(images) == 0:
        return "images not found in mounted input directory '/exchange/input/'"
    del_prev_session(output)
    remove_corrupt_images(input, output)
    remove_duplicate_images(output)
    buf = clustering(output, amount_of_clusters, 'clustering')
    if sampel_of_cluster != None:
        get_sample_of_cluster(output, sampel_of_cluster)
    return Response(content=buf.getvalue(), media_type="image/png")
