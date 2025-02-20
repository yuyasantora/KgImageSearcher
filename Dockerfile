# ベースイメージを指定
FROM python:3.9



# 作業ディレクトリを設定
WORKDIR /app

# Node.jsとnpmをインストール
RUN apt-get update && apt-get install -y nodejs npm


# 必要なツールとライブラリをインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    git \
    curl \
    wget \
    unzip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    build-essential \
    gfortran \
    libatlas-base-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*


RUN pip3 install torch torchvision opencv-python

# numpyのバージョンを固定してインストール
RUN pip3 install "numpy<2"

# torchをインストール
RUN pip3 install --no-cache-dir torch

RUN git clone https://github.com/facebookresearch/detectron2.git && \
    cd detectron2 && \
    git checkout cc87e7ec && \
    sed -i 's/Image.LINEAR/Image.BILINEAR/g' detectron2/data/transforms/transform.py && \
    pip3 install --no-cache-dir -e .

# ローカルのフォルダをコンテナにコピー
COPY ./GRiT /app/GRiT

# pipをアップグレード
RUN pip3 install --upgrade pip

# 必要なパッケージをインストール
RUN pip3 install -r /app/GRiT/requirements.txt

# コンテナ起動時に実行するコマンドを指定
CMD ["python", "/app/GRiT/demo.py", "--test-task", "DenseCap", "--config-file", "GRiT/configs/GRiT_B_DenseCap_ObjectDet.yaml", "--input", "GRiT/demo_images", "--output", "GRiT/visualization", "--opts", "MODEL.WEIGHTS", "GRiT/models/grit_b_densecap_objectdet.pth"]
