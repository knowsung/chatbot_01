import os
from dotenv import load_dotenv
from rag_system import RAGSystem

load_dotenv()

def test_connection():
    """API 연결 테스트"""
    print("=" * 50)
    print("🧪 시스템 연결 테스트 시작")
    print("=" * 50)
    
    # 환경변수 확인
    print("\n1️⃣ 환경변수 확인...")
    openai_key = os.getenv("OPENAI_API_KEY")
    pinecone_key = os.getenv("PINECONE_API_KEY")
    pinecone_env = os.getenv("PINECONE_ENV", "us-east-1")
    
    if not openai_key or openai_key == "sk-your-openai-api-key-here":
        print("❌ OPENAI_API_KEY가 설정되지 않았습니다!")
        return False
    else:
        print(f"✅ OpenAI API Key: {openai_key[:10]}...")
    
    if not pinecone_key or pinecone_key == "your-pinecone-api-key-here":
        print("❌ PINECONE_API_KEY가 설정되지 않았습니다!")
        return False
    else:
        print(f"✅ Pinecone API Key: {pinecone_key[:10]}...")
    
    print(f"✅ Pinecone Environment: {pinecone_env}")
    
    # RAG 시스템 초기화
    print("\n2️⃣ RAG 시스템 초기화 중...")
    try:
        rag = RAGSystem(
            openai_api_key=openai_key,
            pinecone_api_key=pinecone_key,
            pinecone_env=pinecone_env
        )
        print("✅ RAG 시스템 초기화 성공!")
    except Exception as e:
        print(f"❌ RAG 시스템 초기화 실패: {e}")
        return False
    
    # Embedding 테스트
    print("\n3️⃣ Embedding 생성 테스트...")
    try:
        test_text = "네이버 검색광고 품질지수를 높이는 방법"
        embedding = rag.create_embedding(test_text)
        print(f"✅ Embedding 생성 성공! (차원: {len(embedding)})")
    except Exception as e:
        print(f"❌ Embedding 생성 실패: {e}")
        return False
    
    # 테스트 데이터 업로드
    print("\n4️⃣ 테스트 데이터 업로드...")
    try:
        test_docs = [
            {
                "text": "네이버 파워링크는 검색결과 상단에 노출되는 광고 상품입니다. 클릭당 과금(CPC) 방식으로 운영되며, 품질지수가 높을수록 낮은 입찰가로도 상위 노출이 가능합니다.",
                "metadata": {
                    "source": "테스트",
                    "chapter": "Chapter 1",
                    "chunk_id": 0
                }
            },
            {
                "text": "구글 애즈(Google Ads)는 전 세계에서 가장 큰 검색광고 플랫폼입니다. 키워드 광고, 디스플레이 광고, 유튜브 광고 등 다양한 광고 형태를 제공합니다.",
                "metadata": {
                    "source": "테스트",
                    "chapter": "Chapter 2",
                    "chunk_id": 1
                }
            }
        ]
        
        for doc in test_docs:
            rag.add_document(doc["text"], doc["metadata"])
        
        print(f"✅ 테스트 데이터 {len(test_docs)}개 업로드 완료!")
    except Exception as e:
        print(f"❌ 테스트 데이터 업로드 실패: {e}")
        return False
    
    # 검색 테스트
    print("\n5️⃣ 유사도 검색 테스트...")
    try:
        query = "네이버 광고 품질지수란?"
        results = rag.search_similar_content(query, top_k=2)
        
        print(f"✅ 검색 완료! {len(results)}개 결과 발견")
        for i, result in enumerate(results, 1):
            print(f"\n   결과 {i}:")
            print(f"   - 텍스트: {result['text'][:100]}...")
            print(f"   - 유사도: {result['score']:.4f}")
    except Exception as e:
        print(f"❌ 검색 테스트 실패: {e}")
        return False
    
    # 응답 생성 테스트
    print("\n6️⃣ AI 응답 생성 테스트...")
    try:
        prompt = """다음 정보를 바탕으로 질문에 답변해주세요:

정보: 네이버 파워링크는 검색결과 상단에 노출되는 광고 상품입니다. 클릭당 과금(CPC) 방식으로 운영되며, 품질지수가 높을수록 낮은 입찰가로도 상위 노출이 가능합니다.

질문: 네이버 파워링크는 어떤 과금 방식인가요?"""
        
        import asyncio
        response = asyncio.run(rag.generate_response(prompt))
        
        print("✅ AI 응답 생성 성공!")
        print(f"\n응답: {response}")
    except Exception as e:
        print(f"❌ AI 응답 생성 실패: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 모든 테스트 통과!")
    print("=" * 50)
    return True


if __name__ == "__main__":
    success = test_connection()
    
    if success:
        print("\n✅ 시스템이 정상적으로 작동합니다!")
        print("이제 교재를 업로드할 수 있습니다:")
        print("  python upload_textbook.py")
    else:
        print("\n❌ 시스템에 문제가 있습니다. 위의 오류를 확인해주세요.")