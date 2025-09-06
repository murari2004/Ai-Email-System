        from textblob import TextBlob
        import openai
        import os
        from typing import Tuple, List
        from app.core.config import OPENAI_API_KEY
        from app.services.rag_service import RAGService

        if OPENAI_API_KEY:
            openai.api_key = OPENAI_API_KEY

        class AIService:
            def __init__(self):
                self.rag = RAGService()

            def analyze_sentiment(self, text: str) -> Tuple[str, float]:
                blob = TextBlob(text or '')
                polarity = blob.sentiment.polarity
                if polarity > 0.1:
                    sentiment = 'positive'
                elif polarity < -0.1:
                    sentiment = 'negative'
                else:
                    sentiment = 'neutral'
                return sentiment, abs(polarity)

            def classify_priority(self, subject: str, body: str, sentiment: str) -> str:
                text = (subject + ' ' + body).lower()
                urgent_keywords = ['urgent','immediately','asap','cannot access','critical','failed','error']
                for k in urgent_keywords:
                    if k in text:
                        return 'urgent'
                if sentiment == 'negative':
                    return 'high'
                return 'normal'

            def generate_response(self, email_data: dict, max_tokens=250) -> dict:
                # retrieve context from RAG
                snippets = self.rag.retrieve(email_data.get('body',''), top_k=3)
                context_text = '\n'.join(snippets)
                prompt = f"""You are a professional customer support assistant. Use the KB context below to answer the customer's message.

KB:\n{context_text}\n
Customer message:\n{email_data.get('body')}\n
Respond empathetically, mention product if present, keep under 200 words."""
                if OPENAI_API_KEY:
                    try:
                        resp = openai.ChatCompletion.create(
                            model='gpt-3.5-turbo',
                            messages=[{'role':'system','content':'You are an expert support assistant.'},
                                      {'role':'user','content':prompt}],
                            max_tokens=max_tokens,
                            temperature=0.2
                        )
                        text = resp['choices'][0]['message']['content'].strip()
                        return {'response': text, 'model':'gpt-3.5-turbo'}
                    except Exception as e:
                        return {'response': f"Automated reply: Thanks for contacting us about '{email_data.get('subject')}'. We'll review.", 'model':'fallback'}
                else:
                    # simple template + include context end
                    return {'response': f"Hi {email_data.get('sender').split('@')[0]},\n\nThanks for contacting us about '{email_data.get('subject')}'. We are looking into this.\n\nContext:\n{context_text[:500]}\n\nBest, Support Team", 'model':'template'}
