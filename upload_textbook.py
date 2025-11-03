import os
from PyPDF2 import PdfReader
from rag_system import RAGSystem
from dotenv import load_dotenv
import re

load_dotenv()

class TextbookUploader:
    def __init__(self):
        self.rag = RAGSystem(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            pinecone_api_key=os.getenv("PINECONE_API_KEY"),
            pinecone_env=os.getenv("PINECONE_ENV")
        )
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """PDF에서 텍스트 추출"""
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> list:
        """
        텍스트를 청크로 분할
        
        Args:
            text: 전체 텍스트
            chunk_size: 각 청크의 대략적인 크기 (문자 수)
            overlap: 청크 간 겹치는 부분의 크기
            
        Returns:
            청크 리스트
        """
        # 문단 단위로 먼저 분리
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            # 현재 청크에 문단을 추가했을 때 크기 확인
            if len(current_chunk) + len(para) < chunk_size:
                current_chunk += para + "\n\n"
            else:
                # 청크가 충분히 크면 저장하고 새로 시작
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # Overlap을 위해 이전 청크의 마지막 부분 포함
                if chunks:
                    overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                    current_chunk = overlap_text + para + "\n\n"
                else:
                    current_chunk = para + "\n\n"
        
        # 마지막 청크 추가
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def detect_chapter(self, text: str) -> str:
        """텍스트에서 챕터 정보 추출"""
        # 챕터 패턴 예시: "Chapter 1", "제1장", "1장" 등
        patterns = [
            r'Chapter\s*(\d+)',
            r'제\s*(\d+)\s*장',
            r'(\d+)\s*장',
            r'CHAPTER\s*(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text[:500])  # 텍스트 앞부분에서 찾기
            if match:
                return f"Chapter {match.group(1)}"
        
        return "Unknown Chapter"
    
    def upload_textbook(self, pdf_path: str, textbook_name: str):
        """
        교재를 벡터 DB에 업로드
        
        Args:
            pdf_path: PDF 파일 경로
            textbook_name: 교재 이름 (예: "검색광고마케터1급", "SNS광고마케터1급")
        """
        print(f"📚 '{textbook_name}' 교재 업로드 시작...")
        
        # 1. PDF에서 텍스트 추출
        print("📄 PDF 텍스트 추출 중...")
        full_text = self.extract_text_from_pdf(pdf_path)
        
        # 2. 텍스트를 청크로 분할
        print("✂️  텍스트 청크 분할 중...")
        chunks = self.chunk_text(full_text, chunk_size=1000, overlap=200)
        print(f"   총 {len(chunks)}개의 청크 생성됨")
        
        # 3. 각 청크를 벡터 DB에 업로드
        print("☁️  벡터 DB에 업로드 중...")
        for i, chunk in enumerate(chunks):
            chapter = self.detect_chapter(chunk)
            
            metadata = {
                'source': textbook_name,
                'chunk_id': i,
                'chapter': chapter,
                'total_chunks': len(chunks)
            }
            
            self.rag.add_document(chunk, metadata)
            
            # 진행상황 표시
            if (i + 1) % 10 == 0:
                print(f"   진행: {i + 1}/{len(chunks)} 청크 완료")
        
        print(f"✅ '{textbook_name}' 업로드 완료!\n")
    
    def upload_multiple_textbooks(self, textbook_files: dict):
        """
        여러 교재를 한번에 업로드
        
        Args:
            textbook_files: {교재명: PDF경로} 딕셔너리
        """
        for name, path in textbook_files.items():
            if os.path.exists(path):
                self.upload_textbook(path, name)
            else:
                print(f"⚠️  파일을 찾을 수 없습니다: {path}")


if __name__ == "__main__":
    uploader = TextbookUploader()
    
    # 교재 파일 경로 설정
    textbooks = {
        "검색광고마케터1급": "./textbooks/검색광고마케터1급.pdf",
        "SNS광고마케터1급": "./textbooks/SNS광고마케터1급.pdf"
    }
    
    # 업로드 실행
    uploader.upload_multiple_textbooks(textbooks)
    
    print("🎉 모든 교재 업로드가 완료되었습니다!")