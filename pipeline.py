import streamlit as st
import re
import time
from tools import web_search, scrape_url
from agents import writer_chain, critic_chain

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind — Multi-Agent Research System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #080D1A !important;
    color: #E2E8F0;
    font-family: 'Inter', sans-serif;
}
[data-testid="stSidebar"] {
    background: #0D1527 !important;
    border-right: 1px solid rgba(0, 212, 255, 0.12);
}
[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer, header { visibility: hidden; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0D1527; }
::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.3); border-radius: 2px; }

.hero {
    background: linear-gradient(135deg, #0D1527 0%, #0A0F1E 50%, #0D1527 100%);
    border: 1px solid rgba(0,212,255,0.15);
    border-radius: 16px;
    padding: 40px 48px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -10%;
    width: 60%;
    height: 200%;
    background: radial-gradient(ellipse, rgba(0,212,255,0.06) 0%, transparent 70%);
    pointer-events: none;
}
.hero-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 500;
    color: #00D4FF;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 12px;
}
.hero-title {
    font-size: 38px;
    font-weight: 700;
    color: #F0F6FF;
    letter-spacing: -1px;
    line-height: 1.15;
    margin-bottom: 12px;
}
.hero-title span { color: #00D4FF; }
.hero-subtitle {
    font-size: 15px;
    color: #7B93B8;
    font-weight: 400;
    line-height: 1.6;
    max-width: 540px;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(0,212,255,0.08);
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 20px;
    padding: 4px 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #00D4FF;
    margin-top: 20px;
    margin-right: 8px;
}
.hero-badge-amber {
    background: rgba(255,179,0,0.08);
    border-color: rgba(255,179,0,0.2);
    color: #FFB300;
}
.pipeline-track {
    display: flex;
    align-items: center;
    gap: 0;
    background: #0D1527;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 28px;
    overflow: hidden;
}
.pipeline-step {
    display: flex;
    align-items: center;
    flex: 1;
    position: relative;
}
.step-node {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: 2px solid rgba(255,255,255,0.1);
    background: #131B2E;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    transition: all 0.3s ease;
    flex-shrink: 0;
    z-index: 2;
    position: relative;
}
.step-node.active {
    border-color: #00D4FF;
    background: rgba(0,212,255,0.12);
    box-shadow: 0 0 12px rgba(0,212,255,0.3);
    animation: pulse-node 1.5s infinite;
}
.step-node.done {
    border-color: #00E676;
    background: rgba(0,230,118,0.12);
}
.step-node.error {
    border-color: #FF5252;
    background: rgba(255,82,82,0.12);
}
@keyframes pulse-node {
    0%, 100% { box-shadow: 0 0 8px rgba(0,212,255,0.3); }
    50% { box-shadow: 0 0 20px rgba(0,212,255,0.6); }
}
.step-label {
    margin-left: 10px;
    font-size: 12px;
    font-weight: 500;
    color: #4A6080;
    font-family: 'JetBrains Mono', monospace;
    transition: color 0.3s;
}
.step-label.active { color: #00D4FF; }
.step-label.done { color: #00E676; }
.step-connector {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(255,255,255,0.05), rgba(255,255,255,0.05));
    margin: 0 8px;
    transition: background 0.3s;
}
.step-connector.done {
    background: linear-gradient(90deg, rgba(0,230,118,0.3), rgba(0,230,118,0.1));
}
.input-card {
    background: #0D1527;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 28px 32px;
    margin-bottom: 24px;
}
.input-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 500;
    color: #00D4FF;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 16px;
}
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input {
    background: #131B2E !important;
    border: 1.5px solid rgba(0,212,255,0.2) !important;
    border-radius: 8px !important;
    color: #E2E8F0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
    padding: 14px 16px !important;
}
[data-testid="stTextArea"] textarea:focus,
[data-testid="stTextInput"] input:focus {
    border-color: rgba(0,212,255,0.5) !important;
    box-shadow: 0 0 0 3px rgba(0,212,255,0.08) !important;
    outline: none !important;
}
[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #00D4FF, #0094CC) !important;
    color: #050A14 !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 12px 32px !important;
    border-radius: 8px !important;
    border: none !important;
    letter-spacing: 0.3px;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 16px rgba(0,212,255,0.25) !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(0,212,255,0.35) !important;
}
[data-testid="stButton"] > button[kind="secondary"] {
    background: transparent !important;
    color: #7B93B8 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    padding: 10px 20px !important;
}
.agent-card {
    background: #0D1527;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    margin-bottom: 20px;
    overflow: hidden;
}
.agent-card-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 20px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.02);
}
.agent-icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
}
.agent-icon-search { background: rgba(0,212,255,0.12); }
.agent-icon-scrape { background: rgba(139,92,246,0.12); }
.agent-icon-writer { background: rgba(0,230,118,0.12); }
.agent-icon-critic { background: rgba(255,179,0,0.12); }
.agent-card-title {
    font-size: 13px;
    font-weight: 600;
    color: #D0E0F5;
    letter-spacing: 0.2px;
}
.agent-card-subtitle {
    font-size: 11px;
    color: #4A6080;
    font-family: 'JetBrains Mono', monospace;
}
.status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    margin-left: auto;
    flex-shrink: 0;
}
.status-dot-running { background: #00D4FF; animation: blink 1s infinite; }
.status-dot-done { background: #00E676; }
.status-dot-error { background: #FF5252; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
.agent-card-body {
    padding: 20px;
    font-size: 14px;
    color: #A0B4CC;
    line-height: 1.7;
    font-family: 'JetBrains Mono', monospace;
    max-height: 320px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-word;
}
.agent-card-body.prose {
    font-family: 'Inter', sans-serif;
    font-size: 14.5px;
    color: #C8D8EA;
    line-height: 1.8;
}
.url-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(139,92,246,0.1);
    border: 1px solid rgba(139,92,246,0.25);
    border-radius: 20px;
    padding: 4px 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #A78BFA;
    margin-bottom: 12px;
    word-break: break-all;
}
.critique-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
}
.score-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 4px;
    background: rgba(255,179,0,0.12);
    border: 1px solid rgba(255,179,0,0.25);
    color: #FFB300;
}
.sidebar-section { margin-bottom: 24px; }
.sidebar-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 500;
    color: #4A6080;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.history-item {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
    cursor: pointer;
    font-size: 12px;
    color: #7B93B8;
    line-height: 1.5;
    transition: all 0.2s;
}
.history-item:hover {
    background: rgba(0,212,255,0.05);
    border-color: rgba(0,212,255,0.15);
    color: #C0D4E8;
}
.stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    font-size: 12px;
}
.stat-label { color: #4A6080; }
.stat-value {
    color: #00D4FF;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 500;
}
.section-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,212,255,0.15), transparent);
    margin: 28px 0;
}
.copy-row {
    display: flex;
    justify-content: flex-end;
    padding: 8px 16px;
    border-top: 1px solid rgba(255,255,255,0.05);
    background: rgba(255,255,255,0.01);
    gap: 8px;
}
[data-testid="stExpander"] {
    background: #0D1527 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary {
    color: #A0B4CC !important;
    font-size: 13px !important;
}
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #00D4FF, #00A8CC) !important;
}
[data-testid="stSelectbox"] select,
[data-testid="stSelectbox"] > div > div {
    background: #131B2E !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #E2E8F0 !important;
    border-radius: 8px !important;
}
[data-testid="stMetric"] {
    background: #0D1527;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 16px 20px;
}
[data-testid="stMetric"] label { color: #4A6080 !important; font-size: 12px !important; }
[data-testid="stMetricValue"] { color: #00D4FF !important; font-family: 'JetBrains Mono', monospace !important; }
[data-testid="stCheckbox"] label { color: #7B93B8 !important; font-size: 13px !important; }
[data-testid="stSlider"] > div > div > div { background: rgba(0,212,255,0.3) !important; }
</style>
""", unsafe_allow_html=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────
def extract_first_url(text):
    urls = re.findall(r"https?://[^\s]+", text)
    return urls[0] if urls else None

def init_session():
    defaults = {
        "history": [],
        "run_count": 0,
        "last_topic": "",
        "current_state": None,
        "is_running": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:20px 4px 24px;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#00D4FF;letter-spacing:3px;text-transform:uppercase;margin-bottom:6px;">ResearchMind</div>
        <div style="font-size:19px;font-weight:700;color:#F0F6FF;letter-spacing:-0.5px;">Control Panel</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label">⚙️ &nbsp;Pipeline Settings</div>', unsafe_allow_html=True)
    max_chars = st.slider("Max output chars per agent", 500, 5000, 2000, 250)
    search_only = st.checkbox("Search only (skip write & critique)", value=False)
    show_raw = st.checkbox("Show raw search results", value=False)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-label">📊 &nbsp;Session Stats</div>', unsafe_allow_html=True)

    # ── FIX 1: pre-build the last_topic display string outside f-string ──
    run_count_val = st.session_state.run_count
    history_count_val = len(st.session_state.history)
    last_topic_raw = st.session_state.last_topic
    if len(last_topic_raw) > 22:
        last_topic_display = last_topic_raw[:22] + "…"
    else:
        last_topic_display = last_topic_raw if last_topic_raw else "—"

    st.markdown(
        '<div class="stat-row">'
        '<span class="stat-label">Runs this session</span>'
        '<span class="stat-value">' + str(run_count_val) + '</span>'
        '</div>'
        '<div class="stat-row">'
        '<span class="stat-label">Reports generated</span>'
        '<span class="stat-value">' + str(history_count_val) + '</span>'
        '</div>'
        '<div class="stat-row">'
        '<span class="stat-label">Last topic</span>'
        '<span class="stat-value" style="color:#A78BFA;font-size:10px;max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">'
        + last_topic_display +
        '</span>'
        '</div>',
        unsafe_allow_html=True
    )

    if st.session_state.history:
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-label">🕘 &nbsp;Search History</div>', unsafe_allow_html=True)
        for item in reversed(st.session_state.history[-6:]):
            st.markdown('<div class="history-item">🔍 ' + item + '</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-label">🤖 &nbsp;Active Agents</div>', unsafe_allow_html=True)
    agents_info = [
        ("🔍", "WebSearch", "Tavily / SerpAPI"),
        ("🌐", "Scraper", "BeautifulSoup"),
        ("✍️", "Writer", "LLM Chain"),
        ("🎯", "Critic", "LLM Chain"),
    ]
    for icon, name, detail in agents_info:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.04);">'
            '<span style="font-size:14px;">' + icon + '</span>'
            '<div>'
            '<div style="font-size:12px;color:#C0D4E8;font-weight:500;">' + name + '</div>'
            '<div style="font-size:10px;color:#4A6080;font-family:JetBrains Mono,monospace;">' + detail + '</div>'
            '</div>'
            '<div style="margin-left:auto;width:6px;height:6px;border-radius:50%;background:#00E676;box-shadow:0 0 6px rgba(0,230,118,0.5);"></div>'
            '</div>',
            unsafe_allow_html=True
        )


# ─── Main Content ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">// MULTI-AGENT RESEARCH SYSTEM</div>
    <div class="hero-title">ResearchMind <span>360</span></div>
    <div class="hero-subtitle">Autonomous research pipeline powered by four specialized AI agents. Enter a topic and watch them collaborate — search, scrape, write, critique.</div>
    <div style="margin-top:20px;">
        <span class="hero-badge">🔍 WebSearch</span>
        <span class="hero-badge">🌐 Scraper</span>
        <span class="hero-badge">✍️ Writer</span>
        <span class="hero-badge hero-badge-amber">🎯 Critic</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ─── Pipeline Tracker ─────────────────────────────────────────────────────────
def get_step_class(step_index, active_step):
    if active_step is None:
        return "idle", "idle"
    if step_index < active_step:
        return "done", "done"
    if step_index == active_step:
        return "active", "active"
    return "idle", "idle"

def render_pipeline_tracker(active_step=None):
    steps = ["SEARCH", "SCRAPE", "WRITE", "CRITIQUE"]
    icons = ["🔍", "🌐", "✍️", "🎯"]
    html = '<div class="pipeline-track">'
    for i, (step, icon) in enumerate(zip(steps, icons)):
        node_cls, label_cls = get_step_class(i, active_step)
        html += '<div class="pipeline-step">'
        html += '<div class="step-node ' + node_cls + '">' + icon + '</div>'
        html += '<span class="step-label ' + label_cls + '">' + step + '</span>'
        html += '</div>'
        if i < len(steps) - 1:
            connector_cls = "done" if (active_step is not None and i < active_step) else ""
            html += '<div class="step-connector ' + connector_cls + '"></div>'
    html += '</div>'
    return html

pipeline_placeholder = st.empty()
pipeline_placeholder.markdown(render_pipeline_tracker(None), unsafe_allow_html=True)

# ─── Input Area ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="input-card">
    <div class="input-label">// Research Topic</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([5, 1], gap="medium")
with col1:
    topic = st.text_input(
        label="topic_input",
        label_visibility="collapsed",
        placeholder="e.g. 'Latest advancements in quantum computing 2024' or 'Impact of AI on healthcare'",
        key="topic_input"
    )
with col2:
    run_btn = st.button("▶ Run Pipeline", type="primary", use_container_width=True)

st.markdown("""
<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:24px;margin-top:-8px;">
    <span style="font-size:11px;color:#4A6080;align-self:center;font-family:'JetBrains Mono',monospace;">Try:</span>
</div>
""", unsafe_allow_html=True)

sugg_cols = st.columns(4)
suggestions = [
    "Generative AI in 2025",
    "Electric vehicle market trends",
    "Climate change latest research",
    "Quantum computing breakthroughs"
]
for i, sugg in enumerate(suggestions):
    with sugg_cols[i]:
        if st.button(sugg, key="sugg_" + str(i), type="secondary", use_container_width=True):
            topic = sugg
            run_btn = True


# ─── Pipeline Execution ───────────────────────────────────────────────────────
if run_btn and topic:
    st.session_state.run_count += 1
    st.session_state.last_topic = topic
    if topic not in st.session_state.history:
        st.session_state.history.append(topic)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── FIX 2: pre-build topic display string outside f-string ──
    topic_display = '"' + topic + '"'
    st.markdown(
        '<div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">'
        '<div style="width:3px;height:28px;background:linear-gradient(180deg,#00D4FF,#0066AA);border-radius:2px;"></div>'
        '<div>'
        '<div style="font-size:12px;color:#4A6080;font-family:JetBrains Mono,monospace;letter-spacing:1px;text-transform:uppercase;">Researching</div>'
        '<div style="font-size:20px;font-weight:700;color:#F0F6FF;letter-spacing:-0.5px;">' + topic_display + '</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    # ── STEP 1: Search ────────────────────────────────────────────────────
    pipeline_placeholder.markdown(render_pipeline_tracker(0), unsafe_allow_html=True)

    search_card = st.empty()
    search_card.markdown("""
    <div class="agent-card">
        <div class="agent-card-header">
            <div class="agent-icon agent-icon-search">🔍</div>
            <div>
                <div class="agent-card-title">Web Search Agent</div>
                <div class="agent-card-subtitle">Searching the web...</div>
            </div>
            <div class="status-dot status-dot-running"></div>
        </div>
        <div class="agent-card-body">Querying search engine...</div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner(""):
        search_results = web_search.invoke({"query": topic})

    # ── FIX 3: build search card HTML with plain string concat, no backslashes in f-string ──
    search_len = len(search_results)
    topic_short = topic[:30]
    search_display = search_results[:max_chars] + ("…" if search_len > max_chars else "")

    if show_raw:
        search_body_html = '<div class="agent-card-body">' + search_display + '</div>'
    else:
        search_body_html = (
            '<div style="padding:12px 20px 16px;font-size:13px;color:#4A6080;">'
            '✓ Search complete — '
            '<span style="color:#00E676;">' + str(search_len) + ' chars</span>'
            ' retrieved. Toggle "Show raw results" in sidebar to view.'
            '</div>'
        )

    search_card.markdown(
        '<div class="agent-card">'
        '<div class="agent-card-header">'
        '<div class="agent-icon agent-icon-search">🔍</div>'
        '<div>'
        '<div class="agent-card-title">Web Search Agent</div>'
        '<div class="agent-card-subtitle">search.invoke(query: "' + topic_short + '...") → ' + str(search_len) + ' chars returned</div>'
        '</div>'
        '<div class="status-dot status-dot-done"></div>'
        '</div>'
        + search_body_html +
        '</div>',
        unsafe_allow_html=True
    )

    # ── STEP 2: Scrape ────────────────────────────────────────────────────
    pipeline_placeholder.markdown(render_pipeline_tracker(1), unsafe_allow_html=True)

    url = extract_first_url(search_results)

    # ── FIX 4: ternary with string operations moved outside f-string ──
    if url:
        scrape_subtitle = "Extracting: " + url[:60] + "..."
        scrape_body_loading = "Scraping content from URL..."
    else:
        scrape_subtitle = "No URL detected in results"
        scrape_body_loading = "⚠ No URL found — skipping scrape step."

    scrape_card = st.empty()
    scrape_card.markdown(
        '<div class="agent-card">'
        '<div class="agent-card-header">'
        '<div class="agent-icon agent-icon-scrape">🌐</div>'
        '<div>'
        '<div class="agent-card-title">URL Scraper Agent</div>'
        '<div class="agent-card-subtitle">' + scrape_subtitle + '</div>'
        '</div>'
        '<div class="status-dot status-dot-running"></div>'
        '</div>'
        '<div class="agent-card-body">' + scrape_body_loading + '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    if url:
        with st.spinner(""):
            scraped = scrape_url.invoke({"url": url})
    else:
        scraped = "No URL found in search results."

    scraped_len = len(scraped)
    scrape_display = scraped[:max_chars] + ("…" if scraped_len > max_chars else "")
    url_chip_html = '<div class="url-chip">🔗 ' + url + '</div>' if url else ''

    scrape_card.markdown(
        '<div class="agent-card">'
        '<div class="agent-card-header">'
        '<div class="agent-icon agent-icon-scrape">🌐</div>'
        '<div>'
        '<div class="agent-card-title">URL Scraper Agent</div>'
        '<div class="agent-card-subtitle">scrape_url.invoke(url: "...") → ' + str(scraped_len) + ' chars</div>'
        '</div>'
        '<div class="status-dot status-dot-done"></div>'
        '</div>'
        '<div class="agent-card-body">' + url_chip_html + scrape_display + '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    if search_only:
        pipeline_placeholder.markdown(render_pipeline_tracker(2), unsafe_allow_html=True)
        st.info("Search-only mode enabled. Skipping write and critique steps.")
        st.stop()

    # ── STEP 3: Write ─────────────────────────────────────────────────────
    pipeline_placeholder.markdown(render_pipeline_tracker(2), unsafe_allow_html=True)

    write_card = st.empty()
    write_card.markdown("""
    <div class="agent-card">
        <div class="agent-card-header">
            <div class="agent-icon agent-icon-writer">✍️</div>
            <div>
                <div class="agent-card-title">Writer Agent</div>
                <div class="agent-card-subtitle">Composing research report...</div>
            </div>
            <div class="status-dot status-dot-running"></div>
        </div>
        <div class="agent-card-body prose">Synthesizing research data into a structured report...</div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner(""):
        report = writer_chain.invoke({
            "topic": topic,
            "research": search_results + "\n\n" + scraped
        })

    report_len = len(report)
    report_display = report[:max_chars] + ("…" if report_len > max_chars else "")

    write_card.markdown(
        '<div class="agent-card">'
        '<div class="agent-card-header">'
        '<div class="agent-icon agent-icon-writer">✍️</div>'
        '<div>'
        '<div class="agent-card-title">Writer Agent</div>'
        '<div class="agent-card-subtitle">writer_chain.invoke(topic: "...") → report generated</div>'
        '</div>'
        '<div class="status-dot status-dot-done"></div>'
        '</div>'
        '<div class="agent-card-body prose">' + report_display + '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    with st.expander("📄 View Full Report", expanded=True):
        st.markdown(
            '<div style="padding:8px 4px;font-family:Inter,sans-serif;font-size:14.5px;color:#C8D8EA;line-height:1.8;white-space:pre-wrap;">'
            + report +
            '</div>',
            unsafe_allow_html=True
        )
        # ── FIX 5: safe_topic pre-built before download_button ──
        safe_topic = topic[:30].replace(" ", "_")
        st.download_button(
            label="⬇ Download Report (.txt)",
            data=report,
            file_name="research_" + safe_topic + ".txt",
            mime="text/plain"
        )

    # ── STEP 4: Critique ──────────────────────────────────────────────────
    pipeline_placeholder.markdown(render_pipeline_tracker(3), unsafe_allow_html=True)

    critique_card = st.empty()
    critique_card.markdown("""
    <div class="agent-card">
        <div class="agent-card-header">
            <div class="agent-icon agent-icon-critic">🎯</div>
            <div>
                <div class="agent-card-title">Critic Agent</div>
                <div class="agent-card-subtitle">Evaluating report quality...</div>
            </div>
            <div class="status-dot status-dot-running"></div>
        </div>
        <div class="agent-card-body prose">Analyzing report for accuracy, depth, and gaps...</div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner(""):
        feedback = critic_chain.invoke({"report": report})

    feedback_len = len(feedback)
    feedback_display = feedback[:max_chars] + ("…" if feedback_len > max_chars else "")

    critique_card.markdown(
        '<div class="agent-card" style="border-color:rgba(255,179,0,0.15);">'
        '<div class="agent-card-header" style="background:rgba(255,179,0,0.03);">'
        '<div class="agent-icon agent-icon-critic">🎯</div>'
        '<div>'
        '<div class="agent-card-title">Critic Agent</div>'
        '<div class="agent-card-subtitle">critic_chain.invoke(report: "...") → feedback ready</div>'
        '</div>'
        '<div class="status-dot status-dot-done" style="background:#FFB300;box-shadow:0 0 6px rgba(255,179,0,0.4);"></div>'
        '</div>'
        '<div class="agent-card-body prose" style="border-left:2px solid rgba(255,179,0,0.25);">'
        + feedback_display +
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    with st.expander("🎯 View Full Critique", expanded=False):
        st.markdown(
            '<div style="padding:8px 4px;font-family:Inter,sans-serif;font-size:14.5px;color:#C8D8EA;line-height:1.8;white-space:pre-wrap;">'
            + feedback +
            '</div>',
            unsafe_allow_html=True
        )

    # ── Pipeline Complete ──────────────────────────────────────────────────
    pipeline_placeholder.markdown(render_pipeline_tracker(4), unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Search Data", str(search_len) + " chars")
    with m2:
        st.metric("Scraped Content", str(scraped_len) + " chars")
    with m3:
        st.metric("Report Length", str(report_len) + " chars")
    with m4:
        st.metric("Critique Length", str(feedback_len) + " chars")

    st.session_state.current_state = {
        "topic": topic,
        "search_results": search_results,
        "scraped_content": scraped,
        "report": report,
        "feedback": feedback
    }

    st.markdown("""
    <div style="background:rgba(0,230,118,0.05);border:1px solid rgba(0,230,118,0.15);border-radius:10px;padding:16px 20px;margin-top:16px;display:flex;align-items:center;gap:12px;">
        <span style="font-size:18px;">✅</span>
        <div>
            <div style="font-size:13px;font-weight:600;color:#00E676;">Pipeline Complete</div>
            <div style="font-size:12px;color:#4A6080;margin-top:2px;">All 4 agents ran successfully. Report and critique are ready.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif not topic and run_btn:
    st.warning("Please enter a research topic before running the pipeline.")

# ── Empty state ───────────────────────────────────────────────────────────────
if not run_btn or not topic:
    st.markdown("""
    <div style="text-align:center;padding:60px 40px;opacity:0.5;">
        <div style="font-size:48px;margin-bottom:16px;">🧠</div>
        <div style="font-size:15px;color:#4A6080;font-family:'JetBrains Mono',monospace;">Enter a topic above to activate the pipeline</div>
        <div style="font-size:12px;color:#2A3F5A;margin-top:8px;">4 agents · search → scrape → write → critique</div>
    </div>
    """, unsafe_allow_html=True)
























































# from tools import web_search
# from tools import scrape_url

# from agents import writer_chain
# from agents import critic_chain

# import re


# def extract_first_url(text):

#     urls = re.findall(
#         r"https?://[^\s]+",
#         text
#     )

#     return urls[0] if urls else None


# def run_research_pipeline(topic):

#     state = {}

#     print("\n" + "-"*50)
#     print("STEP 1 : SEARCH")
#     print("-"*50)

#     search_results = web_search.invoke(
#         {"query": topic}
#     )

#     state["search_results"] = search_results

#     print(search_results[:1000])

#     print("\n" + "-"*50)
#     print("STEP 2 : SCRAPE")
#     print("-"*50)

#     url = extract_first_url(search_results)

#     if url:

#         scraped_content = scrape_url.invoke(
#             {"url": url}
#         )

#     else:

#         scraped_content = "No URL found."

#     state["scraped_content"] = scraped_content

#     print(scraped_content[:1000])

#     print("\n" + "-"*50)
#     print("STEP 3 : WRITE REPORT")
#     print("-"*50)

#     report = writer_chain.invoke({
#         "topic": topic,
#         "research":
#             state["search_results"]
#             + "\n\n"
#             + state["scraped_content"]
#     })

#     state["report"] = report

#     print(report)

#     print("\n" + "-"*50)
#     print("STEP 4 : CRITIQUE")
#     print("-"*50)

#     feedback = critic_chain.invoke({
#         "report": report
#     })

#     state["feedback"] = feedback

#     print(feedback)

#     return state


# if __name__ == "__main__":

#     topic = input(
#         "Enter a research topic: "
#     )

#     run_research_pipeline(topic)