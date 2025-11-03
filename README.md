디지털 광고 마케팅 챗봇 서버
검색광고마케터1급과 SNS광고마케터1급 교재 기반 AI 챗봇 서버

🚀 빠른 시작
1. 필수 준비물
Python 3.8 이상
OpenAI API Key (링크)
Pinecone 계정 (링크)
Poe 계정
2. 설치
bash
# 저장소 클론
git clone <your-repo-url>
cd digital-ad-marketing-bot

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
3. 환경 변수 설정
.env 파일 생성:

bash
cp .env.example .env
.env 파일에 API 키 입력:

OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
PINECONE_ENV=us-east-1-aws
POE_ACCESS_KEY=...
4. 교재 업로드
교재 PDF 파일을 ./textbooks/ 폴더에 배치:

textbooks/
├── 검색광고마케터1급.pdf
└── SNS광고마케터1급.pdf
업로드 스크립트 실행:

bash
python upload_textbook.py
5. 서버 실행
로컬에서 테스트:

bash
python main.py
서버가 http://localhost:8000에서 실행됩니다.

6. Poe 봇 연결
Poe Server Bot 생성
Server URL에 배포된 서버 주소 입력 (예: https://your-app.railway.app)
Access Key 입력
봇 생성 완료!
📦 배포 (Railway)
Railway로 배포하기
Railway 가입
새 프로젝트 생성
GitHub 저장소 연결
환경 변수 추가:
OPENAI_API_KEY
PINECONE_API_KEY
PINECONE_ENV
POE_ACCESS_KEY
자동 배포 완료!
배포된 URL을 Poe Bot Server URL에 입력하세요.

🏗️ 프로젝트 구조
.
├── main.py                 # FastAPI 서버 & Poe Bot
├── rag_system.py          # RAG 시스템 (검색 + 생성)
├── upload_textbook.py     # 교재 업로드 스크립트
├── requirements.txt       # Python 패키지
├── .env                   # 환경 변수
├── railway.json           # Railway 배포 설정
└── textbooks/             # 교재 PDF 파일
    ├── 검색광고마케터1급.pdf
    └── SNS광고마케터1급.pdf
🔧 주요 기능
RAG (Retrieval Augmented Generation)
사용자 질문과 관련된 교재 내용 자동 검색
벡터 유사도 기반 정확한 정보 제공
OpenAI GPT를 활용한 자연스러운 답변 생성
지원 플랫폼
✅ 네이버 검색광고 (파워링크, 쇼핑검색, 브랜드검색)
✅ 구글 광고 (검색광고, 디스플레이, YouTube)
✅ 메타 광고 (페이스북, 인스타그램)
🧪 테스트
서버가 실행 중일 때 다음 명령으로 테스트:

bash
curl http://localhost:8000/health
💡 사용 예시
봇에게 이런 질문들을 해보세요:

"네이버 파워링크 품질지수 개선 방법은?"
"구글 애즈 키워드 매칭 유형 설명해줘"
"메타 광고 맞춤 타겟 설정하는 방법"
"검색광고와 디스플레이 광고 차이점"
📝 라이선스
MIT License

🤝 기여
이슈나 PR은 언제나 환영합니다!

