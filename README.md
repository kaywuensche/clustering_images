# Clustering Images

API for grouping images on similarity. 

Optional you can sample your image set based on clusters. Sampling your images makes sense if you have a hugh amount of them and wanna label only a subset by using an [image labeling tool](https://github.com/BMW-InnovationLab/BMW-Labeltool-Lite).

## Prerequisites:
- docker
- docker-compose

### Check for prerequisites
To check if docker-ce is installed:

```docker --version```

To check if docker-compose is installed:

```docker-compose --version```

### Install prerequisites
**Ubuntu**

To install [Docker](https://docs.docker.com/engine/install/ubuntu/) and [Docker Compose](https://docs.docker.com/compose/install/) on Ubuntu, please follow the link.

**Windows 10**

To install Docker on [Windows](https://docs.docker.com/docker-for-windows/install/), please follow the link.

## Build The Docker Image
In order to build the project run the following command from the project's root directory:

```sudo docker-compose up --build```

## API Endpoints
To see all the available endpoints, open your favorite browser and navigate to:

```http://<machine_IP>:5002/docs```

<img width="968" alt="overview" src="https://user-images.githubusercontent.com/58667455/119461518-10106a80-bd40-11eb-887f-0f5777490afc.png">

You can change the port in the docker compose file.

**/download_web_images (POST)**

This endpoint takes a search query and downloads corresponding images from google, bing and yahoo.

Images will be saved to the mounted input directory, which can be changed in the docker compose file:
```
├──exchange/
    ├── input/
        ├── *.jpg
        ├── *.jpeg
        ├── *.png
```
The endpoint returns an overview of all downloaded images. For example when searching for 'germany':

![all_input_images](https://user-images.githubusercontent.com/58667455/119461239-cc1d6580-bd3f-11eb-9653-752f60f76d05.png)

**/get_amount_of_clusters (POST)**

This endpoint takes the image set from the mounted input directory and returns the result of the elbow method for choosing the best amount of clusters:

![elbow](https://user-images.githubusercontent.com/58667455/119462733-5b774880-bd41-11eb-88d3-6c914cfc650d.png)

Please place files in the mounted input directory. 
```
├──exchange/
    ├── input/
        ├── *.jpg
        ├── *.jpeg
        ├── *.png
```

**/cluster_images (POST)**

This endpoint takes the image set from the mounted input directory and groups them based on similarity.

In addition you have the opportunity to get a sample of your image set by choosing *x* percentage of each image cluster.

Please place files in the input directory. The output directory will be generated automaticly:
```
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
```
The endpoint returns an overview of the image clusters:

![clusters_overview](https://user-images.githubusercontent.com/58667455/119463097-b3ae4a80-bd41-11eb-8df1-d341b20e50c4.png)
