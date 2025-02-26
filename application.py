import streamlit as st
import openai
import numpy as np
import pandas as pd
from PIL import Image
from serch import create_index_faiss, find_closest_vectors_faiss
from openai import OpenAI
import os

import subprocess
import io



# 表示するテキストを切り詰める
def truncate_text_by_chars(text, max_chars=200):
    if len(text) > max_chars:
        return text[:max_chars] + '...'
    return text

def format_caption(rank, description):
    return f"**Rank {rank}:**\n{description}"

def run_image_search_app():
    # セッションステートの初期化
    if 'search_results' not in st.session_state:
        st.session_state['search_results'] = []
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    st.title("KG 画像検索")
    st.write("よく使用される検索ワード")
    common_keywords = ['traffic light', 'night', 'wet road', 'tunnel', '橋', '歩行者', '青空', ]
    # リストの長さに応じたカラムを作成
    columns = st.columns(len(common_keywords))
    # セッションステートの初期化
    if 'search_text' not in st.session_state:
        st.session_state['search_text'] = ""
    for i, keyword in enumerate(common_keywords):
        # 各カラムにボタンを配置
        with columns[i]:
            if st.button(keyword, use_container_width=True):
                st.session_state['search_text'] = keyword
    search_text = st.text_input("検索したい文言を入力してください: ", value=st.session_state['search_text'])
    download_csv_index_number = st.number_input(
        "検索結果の上位何件のデータをダウンロードしますか？: ",
        min_value=9, max_value=5000, value=9, step=1
    )
    if st.button("Search"):
        response = client.embeddings.create(
            input=search_text,
            model="text-embedding-3-small"
        )
        embeds = response.data[0].embedding
        embeds = np.array(embeds)
        ref_vector = embeds.astype('float32')
        index = create_index_faiss(["emb_data"])
        closest_vectors = find_closest_vectors_faiss(ref_vector, "index.faiss", download_csv_index_number)
        
        # 検索結果をセッションステートに保存
        st.session_state['search_results'] = closest_vectors

    # 検索結果がある場合に表示
    if st.session_state['search_results']:
        image_paths = []
        text_paths = []
        full_descriptions = []
        captions = []
        for idx, (image_path, dist) in enumerate(st.session_state['search_results'], 1):
            img_path = image_path.replace("emb_data/", "input_images/")
            image_paths.append(img_path)
            text_path = image_path.replace("emb_data/", "text_data/")
            text_path = text_path + ".txt"
            text_paths.append(text_path)
            
            # 説明文を読み込み
            with open(text_path, "r") as f:
                description = f.read()
            full_descriptions.append(description)
            
            # 短縮された説明文をキャプションに使用
            truncated_description = truncate_text_by_chars(description)
            captions.append(f"{truncated_description}")



        df = pd.DataFrame({"image_path": image_paths, "description": full_descriptions})
        csv = df.to_csv(index=True).encode("utf-8")
        # 上位n件のデータを含んだcsv
        st.download_button(
            "Download CSV",
            data = csv,
            file_name = "search_result.csv",
            mime = "text/csv"
        )
        
        image_list = [Image.open(img_path) for img_path in image_paths[:download_csv_index_number]]
        for i in range(0, len(image_list), 3):
            cols = st.columns([1.5, 0.2, 1.5, 0.2, 1.5])  # 空の列の幅を1に設定
            for j, col in enumerate(cols[::2]):  # 画像を配置する列を選択
                if i + j < len(image_list):
                    img = image_list[i + j]
                    with col:
                        st.image(img, caption=captions[i + j])
                        # 画像をバイトストリームに変換
                        img_byte_arr = io.BytesIO()
                        img.save(img_byte_arr, format='JPEG')
                        img_byte_arr = img_byte_arr.getvalue()
                        # ダウンロードボタンを追加
                        st.download_button(
                            label="Download",
                            data=img_byte_arr,
                            file_name=f"image_{i + j}.jpg",
                            mime="image/jpeg"
                        )
        
                    

def convert_image_to_vector():
    
    # Streamlitアプリケーション
    st.title("KG画像登録システム")

    # 画像のアップロード（複数ファイル対応）
    uploaded_files = st.file_uploader("Choose images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    if uploaded_files:
        save_dir = "GRiT/input_images"
        #os.makedirs(save_dir, exist_ok=True)

        for uploaded_file in uploaded_files:
            # 画像の保存パスを決定
            image_path = os.path.join(save_dir, uploaded_file.name)

            # ファイルが既に存在するか確認
            if os.path.exists(image_path):
                st.info(f"ファイルはすでに存在しています: {uploaded_file.name}")
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
            '--input', 'input_images',
            '--output', 'GRiT/visualization',
            '--opts', 'MODEL.WEIGHTS', 'GRiT/models/grit_b_densecap_objectdet.pth'
            ], capture_output=True, text=True)
            
        
        
        



def main():
    # セッションステートの初期化
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    # 検索文言の初期化
    

    # ページ選択
    st.sidebar.image("KG-Motors-Logo.png")
    page = st.sidebar.selectbox("ページを選択してください", ["画像を検索する", "画像を登録する"])

    if page == "画像を登録する":
        if not st.session_state['authenticated']:
            st.title("KG画像登録システム")
            # パスワード入力
            password = st.text_input("パスワードを入力してください", type="password")
            if st.button("ログイン"):
                if password == "Doshisho1202":  # ここに実際のパスワードを設定
                    st.session_state['authenticated'] = True
                    st.success("認証に成功しました。")
                    
                else:
                    st.error("パスワードが間違っています。")
        else:
            convert_image_to_vector()
    
    elif page == "画像を検索する":
        run_image_search_app()

if __name__ == "__main__":
    main()