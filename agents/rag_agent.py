import logging
import uuid
from typing import Any

from api.schemas import ChatResponse, SourceProduct, ProductRecord

logger = logging.getLogger(__name__)


class RAGAgent:
    """Retrieval-Augmented Generation Agent for customer queries.

    Combines vector similarity search (ChromaDB) with either Gemini LLM
    or template-based response generation to answer customer questions
    about products in the catalog.
    """

    def __init__(self, vector_store: Any, catalog_db: Any, api_key: str = ""):
        self.vector_store = vector_store
        self.catalog_db = catalog_db
        self.api_key = api_key
        self.model = None
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-2.0-flash")
                logger.info("RAGAgent: Gemini model initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini model: {e}")
                self.model = None

    def chat(self, message: str, conversation_id: str = "") -> ChatResponse:
        """Process a customer message and return an AI-generated response."""
        if not conversation_id:
            conversation_id = str(uuid.uuid4())

        try:
            # 1. Search vector store for similar products
            search_results = self.vector_store.search(message, top_k=5)

            # 2. Fetch full product records from catalog DB
            products: list[ProductRecord] = []
            for result in search_results:
                pid = int(result.get("id", 0))
                product = self.catalog_db.get_product(pid)
                if product:
                    products.append(product)

            # 3. Build source product references
            source_products = self._format_source_products(products, search_results)

            # 4. Generate response
            if self.model:
                try:
                    answer = self._gemini_response(message, products)
                except Exception as e:
                    logger.error(f"Gemini chat failed, falling back to template: {e}")
                    answer = self._template_response(message, products)
            else:
                answer = self._template_response(message, products)

            return ChatResponse(
                answer=answer,
                source_products=source_products,
                conversation_id=conversation_id,
            )

        except Exception as e:
            logger.error(f"Chat processing failed: {e}")
            return ChatResponse(
                answer="I'm sorry, I encountered an error while processing your request. Please try again.",
                source_products=[],
                conversation_id=conversation_id,
            )

    def _gemini_response(self, message: str, products: list[ProductRecord]) -> str:
        """Generate a response using Gemini with retrieved product context."""
        context_parts = []
        for p in products:
            context_parts.append(
                f"Product: {p.name}\n"
                f"Price: ${p.price:.2f}\n"
                f"Description: {p.description}\n"
                f"Tags: {', '.join(p.seo_tags[:5])}\n"
            )
        context = "\n".join(context_parts) if context_parts else "No products found in catalog."

        prompt = (
            "You are OmniAI Shopping Assistant — a friendly, knowledgeable helper "
            "for an online store. Use the product catalog context below to answer "
            "the customer's question. Be specific about products, mention prices, "
            "and highlight key features. If no relevant products are found, say so "
            "politely and suggest they check back later.\n\n"
            f"## Product Catalog Context\n{context}\n\n"
            f"## Customer Question\n{message}\n\n"
            "## Your Response (be helpful, concise, and friendly):"
        )
        response = self.model.generate_content(prompt)
        return response.text.strip()

    def _template_response(self, message: str, products: list[ProductRecord]) -> str:
        """Generate a structured response without LLM, using retrieved products."""
        if not products:
            return (
                "I don't have any products matching that query yet. "
                "Our catalog is growing — try uploading some products through "
                "the Admin Dashboard, then come back and ask me again! 🛍️"
            )

        answer = "Great question! Based on our catalog, here are some items you might love:\n\n"
        for i, p in enumerate(products, 1):
            answer += f"**{i}. {p.name}** — ${p.price:.2f}\n"
            if p.description:
                # Show first sentence of description
                first_sentence = p.description.split(".")[0] + "."
                answer += f"   {first_sentence}\n"
            if p.key_selling_points:
                answer += f"   ✨ {p.key_selling_points[0]}\n"
            answer += "\n"

        answer += "Would you like more details about any of these items?"
        return answer

    def _format_source_products(
        self, products: list[ProductRecord], search_results: list[dict]
    ) -> list[SourceProduct]:
        """Convert product records + search distances to SourceProduct list."""
        sources = []
        # Build distance lookup from search results
        distance_map = {}
        for r in search_results:
            distance_map[int(r.get("id", 0))] = r.get("distance", 1.0)

        for p in products:
            # Convert distance to relevance score (lower distance = higher relevance)
            pid = p.id or 0
            distance = distance_map.get(pid, 1.0)
            relevance = max(0.0, min(1.0, 1.0 - distance))
            sources.append(
                SourceProduct(
                    id=pid,
                    name=p.name,
                    price=p.price,
                    relevance_score=round(relevance, 3),
                )
            )
        return sources
