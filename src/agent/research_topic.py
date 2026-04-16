from __future__ import annotations

import json
import re
from urllib.parse import urlparse

import requests
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field

from agent.graph_state import RouteInfo, State, TopicBrief
from agent.source_registry import get_domain_config


llm = init_chat_model("openai:gpt-4.1")

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}
MAX_SEARCH_RESULTS = 5
MAX_FETCHED_PAGES = 3


class SearchQueries(BaseModel):
    queries: list[str] = Field(default_factory=list)


class TopicBriefModel(BaseModel):
    topic_title: str
    factual_summary: str
    key_facts: list[str] = Field(default_factory=list)
    quantitative_data: list[str] = Field(default_factory=list)
    process_steps: list[str] = Field(default_factory=list)
    visual_elements: list[str] = Field(default_factory=list)
    spatial_relationships: list[str] = Field(default_factory=list)
    misconceptions_to_avoid: list[str] = Field(default_factory=list)
    narration_outline: list[str] = Field(default_factory=list)
    recommended_visual_mode: str
    source_registry: list[str] = Field(default_factory=list)
    source_snippets: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)


QUERY_PROMPT = """
You are preparing research queries for an educational animation system.

Given the user prompt, its route classification, and the domain, generate 2 to 4 focused
web search queries that will retrieve factual, visualizable, educational information.

Rules:
- For real-world named events or systems, include the exact entity name.
- Prefer queries that retrieve official sources, mission profiles, process breakdowns,
  timelines, mechanisms, or quantitative facts.
- Keep queries compact.
""".strip()


SYNTHESIS_PROMPT = """
You are building a factual topic brief for an educational animation pipeline.

Your output will drive scene planning for a math/science explainer video, so it must be:
- fact-focused,
- visually oriented,
- explicit about quantitative data when available,
- explicit about uncertainty or missing evidence.

Rules:
- Use the supplied web evidence as primary factual grounding when it exists.
- Do not invent specific dates, numbers, or named facts if the evidence does not support them.
- Prefer concrete process steps over vague summaries.
- recommended_visual_mode must be one of: conceptual, quantitative, hybrid.
- source_registry should contain the URLs you relied on most.
- source_snippets should contain short evidence-backed fact statements, not raw HTML.
""".strip()


INTERNAL_BRIEF_PROMPT = """
You are building a factual topic brief for a concept-focused educational animation.

Use strong general scientific knowledge, but avoid pretending to know specific recent
facts or measurements unless they are canonical and stable.

The brief must optimize for clear visual explanation:
- key facts,
- process steps,
- what objects need to be shown,
- common misconceptions,
- and what the narration should cover.

recommended_visual_mode must be one of: conceptual, quantitative, hybrid.
""".strip()


def _get_prompt(state: State) -> str:
    prompt = state.get("prompt", "").strip()
    if prompt:
        return prompt

    for message in reversed(state.get("messages", [])):
        content = getattr(message, "content", "")
        if isinstance(content, str) and content.strip():
            return content.strip()
    return ""


def _build_search_queries(prompt: str, route_info: RouteInfo) -> list[str]:
    domain_config = get_domain_config(route_info["domain"])
    response = llm.with_structured_output(SearchQueries).invoke(
        [
            ("system", QUERY_PROMPT),
            (
                "human",
                json.dumps(
                    {
                        "prompt": prompt,
                        "route_info": route_info,
                        "query_hints": list(domain_config.query_hints),
                    },
                    ensure_ascii=False,
                ),
            ),
        ]
    )
    queries = [query.strip() for query in response.queries if query.strip()]
    if queries:
        return queries[:4]

    entity_clause = " ".join(route_info.get("named_entities", []))
    return [f"{prompt} {entity_clause}".strip()]


def _search_with_duckduckgo(query: str) -> list[dict]:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        return []

    results: list[dict] = []
    try:
        with DDGS() as ddgs:
            for item in ddgs.text(query, max_results=MAX_SEARCH_RESULTS):
                results.append(
                    {
                        "title": item.get("title", ""),
                        "href": item.get("href", ""),
                        "body": item.get("body", ""),
                    }
                )
    except Exception:
        return []
    return results


def _filter_results(results: list[dict], route_info: RouteInfo) -> list[dict]:
    domain_config = get_domain_config(route_info["domain"])
    preferred_domains = domain_config.preferred_domains
    if not preferred_domains:
        return results[:MAX_SEARCH_RESULTS]

    preferred: list[dict] = []
    fallback: list[dict] = []
    for result in results:
        href = result.get("href", "")
        parsed = urlparse(href)
        hostname = parsed.hostname or ""
        if any(hostname.endswith(domain) for domain in preferred_domains):
            preferred.append(result)
        else:
            fallback.append(result)

    return (preferred + fallback)[:MAX_SEARCH_RESULTS]


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _fetch_page_excerpt(url: str) -> str:
    try:
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        return ""

    content_type = response.headers.get("content-type", "")
    if "html" not in content_type:
        return ""

    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return _clean_text(response.text)[:1500]

    soup = BeautifulSoup(response.text, "html.parser")
    title = _clean_text(soup.title.get_text(" ", strip=True)) if soup.title else ""

    paragraphs: list[str] = []
    for tag in soup.find_all(["p", "li"]):
        text = _clean_text(tag.get_text(" ", strip=True))
        if len(text) < 40:
            continue
        paragraphs.append(text)
        if sum(len(item) for item in paragraphs) > 1800:
            break

    excerpt = " ".join(paragraphs)[:1800]
    if title:
        return f"Title: {title}\nExcerpt: {excerpt}"
    return excerpt


def _collect_web_evidence(prompt: str, route_info: RouteInfo) -> tuple[list[str], list[str]]:
    if not route_info.get("needs_external_grounding", False):
        return [], []

    queries = _build_search_queries(prompt, route_info)
    seen_urls: set[str] = set()
    selected_urls: list[str] = []
    evidence_blocks: list[str] = []

    for query in queries:
        results = _filter_results(_search_with_duckduckgo(query), route_info)
        for result in results:
            href = result.get("href", "").strip()
            if not href or href in seen_urls:
                continue
            seen_urls.add(href)
            title = result.get("title", "").strip()
            snippet = result.get("body", "").strip()
            evidence = f"URL: {href}\nTitle: {title}\nSnippet: {snippet}"
            if len(selected_urls) < MAX_FETCHED_PAGES:
                page_excerpt = _fetch_page_excerpt(href)
                if page_excerpt:
                    evidence += f"\nPage Excerpt: {page_excerpt}"
                    selected_urls.append(href)
            evidence_blocks.append(evidence)
            if len(evidence_blocks) >= MAX_SEARCH_RESULTS:
                break
        if len(evidence_blocks) >= MAX_SEARCH_RESULTS:
            break

    return queries, evidence_blocks


def _synthesize_external_brief(
    prompt: str,
    route_info: RouteInfo,
    queries: list[str],
    evidence_blocks: list[str],
) -> TopicBrief:
    response = llm.with_structured_output(TopicBriefModel).invoke(
        [
            ("system", SYNTHESIS_PROMPT),
            (
                "human",
                json.dumps(
                    {
                        "prompt": prompt,
                        "route_info": route_info,
                        "search_queries": queries,
                        "web_evidence": evidence_blocks,
                    },
                    ensure_ascii=False,
                ),
            ),
        ]
    )
    return response.model_dump()


def _synthesize_internal_brief(prompt: str, route_info: RouteInfo) -> TopicBrief:
    response = llm.with_structured_output(TopicBriefModel).invoke(
        [
            ("system", INTERNAL_BRIEF_PROMPT),
            (
                "human",
                json.dumps(
                    {
                        "prompt": prompt,
                        "route_info": route_info,
                    },
                    ensure_ascii=False,
                ),
            ),
        ]
    )
    return response.model_dump()


def build_topic_brief(state: State) -> dict:
    prompt = _get_prompt(state)
    route_info = state.get("route_info")
    if not route_info:
        route_info = {
            "route": "concept_only",
            "needs_external_grounding": False,
            "named_entities": [],
            "time_sensitive": False,
            "domain": "general_science",
            "ambiguity_notes": [],
        }

    queries, evidence_blocks = _collect_web_evidence(prompt, route_info)
    if evidence_blocks:
        topic_brief = _synthesize_external_brief(prompt, route_info, queries, evidence_blocks)
    else:
        topic_brief = _synthesize_internal_brief(prompt, route_info)

    summary = topic_brief.get("factual_summary", "").strip()
    message = summary or f"Built topic brief for {topic_brief.get('topic_title', 'the topic')}."

    return {
        "messages": [AIMessage(content=message)],
        "topic_brief": topic_brief,
    }
