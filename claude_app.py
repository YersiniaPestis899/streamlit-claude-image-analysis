import os
import streamlit as st
import boto3
import json
import base64
from PIL import Image
import io

# 環境変数のチェック
required_env_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_DEFAULT_REGION']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    st.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    st.stop()

# Bedrockクライアントの設定
try:
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name=os.getenv('AWS_DEFAULT_REGION'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
except Exception as e:
    st.error(f"Failed to initialize AWS Bedrock client: {str(e)}")
    st.stop()

def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def analyze_image(image, prompt):
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
        st.error(f"Error during image analysis: {str(e)}")
        return None

st.title("AWS Bedrock Claude 3.5 Sonnet Image Analysis App")

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
        st.error(f"Error processing the image: {str(e)}")