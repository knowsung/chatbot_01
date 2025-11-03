try:
    # Pinecone 3.x 버전 (새로운 방식)
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_VERSION = 3
except ImportError:
    # Pinecone 2.x 버전 (이전 방식)
    import pinecone
    PINECONE_VERSION = 2

from openai import OpenAI
from typing import List, Dict
import tiktoken
import time

class RAGSystem:
    def __init__(self, openai_api_key: str, pinecone_api_key: str, pinecone_env: str = "us-east-1"):
        """RAG 시스템 초기화"""
        
        # OpenAI 클라이언트
        self.openai_client = OpenAI(api_key=openai_api_key)
        
        # 인덱스 이름
        self.index_name = "ad-marketing-textbook"
        
        # Pinecone 버전별 초기화
        if PINECONE_VERSION == 3:
            print("📌 Pinecone 3.x 버전 사용 중...")
            # Pinecone 초기화 (새로운 방식)
            self.pc = Pinecone(api_key=pinecone_api_key)
            
            # Pinecone 인덱스 연결 또는 생성
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                print(f"인덱스 '{self.index_name}' 생성 중...")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=1536,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=pinecone_env
                    )
                )
                # 인덱스 생성 대기
                print("인덱스 생성 대기 중 (약 10초)...")
                time.sleep(10)
            
            self.index = self.pc.Index(self.index_name)
        else:
            print("📌 Pinecone 2.x 버전 사용 중...")
            # Pinecone 초기화 (이전 방식)
            pinecone.init(api_key=pinecone_api_key, environment=pinecone_env)
            
            # Pinecone 인덱스 연결 또는 생성
            if self.index_name not in pinecone.list_indexes():
                print(f"인덱스 '{self.index_name}' 생성 중...")
                pinecone.create_index(
                    name=self.index_name,
                    dimension=1536,
                    metric="cosine"
                )
                print("인덱스 생성 대기 중 (약 10초)...")
                time.sleep(10)
            
            self.index = pinecone.Index(self.index_name)
        
        # 토큰 카운터
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        
    def create_embedding(self, text: str) -> List[float]:
        """텍스트를 벡터로 변환"""
        response = self.openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
    
    def search_similar_content(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        사용자 질문과 유사한 교재 내용 검색
        
        Args:
            query: 사용자 질문
            top_k: 반환할 결과 개수
            
        Returns:
            관련 문서들의 리스트
        """
        # 질문을 벡터로 변환
        query_vector = self.create_embedding(query)
        
        # Pinecone에서 유사한 내용 검색
        results = self.index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )
        
        # 결과 포맷팅
        docs = []
        for match in results['matches']:
            docs.append({
                'text': match['metadata'].get('text', ''),
                'source': match['metadata'].get('source', ''),
                'chapter': match['metadata'].get('chapter', ''),
                'score': match['score']
            })
        
        return docs
    
    async def generate_response(self, prompt: str) -> str:
        """
        OpenAI를 사용하여 응답 생성
        
        Args:
            prompt: 컨텍스트가 포함된 전체 프롬프트
            
        Returns:
            생성된 응답
        """
        response = self.openai_client.chat.completions.create(
            model="gpt-4",  # 또는 "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "당신은 디지털 광고 마케팅 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    def add_document(self, text: str, metadata: Dict):
        """
        교재 내용을 벡터 DB에 추가
        
        Args:
            text: 추가할 텍스트
            metadata: 메타데이터 (source, chapter 등)
        """
        # 텍스트를 벡터로 변환
        vector = self.create_embedding(text)
        
        # 고유 ID 생성 (ASCII만 허용하므로 해시 사용)
        import hashlib
        source = metadata.get('source', 'unknown')
        chunk_id = metadata.get('chunk_id', 0)
        
        # 한글을 포함한 source를 해시로 변환
        source_hash = hashlib.md5(source.encode('utf-8')).hexdigest()[:8]
        doc_id = f"doc_{source_hash}_{chunk_id}"
        
        # 메타데이터에 원본 텍스트 추가
        metadata['text'] = text
        
        # Pinecone에 저장
        self.index.upsert(
            vectors=[(doc_id, vector, metadata)]
        )
    
    def count_tokens(self, text: str) -> int:
        """텍스트의 토큰 수 계산"""
        return len(self.encoding.encode(text))