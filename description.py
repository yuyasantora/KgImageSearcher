import streamlit as st
import os
from PIL import Image
import subprocess

# Streamlitアプリケーション
st.title("KG画像検索システム")

# 画像のアップロード（複数ファイル対応）
uploaded_files = st.file_uploader("Choose images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    save_dir = "GRiT/input_images"
    os.makedirs(save_dir, exist_ok=True)

    for uploaded_file in uploaded_files:
        # 画像の保存パスを決定
        image_path = os.path.join(save_dir, uploaded_file.name)

        # ファイルが既に存在するか確認
        if os.path.exists(image_path):
            st.info(f"File already exists and will be skipped: {uploaded_file.name}")
            continue

        # 画像を表示
        image = Image.open(uploaded_file)
        st.image(image, caption=f'Uploaded Image: {uploaded_file.name}', use_container_width=True)

        # 画像をローカルに保存
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Saved file: {image_path}")

    # demo.pyを実行
    result = subprocess.run([
        'python', 'GRiT/demo.py',
        '--test-task', 'DenseCap',
        '--config-file', 'GRiT/configs/GRiT_B_DenseCap_ObjectDet.yaml',
        '--input', 'GRiT/input_images',
        '--output', 'GRiT/visualization',
        '--opts', 'MODEL.WEIGHTS', 'GRiT/models/grit_b_densecap_objectdet.pth'
        ], capture_output=True, text=True)
        
    st.write("GRiT Execution Output:")
    print(result)
    st.text(result.stdout)
    