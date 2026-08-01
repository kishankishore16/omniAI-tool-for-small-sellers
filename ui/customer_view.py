"""
OmniAI — Customer Chat View
RAG-powered shopping assistant chatbot interface.
"""

import streamlit as st
import uuid


def render(api_request_fn):
    """Render the customer-facing chatbot interface."""
    st.markdown(
        """
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h1 class='gradient-text' style='font-size: 2.5rem; margin-bottom: 0.5rem;'>
                Chat with OmniAI
            </h1>
            <p style='color: #9ca3af; font-size: 1.1rem;'>
                Your intelligent personal shopping assistant — ask about products,
                prices, and recommendations.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Session State ────────────────────────────────────────────
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())

    # ── Sidebar Controls ─────────────────────────────────────────
    with st.sidebar:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.session_state.conversation_id = str(uuid.uuid4())
            st.rerun()

    # ── Chat Area ────────────────────────────────────────────────
    chat_container = st.container()

    with chat_container:
        # Welcome state with suggestion buttons
        if not st.session_state.messages:
            st.markdown(
                """
                <div class="glass-card" style="text-align: center; margin: 2rem auto;
                     max-width: 600px;">
                    <h3>👋 Hello! How can I help you shop today?</h3>
                    <p style="color: #9ca3af;">
                        I can help you find products, compare prices, and give
                        personalized recommendations based on our catalog.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                "<p style='text-align: center; color: #6b7280;'>Try asking:</p>",
                unsafe_allow_html=True,
            )

            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("💍 What jewelry do you have?", use_container_width=True):
                    _process_message("What jewelry do you have?", api_request_fn)
            with c2:
                if st.button("🎁 Gift options under $100", use_container_width=True):
                    _process_message(
                        "Show me gift options under $100", api_request_fn
                    )
            with c3:
                if st.button("⭐ Most popular items?", use_container_width=True):
                    _process_message(
                        "What's your most popular item?", api_request_fn
                    )

        # Display conversation history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("products"):
                    with st.expander("📦 View referenced products"):
                        for p in msg["products"]:
                            score = p.get("relevance_score", 0)
                            score_bar = "🟢" if score > 0.7 else "🟡" if score > 0.4 else "🔴"
                            st.markdown(
                                f"{score_bar} **{p.get('name', 'Product')}** — "
                                f"${p.get('price', 0.0):.2f} "
                                f"*(relevance: {score:.0%})*"
                            )

    # ── Chat Input ───────────────────────────────────────────────
    if prompt := st.chat_input("Ask about our products..."):
        _process_message(prompt, api_request_fn)


def _process_message(prompt: str, api_request_fn):
    """Send a message to the RAG agent and display the response."""
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Searching products and generating response..."):
            payload = {
                "message": prompt,
                "conversation_id": st.session_state.conversation_id,
            }
            response = api_request_fn("POST", "/api/chat", json=payload)

            if response:
                answer = response.get("answer", "Sorry, I couldn't generate a response.")
                products = response.get("source_products", [])

                st.markdown(answer)

                if products:
                    with st.expander("📦 View referenced products"):
                        for p in products:
                            score = p.get("relevance_score", 0)
                            score_bar = "🟢" if score > 0.7 else "🟡" if score > 0.4 else "🔴"
                            st.markdown(
                                f"{score_bar} **{p.get('name', 'Product')}** — "
                                f"${p.get('price', 0.0):.2f} "
                                f"*(relevance: {score:.0%})*"
                            )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "products": products,
                })
            else:
                error_msg = (
                    "Sorry, I'm having trouble connecting to the backend. "
                    "Please make sure the API server is running."
                )
                st.markdown(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                })

    st.rerun()
