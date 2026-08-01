"""
OmniAI — Admin Dashboard View
Upload products, browse the catalog, and view analytics.
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


def render(api_request_fn):
    """Render the admin dashboard with three tabs."""
    st.markdown("<h2>Admin Dashboard</h2>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(
        ["📤 Upload Product", "📦 Product Catalog", "📊 Analytics"]
    )

    # ══════════════════════════════════════════════════════════════
    # TAB 1: Upload Product
    # ══════════════════════════════════════════════════════════════
    with tab1:
        st.markdown("### Process New Product")

        col1, col2 = st.columns([1, 2])

        with col1:
            uploaded_file = st.file_uploader(
                "Upload Product Image", type=["jpg", "png", "webp"]
            )
            if uploaded_file:
                st.image(uploaded_file, use_container_width=True)

                if st.button("Process with OmniAI 🚀", use_container_width=True):
                    with st.spinner("Processing image through AI pipeline..."):
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        status_text.text("🔍 Analyzing image with Vision Agent...")
                        progress_bar.progress(20)

                        files = {
                            "file": (
                                uploaded_file.name,
                                uploaded_file.getvalue(),
                                uploaded_file.type,
                            )
                        }
                        result = api_request_fn("POST", "/api/process-product", files=files)

                        if result and result.get("success"):
                            # Update progress through steps
                            steps = result.get("processing_steps", [])
                            for i, step in enumerate(steps):
                                pct = min(100, 25 + (i + 1) * 20)
                                status_text.text(
                                    f"✅ {step['agent']} — {step['duration_ms']:.0f}ms"
                                )
                                progress_bar.progress(pct)

                            progress_bar.progress(100)
                            status_text.text("✅ Processing complete!")
                            st.session_state["latest_product"] = result
                            st.success("Product processed successfully!")
                            st.rerun()
                        elif result:
                            st.error(f"Processing failed: {result}")
                        else:
                            st.error(
                                "Could not connect to the API. Is the backend running?"
                            )

        with col2:
            if (
                "latest_product" in st.session_state
                and st.session_state["latest_product"]
            ):
                res = st.session_state["latest_product"]
                prod = res["product"]
                steps = res.get("processing_steps", [])
                features = prod.get("features", {})

                html_card = f"""
                <div class="glass-card">
                    <h2 class="gradient-text">{prod['name']}</h2>
                    <div style="display: flex; align-items: center; gap: 12px; margin: 12px 0;">
                        <span style="font-size: 2rem; font-weight: 700; color: #10b981;">
                            ${prod['price']:.2f}
                        </span>
                        <span style="color: #6b7280; font-size: 0.9rem;">
                            (${prod.get('confidence_low', 0):.2f} — ${prod.get('confidence_high', 0):.2f})
                        </span>
                    </div>
                    <span style="background: rgba(124,58,237,0.2); padding: 4px 14px; border-radius: 12px;
                                 font-size: 0.8rem; color: #a5b4fc;">
                        {features.get('product_type', 'Product')}
                    </span>
                    <hr style="border-color: rgba(255,255,255,0.1); margin: 16px 0;">
                    <p style="color: #d1d5db; line-height: 1.7;">{prod['description']}</p>
                    <h4 style="margin-top: 16px;">✨ Key Selling Points</h4>
                    <ul style="color: #9ca3af;">
                        {''.join([f"<li>{sp}</li>" for sp in prod.get('key_selling_points', [])])}
                    </ul>
                    <div style="margin-top: 20px; display: flex; gap: 8px; flex-wrap: wrap;">
                        {''.join([
                            f'<span style="background: rgba(255,255,255,0.05); '
                            f'border: 1px solid rgba(255,255,255,0.1); '
                            f'padding: 4px 10px; border-radius: 16px; font-size: 0.75rem; '
                            f'color: #a5b4fc;">{tag}</span>'
                            for tag in prod.get('seo_tags', [])
                        ])}
                    </div>
                </div>
                """
                st.markdown(html_card, unsafe_allow_html=True)

                # Processing timeline
                if steps:
                    st.markdown("### ⚡ Processing Timeline")
                    cols = st.columns(len(steps))
                    for i, step in enumerate(steps):
                        cols[i].metric(
                            step["agent"],
                            f"{step['duration_ms']:.0f}ms",
                        )

    # ══════════════════════════════════════════════════════════════
    # TAB 2: Product Catalog
    # ══════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### Product Catalog")

        products_res = api_request_fn("GET", "/api/products")

        if products_res and products_res.get("products"):
            products = products_res["products"]

            cols = st.columns(3)
            for i, p in enumerate(products):
                with cols[i % 3]:
                    img_src = f"{API_BASE_URL}{p.get('image_path', '')}"
                    features = p.get("features", {})
                    product_type = features.get("product_type", "Product") if isinstance(features, dict) else "Product"

                    st.markdown(
                        f"""
                        <div class="glass-card" style="margin-bottom: 20px;">
                            <img src="{img_src}"
                                 style="width: 100%; height: 200px; object-fit: cover;
                                        border-radius: 8px; margin-bottom: 12px;"
                                 onerror="this.style.display='none'">
                            <h4 style="margin-bottom: 4px; overflow: hidden;
                                       text-overflow: ellipsis; white-space: nowrap;">
                                {p['name']}
                            </h4>
                            <div style="display: flex; justify-content: space-between;
                                        align-items: center;">
                                <span style="font-size: 1.25rem; font-weight: bold;
                                             color: #10b981;">
                                    ${p['price']:.2f}
                                </span>
                                <span style="background: rgba(124,58,237,0.2);
                                             font-size: 0.7rem; padding: 2px 8px;
                                             border-radius: 10px; color: #a5b4fc;">
                                    {product_type}
                                </span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    with st.expander("Details & Actions"):
                        st.write(p.get("description", ""))
                        if p.get("key_selling_points"):
                            for sp in p["key_selling_points"]:
                                st.write(f"• {sp}")
                        if st.button(
                            "🗑️ Delete", key=f"del_{p['id']}", type="primary"
                        ):
                            api_request_fn("DELETE", f"/api/products/{p['id']}")
                            st.rerun()
        else:
            st.markdown(
                """
                <div class="glass-card" style="text-align: center; padding: 60px 20px;">
                    <h3>📦 No products yet</h3>
                    <p style="color: #9ca3af;">
                        Head over to the Upload tab to add your first product!
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ══════════════════════════════════════════════════════════════
    # TAB 3: Analytics
    # ══════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("### Platform Analytics")

        analytics = api_request_fn("GET", "/api/analytics")

        if analytics and analytics.get("total_products", 0) > 0:
            # ── Top Metrics Row ──────────────────────────────────
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Products", analytics["total_products"])
            c2.metric("Avg Price", f"${analytics['avg_price']:.2f}")

            model_metrics = analytics.get("model_metrics", {})
            c3.metric("Model R²", f"{model_metrics.get('r2', 0):.2f}")

            # Top category
            cats = analytics.get("category_breakdown", [])
            top_cat = max(cats, key=lambda x: x["count"])["product_type"] if cats else "N/A"
            c4.metric("Top Category", top_cat)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Charts Row ───────────────────────────────────────
            row2_c1, row2_c2 = st.columns(2)

            with row2_c1:
                st.markdown("#### Price Distribution")
                dist_data = analytics.get("price_distribution", [])
                if dist_data:
                    df_dist = pd.DataFrame(dist_data)
                    fig = px.bar(
                        df_dist, x="bin", y="count",
                        template="plotly_dark",
                        color_discrete_sequence=["#7c3aed"],
                    )
                    fig.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        margin=dict(t=10, l=0, r=0, b=0),
                        xaxis_title="Price Range",
                        yaxis_title="Count",
                    )
                    st.plotly_chart(fig, use_container_width=True)

            with row2_c2:
                st.markdown("#### Category Breakdown")
                if cats:
                    df_cat = pd.DataFrame(cats)
                    fig = px.pie(
                        df_cat, names="product_type", values="count",
                        template="plotly_dark", hole=0.4,
                        color_discrete_sequence=px.colors.sequential.Purp,
                    )
                    fig.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        margin=dict(t=10, l=0, r=0, b=0),
                    )
                    st.plotly_chart(fig, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Feature Importance ────────────────────────────────
            feat_data = analytics.get("feature_importance", {})
            if feat_data:
                st.markdown("#### 🎯 Pricing Model Feature Importance")
                df_feat = (
                    pd.DataFrame(
                        list(feat_data.items()), columns=["Feature", "Importance"]
                    )
                    .sort_values("Importance", ascending=True)
                )
                fig = px.bar(
                    df_feat, x="Importance", y="Feature", orientation="h",
                    template="plotly_dark",
                    color="Importance",
                    color_continuous_scale="Purp",
                )
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=10, l=0, r=0, b=0),
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown(
                """
                <div class="glass-card" style="text-align: center; padding: 60px 20px;">
                    <h3>📊 Not enough data</h3>
                    <p style="color: #9ca3af;">
                        Upload some products first to see analytics!
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
