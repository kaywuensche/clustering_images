import os
import io
import shutil
import math
import random
import numpy as np
import requests
import urllib.request
from PIL import Image, ImageDraw
from bs4 import BeautifulSoup
import imghdr
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from keras.models import Model
from keras.preprocessing.image import load_img
from keras.applications.vgg16 import preprocess_input
from keras.applications.vgg16 import VGG16
from yellowbrick.cluster import KElbowVisualizer
import matplotlib.pyplot as plt

ALLOWED_EXTENSIONS = set(['.png', '.jpg', '.jpeg'])

def initiat_exchange(folder):
    if not os.path.isdir(folder):
        os.mkdir(folder)

def del_prev_session(folder):
    if os.path.isdir(folder):
        shutil.rmtree(folder)
    os.mkdir(folder)

def get_image_from_url(url_img, search_dir):
    tempfile = os.path.join(search_dir, "temp.jpeg")
    urllib.request.urlretrieve(url_img, tempfile)
    extension = imghdr.what(tempfile)
    os.remove(tempfile)
    urllib.request.urlretrieve(url_img, os.path.join(search_dir, str(len(os.listdir(search_dir)) + 1) + "." + extension))

def get_images_from_web(searchTerm, search_dir):
    url_list = "https://images.search.yahoo.com/search/images;?p={}", "https://www.google.com/search?q={}&site=webhp&tbm=isch", "https://www.bing.com/images/search?q={}&scope=images"
    done = ()
    for url in url_list:
        searchUrl = url.format(searchTerm)
        d = requests.get(searchUrl).text
        soup = BeautifulSoup(d, 'html.parser')
        img_tags = soup.find_all('img')
        for img in img_tags:
            try:
                key_list = img.attrs.keys()
                url_img = 'na'
                if 'src' in key_list and img['src'].startswith("http"):
                    url_img = img['src']
                elif 'src2' in key_list and img['src2'].startswith("http"):
                    url_img = img['src2']
                get_image_from_url(url_img, search_dir)
                done.append(url_img)
            except:
                pass
        linkTags = soup.findAll('a')
        for linkTag in linkTags:
            try:
                linkUrl = linkTag['href']
                if linkUrl.startswith("http"):
                    if linkUrl.endswith(".jpg") or linkUrl.endswith(".jpeg") or linkUrl.endswith(".png") and linkUrl not in done:
                        get_image_from_url(linkUrl, search_dir)
            except:
                pass

def create_image_from_input(directory):
    if os.path.exists(os.path.join(directory, "temp.jpeg")):
        os.remove(os.path.join(directory, "temp.jpeg"))
    files = [filename.path for filename in os.scandir(directory) if os.path.splitext(filename.name)[1] in ALLOWED_EXTENSIONS]
    grid_size = math.ceil(math.sqrt(len(files))) * 100
    with Image.new('RGBA', (grid_size, grid_size), color="white") as new_im:
        k = 0
        for i in range(0, grid_size, 100):
            for j in range(0, grid_size, 100):
                with Image.open(files[k]) as im:
                    im.thumbnail((100, 100))
                    new_im.paste(im, (i, j))
                    k += 1
                if k >= len(files):
                    break
            if k >= len(files):
                break
        buf = io.BytesIO()
        new_im.save(buf, format='PNG')
    return buf

def resize_img_static(image, size):
    pil_image = Image.open(image)
    width, height = pil_image.size
    pil_image = pil_image.resize((size, int(height * (size / width))), Image.ANTIALIAS)
    return pil_image

def remove_corrupt_images(input, output):
    for filename in os.scandir(input):
        extension = os.path.splitext(filename.name)[1]
        if extension in ALLOWED_EXTENSIONS:
            try:
                with Image.open(filename.path) as img:
                    img.save(os.path.join(output, filename.name.replace(extension, '.png')), 'PNG')
            except:
                print('file ' + filename.name + ' skipped')

def remove_duplicate_images(img_dir):
    no_duplicates = {}
    for image in os.scandir(img_dir):
        pil_image = resize_img_static(image.path, 500)
        bytes_pil_image = pil_image.tobytes()
        hashed_value = hash(bytes_pil_image)
        no_duplicates[hashed_value] = image.path
        pil_image.close()
    for image in os.scandir(img_dir):
        if image.path not in list(no_duplicates.values()):
            os.remove(image.path)

def extract_features(file, model):
    img = load_img(file, target_size=(224,224))
    img = np.array(img)
    # reshape the data for the model reshape(num_of_samples, dim 1, dim 2, channels)
    reshaped_img = img.reshape(1,224,224,3)
    # prepare image for model
    imgx = preprocess_input(reshaped_img)
    # get the feature vector
    features = model.predict(imgx, use_multiprocessing=True)
    return features

def create_image_from_clusters(directory):
    dirs = [os.path.join(directory, d) for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
    cols = len(dirs)
    cols = cols * 100
    rows = 11 * 100
    with Image.new('RGBA', (cols, rows), color="white") as new_im:
        for i in range(0, cols, 100):
            cluster_path = dirs[int(i/100)]
            files = os.listdir(cluster_path)
            ImageDraw.Draw(new_im).text((i, 0), os.path.basename(cluster_path), (0, 0, 0))
            l = 0
            for j in range(100, rows, 100):
                if l < len(files):
                    with Image.open(os.path.join(cluster_path, files[l])) as im:
                        im.thumbnail((100, 100))
                        new_im.paste(im, (i, j))
                        l += 1
        buf = io.BytesIO()
        new_im.save(buf, format='PNG')
        return buf

def clustering(path, amount_of_clusters, meth):
    #load model
    model = VGG16()
    model = Model(inputs=model.inputs, outputs=model.layers[-2].output)
    # load images
    os.chdir(path)
    with os.scandir(path) as files:
        images = [file.name for file in files if file.name.endswith('.png')]
    data = {}
    # create feature vectors
    for image in images:
        feat = extract_features(image, model)
        data[image] = feat
    filenames = np.array(list(data.keys()))
    file_count = len(filenames)
    feat = np.array(list(data.values()))
    feat = feat.reshape(-1,4096)
    # reduce the amount of dimensions in the feature vector
    if len(feat) > 100 and file_count > 100:
        components = 100
    else:
        components = min(len(feat), file_count)
    pca = PCA(n_components=components, random_state=22)
    pca.fit(feat)
    x = pca.transform(feat)
    # calculate best amount of clusters
    if amount_of_clusters is None or meth == 'elbow':
        if file_count > 50:
            rounds = 50
        else:
            rounds = file_count
        model = KMeans()
        visualizer = KElbowVisualizer(model, k=(2, rounds), timings=False)
        visualizer.fit(x)
        if (meth == 'elbow'):
            buf = io.BytesIO()
            visualizer.show(outpath=buf, format='PNG')
            plt.gcf().clear()
            return buf
        else:
            amount_of_clusters = visualizer.elbow_value_
            plt.gcf().clear()
    # clustering
    kmeans = KMeans(n_clusters=amount_of_clusters, random_state=22)
    kmeans.fit(x)
    groups = {}
    for file, cluster in zip(filenames, kmeans.labels_):
        if cluster not in groups.keys():
            groups[cluster] = []
            groups[cluster].append(file)
            os.makedirs(os.path.join(path, 'cluster_' + str(cluster)))
        else:
            groups[cluster].append(file)
        shutil.move(os.path.join(path, file), os.path.join(path, 'cluster_' + str(cluster), file))
    return create_image_from_clusters(path)

def get_sample_of_cluster(output, samplesize):
    list_clusters = [f.path for f in os.scandir(os.path.join(output, "")) if f.is_dir()]
    sample = os.path.join(output, "sample")
    os.makedirs(sample)
    for cluster in list_clusters:
        list_images = [f.path for f in os.scandir(os.path.join(cluster, "")) if f.is_file()]
        images_of_cluster = math.floor(len(list_images) * samplesize)
        if(images_of_cluster <= 1):
            images_of_cluster = 1
        selected_sample = random.sample(list_images, images_of_cluster)
        for file in selected_sample:
            shutil.copyfile(file, os.path.join(sample, os.path.basename(file)))
