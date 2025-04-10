from flask import Flask, render_template, request, jsonify, session
import os
from dotenv import load_dotenv
import requests
import PyPDF2
import glob

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 添加 session 支持

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
API_URL = "https://api.deepseek.com/v1/chat/completions"

# 緩存 PDF 內容
PDF_CACHE = None

def load_pdf_content():
    global PDF_CACHE
    if PDF_CACHE is None:
        pdf_content = []
        pdf_dir = "D:\\Code\\law Petition\\PDF"
        pdf_files = glob.glob(os.path.join(pdf_dir, '*.pdf'))
        
        for pdf_file in pdf_files:
            try:
                with open(pdf_file, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            pdf_content.append(text)
            except Exception as e:
                print(f"Error reading {pdf_file}: {str(e)}")
        
        PDF_CACHE = "\n".join(pdf_content)
    return PDF_CACHE

@app.route('/')
def home():
    if 'conversation_history' not in session:
        session['conversation_history'] = []
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    pdf_content = load_pdf_content()
    
    # 獲取對話歷史
    conversation_history = session.get('conversation_history', [])
    
    prompt = f"""
    請你擔任一位專業的律師。以下是參考資料庫的內容：

    {pdf_content}

    歷史對話記錄：
    {' '.join(conversation_history)}

    根據上述資料和以下案件描述，請生成一份正式的訴狀書：
    {user_message}
    
    請按照以下格式生成訴狀：
    1. 案由
    2. 當事人信息
    3. 訴訟請求
    4. 事實與理由（請引用參考資料中的相關內容）
    5. 法律依據（請引用參考資料中的相關法條）
    6. 結尾
    
    請使用正式的法律用語，並確保格式規範。
    """
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 3000
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        ai_response = response.json()['choices'][0]['message']['content']
        
        # 更新對話歷史
        conversation_history.append(f"User: {user_message}")
        conversation_history.append(f"AI: {ai_response}")
        if len(conversation_history) > 10:  # 保留最近的5輪對話
            conversation_history = conversation_history[-10:]
        session['conversation_history'] = conversation_history
        
        return jsonify({"response": ai_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)