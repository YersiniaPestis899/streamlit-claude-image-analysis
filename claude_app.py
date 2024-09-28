import streamlit as st
import boto3
import json
import base64
from PIL import Image
import io

# AWSキー入力と保存のための関数
def get_aws_keys():
    if 'aws_credentials_saved' not in st.session_state:
        st.session_state.aws_credentials_saved = False
    if 'aws_access_key_id' not in st.session_state:
        st.session_state.aws_access_key_id = ''
    if 'aws_secret_access_key' not in st.session_state:
        st.session_state.aws_secret_access_key = ''
    if 'aws_default_region' not in st.session_state:
        st.session_state.aws_default_region = 'ap-northeast-1'

    st.sidebar.title("AWS認証情報")
    aws_access_key_id = st.sidebar.text_input("AWS Access Key ID", st.session_state.aws_access_key_id)
    aws_secret_access_key = st.sidebar.text_input("AWS Secret Access Key", st.session_state.aws_secret_access_key, type="password")
    aws_default_region = st.sidebar.text_input("AWS Default Region", st.session_state.aws_default_region)

    if st.sidebar.button("保存"):
        st.session_state.aws_access_key_id = aws_access_key_id
        st.session_state.aws_secret_access_key = aws_secret_access_key
        st.session_state.aws_default_region = aws_default_region
        st.session_state.aws_credentials_saved = True
        st.sidebar.success("AWSキーが保存されました！")
        st.rerun()  # ここを変更

    return aws_access_key_id, aws_secret_access_key, aws_default_region

# AWSキーの取得
aws_access_key_id, aws_secret_access_key, aws_default_region = get_aws_keys()

# Bedrockクライアントの設定
@st.cache_resource
def get_bedrock_client():
    if not aws_access_key_id or not aws_secret_access_key or not aws_default_region:
        return None
    try:
        return boto3.client(
            service_name='bedrock-runtime',
            region_name=aws_default_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
    except Exception as e:
        st.error(f"AWS Bedrockクライアントの初期化に失敗しました: {str(e)}")
        return None

bedrock = get_bedrock_client()

# encode_image関数とanalyze_image関数は変更なし

def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def analyze_image(image, prompt):
    if not bedrock:
        st.error("AWS Bedrockクライアントが初期化されていません。")
        return None
    
    try:
        base64_image = encode_image(image)
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 200000,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": base64_image
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        response = bedrock.invoke_model(
            body=json.dumps(body),
            modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
            contentType="application/json",
            accept="application/json"
        )

        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    except Exception as e:
        st.error(f"画像解析中にエラーが発生しました: {str(e)}")
        return None

st.title("AWS Bedrock Claude 3.5 Sonnet 画像解析アプリ")

# AWS認証情報が保存されていない場合にのみエラーメッセージを表示
if not st.session_state.aws_credentials_saved:
    st.error("AWS認証情報を入力してください。")
else:
    uploaded_file = st.file_uploader("画像をアップロードしてください", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption='アップロードされた画像', use_column_width=True)

            analysis_button = st.button("画像を解析")
            if analysis_button:
                with st.spinner("画像を解析中..."):
                    result = analyze_image(uploaded_file, "この画像を詳細に説明してください。")
                if result:
                    st.write(result)

            question = st.text_input("画像について質問してください")
            if st.button("質問する") and question:
                with st.spinner("回答を生成中..."):
                    answer = analyze_image(uploaded_file, question)
                if answer:
                    st.write(answer)
        except Exception as e:
            st.error(f"画像処理中にエラーが発生しました: {str(e)}")