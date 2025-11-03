from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from rag_system import RAGSystem
import json
import asyncio

load_dotenv()

# FastAPI 앱 생성
app = FastAPI(title="디지털 광고 마케팅 챗봇")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# RAG 시스템 초기화
rag_system = RAGSystem(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    pinecone_api_key=os.getenv("PINECONE_API_KEY"),
    pinecone_env=os.getenv("PINECONE_ENV", "us-east-1")
)

@app.get("/", response_class=HTMLResponse)
async def home():
    """메인 채팅 페이지"""
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>디지털 광고 마케팅 챗봇</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            .container {
                width: 90%;
                max-width: 800px;
                height: 90vh;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 24px;
                margin-bottom: 5px;
            }
            
            .header p {
                font-size: 14px;
                opacity: 0.9;
            }
            
            .chat-container {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background: #f8f9fa;
            }
            
            .message {
                margin-bottom: 15px;
                display: flex;
                animation: fadeIn 0.3s ease-in;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .message.user {
                justify-content: flex-end;
            }
            
            .message.bot {
                justify-content: flex-start;
            }
            
            .message-content {
                max-width: 70%;
                padding: 12px 16px;
                border-radius: 18px;
                word-wrap: break-word;
            }
            
            .message.user .message-content {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            
            .message.bot .message-content {
                background: white;
                color: #333;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            
            .input-container {
                padding: 20px;
                background: white;
                border-top: 1px solid #e0e0e0;
                display: flex;
                gap: 10px;
            }
            
            #user-input {
                flex: 1;
                padding: 12px 16px;
                border: 2px solid #e0e0e0;
                border-radius: 25px;
                font-size: 14px;
                outline: none;
                transition: border-color 0.3s;
            }
            
            #user-input:focus {
                border-color: #667eea;
            }
            
            #send-btn {
                padding: 12px 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 600;
                transition: transform 0.2s;
            }
            
            #send-btn:hover {
                transform: scale(1.05);
            }
            
            #send-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            
            .typing-indicator {
                display: none;
                padding: 12px 16px;
                background: white;
                border-radius: 18px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                width: fit-content;
            }
            
            .typing-indicator.active {
                display: block;
            }
            
            .typing-indicator span {
                display: inline-block;
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #667eea;
                margin: 0 2px;
                animation: typing 1.4s infinite;
            }
            
            .typing-indicator span:nth-child(2) {
                animation-delay: 0.2s;
            }
            
            .typing-indicator span:nth-child(3) {
                animation-delay: 0.4s;
            }
            
            @keyframes typing {
                0%, 60%, 100% { transform: translateY(0); }
                30% { transform: translateY(-10px); }
            }
            
            .suggestions {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                padding: 10px 20px;
                background: #f8f9fa;
            }
            
            .suggestion-btn {
                padding: 8px 16px;
                background: white;
                border: 2px solid #667eea;
                color: #667eea;
                border-radius: 20px;
                cursor: pointer;
                font-size: 13px;
                transition: all 0.3s;
            }
            
            .suggestion-btn:hover {
                background: #667eea;
                color: white;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 디지털 광고 마케팅 전문가</h1>
                <p>네이버 · 구글 · 메타 광고에 대해 무엇이든 물어보세요!</p>
            </div>
            
            <div class="suggestions">
                <button class="suggestion-btn" onclick="askQuestion('네이버 파워링크 품질지수 개선 방법은?')">
                    네이버 품질지수 개선
                </button>
                <button class="suggestion-btn" onclick="askQuestion('구글 애즈 키워드 매칭 유형 설명해줘')">
                    구글 키워드 매칭
                </button>
                <button class="suggestion-btn" onclick="askQuestion('메타 광고 타겟팅 설정 방법')">
                    메타 타겟팅
                </button>
            </div>
            
            <div class="chat-container" id="chat-container">
                <div class="message bot">
                    <div class="message-content">
                        안녕하세요! 저는 검색광고와 SNS광고 전문 상담 AI입니다. 
                        네이버, 구글, 메타 광고에 대해 궁금한 점을 물어보세요! 😊
                    </div>
                </div>
                <div class="typing-indicator" id="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
            
            <div class="input-container">
                <input 
                    type="text" 
                    id="user-input" 
                    placeholder="메시지를 입력하세요..."
                    onkeypress="if(event.key==='Enter') sendMessage()"
                />
                <button id="send-btn" onclick="sendMessage()">전송</button>
            </div>
        </div>
        
        <script>
            const chatContainer = document.getElementById('chat-container');
            const userInput = document.getElementById('user-input');
            const sendBtn = document.getElementById('send-btn');
            const typingIndicator = document.getElementById('typing-indicator');
            
            function scrollToBottom() {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
            
            function addMessage(content, isUser) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
                
                const contentDiv = document.createElement('div');
                contentDiv.className = 'message-content';
                contentDiv.textContent = content;
                
                messageDiv.appendChild(contentDiv);
                
                // typing indicator 전에 삽입
                chatContainer.insertBefore(messageDiv, typingIndicator);
                scrollToBottom();
            }
            
            function askQuestion(question) {
                userInput.value = question;
                sendMessage();
            }
            
            async function sendMessage() {
                const message = userInput.value.trim();
                if (!message) return;
                
                // 사용자 메시지 추가
                addMessage(message, true);
                userInput.value = '';
                
                // UI 비활성화
                sendBtn.disabled = true;
                userInput.disabled = true;
                typingIndicator.classList.add('active');
                scrollToBottom();
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ message: message })
                    });
                    
                    const data = await response.json();
                    
                    // 봇 응답 추가
                    typingIndicator.classList.remove('active');
                    addMessage(data.response, false);
                    
                } catch (error) {
                    console.error('Error:', error);
                    typingIndicator.classList.remove('active');
                    addMessage('죄송합니다. 오류가 발생했습니다. 다시 시도해주세요.', false);
                }
                
                // UI 활성화
                sendBtn.disabled = false;
                userInput.disabled = false;
                userInput.focus();
            }
            
            // 초기 포커스
            userInput.focus();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/chat")
async def chat(request: Request):
    """채팅 API 엔드포인트"""
    data = await request.json()
    user_message = data.get("message", "")
    
    try:
        # 1. 관련 문서 검색
        relevant_docs = rag_system.search_similar_content(user_message, top_k=3)
        
        # 2. 컨텍스트 구성
        context = _build_context(relevant_docs)
        
        # 3. 프롬프트 생성
        system_prompt = f"""당신은 검색광고마케터1급과 SNS광고마케터1급 자격증 교재를 기반으로 
학습한 디지털 마케팅 전문가입니다.

아래는 사용자 질문과 관련된 교재 내용입니다:

{context}

이 정보를 바탕으로 정확하고 실용적인 답변을 제공해주세요.
답변 시 다음을 지켜주세요:
1. 교재 내용을 기반으로 정확한 정보 제공
2. 초보자도 이해할 수 있도록 명확하게 설명
3. 실무 예시와 함께 구체적인 해결책 제시
4. 한국어로 친절하게 답변
5. 답변은 간결하고 핵심적으로 (3-5문장 정도)

플랫폼별 특징:
- 네이버: 파워링크, 쇼핑검색, 브랜드검색
- 구글: 검색광고, 디스플레이, YouTube, 쇼핑
- 메타: 페이스북, 인스타그램 캠페인"""

        full_prompt = f"{system_prompt}\n\n사용자 질문: {user_message}"
        
        # 4. 응답 생성
        response = await rag_system.generate_response(full_prompt)
        
        return {"response": response}
        
    except Exception as e:
        print(f"Error in chat: {e}")
        return {"response": "죄송합니다. 오류가 발생했습니다. 다시 시도해주세요."}

def _build_context(docs):
    """검색된 문서들로 컨텍스트 구성"""
    if not docs:
        return "관련 교재 내용을 찾지 못했습니다. 일반적인 지식을 바탕으로 답변하겠습니다."
    
    context_parts = []
    for i, doc in enumerate(docs, 1):
        context_parts.append(f"[관련 내용 {i}]\n{doc['text']}\n")
    
    return "\n".join(context_parts)

@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {"status": "ok", "message": "서버가 정상 작동 중입니다"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 서버 시작: http://localhost:{port}")
    print(f"💬 채팅 페이지: http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
