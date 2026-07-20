import streamlit as st

from ai.confluence_article_generator import generate_confluence_article
from progress.progress_manager import ProgressManager
from repositories.memory_repository import MemoryRepository
from services.user_artifact_service import save_user_generated_artifact


def render_confluence_article_tab(memory_repository: MemoryRepository):
    st.header("Confluence Article Generator")
    st.caption("Generate Confluence-ready articles from Project Memory.")

    memory_items = memory_repository.get_memory_items()
    st.info(f"Project Memory contains {len(memory_items)} knowledge items.")

    if not memory_items:
        st.warning("Add and process at least one source before generating Confluence articles.")
        return

    article_title = st.text_input(
        "Article title",
        placeholder="Example: Wallet Service Overview",
        key="confluence_generate_article_title",
    )

    col1, col2 = st.columns(2)

    with col1:
        article_type = st.selectbox(
            "Article type",
            options=[
                "project_overview",
                "functional_spec",
                "technical_overview",
                "decision_log",
                "risk_register",
                "onboarding",
            ],
            format_func=lambda value: {
                "project_overview": "Project Overview",
                "functional_spec": "Functional Specification",
                "technical_overview": "Technical/System Overview",
                "decision_log": "Decision Log",
                "risk_register": "Risk Register",
                "onboarding": "Onboarding Guide",
            }[value],
            key="confluence_generate_article_type",
        )

    with col2:
        audience = st.selectbox(
            "Audience",
            options=[
                "business_analyst",
                "system_analyst",
                "developer",
                "product_manager",
                "qa",
                "mixed",
            ],
            format_func=lambda value: {
                "business_analyst": "Business Analyst",
                "system_analyst": "System Analyst",
                "developer": "Developer",
                "product_manager": "Product Manager",
                "qa": "QA",
                "mixed": "Mixed team",
            }[value],
            key="confluence_generate_audience",
        )

    additional_instructions = st.text_area(
        "Additional instructions",
        height=120,
        placeholder="Example: Focus on onboarding, keep it concise, include open questions.",
        key="confluence_generate_additional_instructions",
    )

    if st.button("Generate Confluence article", key="generate_confluence_article_button"):
        progress = ProgressManager("Generating Confluence article", total_steps=3)

        try:
            progress.step("Preparing Project Memory")
            progress.step("Generating Confluence article with Claude")

            article = generate_confluence_article(
                memory_items=memory_items,
                article_type=article_type,
                article_title=article_title,
                audience=audience,
                additional_instructions=additional_instructions,
            )

            progress.step("Rendering article")

            if not article:
                st.warning("No article was generated. Project Memory may be too generic or empty.")
                progress.done("No article generated")
                return

            st.success("Confluence article generated.")
            st.markdown(article)

            save_user_generated_artifact(
                project_id=memory_repository.project_id,
                artifact_type="confluence_article",
                title=article_title.strip() or "Confluence Article",
                content=article,
                description="Confluence-ready article generated on user request.",
                metadata={"article_type": article_type, "audience": audience},
            )

            st.download_button(
                "Download article as Markdown",
                data=article,
                file_name="confluence_article.md",
                mime="text/markdown",
                key="download_confluence_article_markdown",
            )

            progress.done("Confluence article generation completed.")

        except Exception as exc:
            progress.error("Failed to generate Confluence article")
            st.exception(exc)

