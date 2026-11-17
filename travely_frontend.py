import os
from datetime import datetime
from html import escape

import streamlit as st
from langchain_core.messages import HumanMessage
from main import app


# ---------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Travely | AI Travel Planner",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------
# Theme and reusable styling
# ---------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #07111f;
        --panel: #0d1b2b;
        --panel-2: #102238;
        --line: rgba(148, 181, 214, .16);
        --text: #edf5ff;
        --muted: #9bb0c7;
        --blue: #65a9ff;
        --cyan: #65e0d2;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(ellipse at 12% 0%, rgba(42, 108, 173, .18), transparent 34%),
            radial-gradient(ellipse at 92% 12%, rgba(36, 161, 160, .10), transparent 28%),
            var(--bg);
        color: var(--text);
        font-family: 'DM Sans', sans-serif;
    }

    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stToolbar"] { right: 1rem; }
    [data-testid="stSidebar"] {
        background: #091625;
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] * { color: var(--text); }

    .block-container {
        max-width: 1420px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    h1, h2, h3, .brand, .hero-title {
        font-family: 'Manrope', sans-serif !important;
        letter-spacing: -.035em;
    }

    .brand-row {
        display: flex; align-items: center; gap: .7rem;
        margin: .2rem 0 1.5rem;
    }
    .brand-mark {
        width: 42px; height: 42px; display: grid; place-items: center;
        border-radius: 14px; font-size: 1.35rem;
        background: linear-gradient(145deg, #1e78b8, #15506f);
        box-shadow: 0 8px 28px rgba(36, 143, 195, .25);
    }
    .brand { font-size: 1.25rem; font-weight: 800; color: #f3f8ff; }
    .brand-caption { color: var(--muted); font-size: .76rem; margin-top: -.15rem; }

    .hero {
        position: relative; overflow: hidden; isolation: isolate;
        min-height: 310px; border: 1px solid var(--line);
        border-radius: 26px; padding: 2.5rem 3rem;
        display: flex; align-items: center;
        background:
          linear-gradient(90deg, rgba(5, 17, 31, .97) 0%, rgba(5, 17, 31, .82) 48%, rgba(5, 17, 31, .25) 100%),
          url('https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=1800&q=85') center/cover;
        box-shadow: 0 22px 70px rgba(0,0,0,.22);
        margin-bottom: 1.5rem;
    }
    .hero-content { max-width: 650px; position: relative; z-index: 1; }
    .eyebrow {
        display: inline-flex; align-items: center; gap: .5rem;
        color: #a8ddff; background: rgba(48, 130, 190, .16);
        border: 1px solid rgba(119, 190, 235, .28);
        border-radius: 999px; padding: .42rem .8rem;
        font-size: .74rem; font-weight: 700; letter-spacing: .1em;
        text-transform: uppercase;
    }
    .hero-title {
        color: #fff; font-size: clamp(2.2rem, 5vw, 3.8rem);
        line-height: 1.05; font-weight: 800; margin: 1.1rem 0 .8rem;
    }
    .hero-copy { color: #c3d5e8; font-size: 1.03rem; line-height: 1.7; max-width: 570px; }
    .hero-foot { color: #a9c5dc; font-size: .8rem; margin-top: 1.4rem; }

    .section-kicker {
        color: #8fb9df; font-size: .72rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: .13em;
        margin: 1.8rem 0 .55rem;
    }
    .section-title {
        color: #f0f6ff; font-family: 'Manrope', sans-serif;
        font-size: 1.35rem; font-weight: 800; margin: 0 0 .3rem;
    }
    .section-copy { color: var(--muted); font-size: .9rem; margin-bottom: 1rem; }

    .destination-card {
        height: 118px; border-radius: 17px; overflow: hidden;
        position: relative; border: 1px solid var(--line);
        background-size: cover; background-position: center;
        transition: transform .2s ease, border-color .2s ease;
    }
    .destination-card:after {
        content: ''; position: absolute; inset: 0;
        background: linear-gradient(0deg, rgba(3, 12, 23, .88), rgba(3, 12, 23, .02));
    }
    .destination-name {
        position: absolute; z-index: 1; left: 14px; bottom: 12px;
        color: white; font-weight: 700; font-size: .95rem;
    }

    div[data-testid="stTextArea"] textarea,
    div[data-testid="stTextInput"] input {
        background: #0a1929 !important; color: #edf5ff !important;
        border: 1px solid rgba(133, 176, 215, .25) !important;
        border-radius: 13px !important;
    }
    div[data-testid="stTextArea"] textarea:focus,
    div[data-testid="stTextInput"] input:focus {
        border-color: #65a9ff !important;
        box-shadow: 0 0 0 1px #65a9ff !important;
    }
    div[data-testid="stTextArea"] label,
    div[data-testid="stTextInput"] label {
        color: #c4d8ec !important; font-weight: 600 !important;
    }

    div[data-testid="stButton"] > button {
        border-radius: 12px !important;
        border: 1px solid rgba(119, 174, 218, .25) !important;
        background: #10243a !important;
        color: #eaf4ff !important;
        font-weight: 600 !important;
        min-height: 2.7rem;
        transition: all .18s ease;
    }
    div[data-testid="stButton"] > button:hover {
        border-color: #65a9ff !important;
        background: #173653 !important;
        transform: translateY(-1px);
    }
    div[data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(110deg, #267fc1, #176a88) !important;
        border: 0 !important; color: white !important;
        min-height: 3.25rem; font-size: 1rem !important;
        box-shadow: 0 10px 28px rgba(28, 122, 171, .22);
    }

    .info-panel {
        background: linear-gradient(145deg, rgba(16, 36, 58, .95), rgba(10, 25, 41, .95));
        border: 1px solid var(--line); border-radius: 18px;
        padding: 1rem 1.1rem; margin-bottom: .8rem;
    }
    .info-label { color: #91abc4; font-size: .7rem; text-transform: uppercase; letter-spacing: .1em; }
    .info-value { color: #f2f7ff; font-size: 1rem; font-weight: 700; margin-top: .25rem; }

    [data-testid="stStatusWidget"] {
        background: #0c1b2c; border: 1px solid var(--line);
        border-radius: 14px; margin: .5rem 0;
    }
    [data-testid="stAlert"] { border-radius: 13px; }
    .result-panel {
        background: linear-gradient(145deg, #0e2033, #0a1929);
        border: 1px solid rgba(101, 169, 255, .25);
        border-left: 4px solid #65a9ff;
        border-radius: 16px; padding: 1.25rem 1.4rem;
    }
    .small-muted { color: var(--muted); font-size: .82rem; }
    hr { border-color: var(--line) !important; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# Session state helpers
# ---------------------------------------------------------------------
if "trip_prompt" not in st.session_state:
    st.session_state.trip_prompt = ""
if "last_run" not in st.session_state:
    st.session_state.last_run = None


def set_prompt(prompt: str) -> None:
    """Fill the trip prompt when a sample destination is selected."""
    st.session_state.trip_prompt = prompt


# ---------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="brand-row">
            <div class="brand-mark">🌍</div>
            <div>
                <div class="brand">Travely</div>
                <div class="brand-caption">Your AI travel companion</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("### Your workspace")
    thread_id = st.text_input(
        "Session / User ID",
        value="travely_user",
        help="A stable thread ID can be used by the LangGraph checkpointer to resume a conversation.",
    )
    st.caption("Use the same ID to continue the same conversation, if persistence is enabled in the backend.")

    st.divider()
    st.markdown("### Built with")
    for item in ["🧩 LangGraph orchestration", "🧠 Groq · LLaMA", "🐘 PostgreSQL", "🔎 Tavily Search", "✈️ AviationStack"]:
        st.markdown(f"- {item}")

    st.divider()
    st.markdown("### Agent workflow")
    st.markdown("1. ✈️ Flight research")
    st.markdown("2. 🏨 Hotel discovery")
    st.markdown("3. 🗺️ Itinerary planning")
    st.markdown("4. ✨ Final trip plan")
    st.caption("The workflow shown here should match the nodes configured in main.py.")


# ---------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------
st.markdown(
    """
    <section class="hero">
      <div class="hero-content">
        <span class="eyebrow">✦ Multi-agent travel intelligence</span>
        <div class="hero-title">Your next journey,<br>planned intelligently.</div>
        <div class="hero-copy">
          Tell Travely where you want to go, when you want to travel, and what you want to spend.
          Our specialized AI agents work together to shape your trip.
        </div>
        <div class="hero-foot">FLIGHTS&nbsp;&nbsp; · &nbsp;&nbsp;STAYS&nbsp;&nbsp; · &nbsp;&nbsp;ITINERARIES</div>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# Destination inspiration
# ---------------------------------------------------------------------
st.markdown('<div class="section-kicker">Get inspired</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Popular starting points</div>', unsafe_allow_html=True)
st.markdown('<div class="section-copy">Choose an idea to prefill your travel request.</div>', unsafe_allow_html=True)

destinations = [
    ("🇯🇵 Tokyo", "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=700&q=80", "Plan a 7-day Japan trip under ₹2 lakh, including flights, hotels and sightseeing."),
    ("🇫🇷 Paris", "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=700&q=80", "Plan a 5-day Paris trip with flights, comfortable hotels and major attractions."),
    ("🇹🇭 Bangkok", "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=700&q=80", "Plan a 4-day Bangkok trip with flights, hotels, food and local experiences."),
    ("🇮🇹 Rome", "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=700&q=80", "Plan a 6-day Rome and Italy trip with a balanced sightseeing itinerary."),
    ("🇦🇪 Dubai", "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=700&q=80", "Plan a 3-day Dubai weekend trip with flights, hotel and key experiences."),
]
cols = st.columns(5)
for col, (name, image_url, prompt) in zip(cols, destinations):
    with col:
        st.markdown(
            f'<div class="destination-card" style="background-image:url(&quot;{image_url}&quot;)">'
            f'<div class="destination-name">{name}</div></div>',
            unsafe_allow_html=True,
        )
        st.button(
            f"Explore {name.split(' ', 1)[1]}",
            key=f"dest_{name}",
            use_container_width=True,
            on_click=set_prompt,
            args=(prompt,),
        )


# ---------------------------------------------------------------------
# Trip request
# ---------------------------------------------------------------------
st.markdown('<div class="section-kicker">Start planning</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Where should we take you?</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-copy">Include your destination, dates or duration, budget, number of travellers and preferences.</div>',
    unsafe_allow_html=True,
)

with st.container(border=True):
    user_query = st.text_area(
        "Describe your ideal trip",
        key="trip_prompt",
        height=130,
        placeholder="Example: Plan a 7-day Japan trip for 2 people in April, under ₹2 lakh. Include flights, hotels, food and a day-wise itinerary.",
    )
    left, right = st.columns([1, 3])
    with left:
        generate = st.button("✨ Generate my trip", type="primary", use_container_width=True)
    with right:
        st.markdown(
            '<p class="small-muted" style="padding-top:.7rem">Travely will coordinate its agents and assemble the information into one travel plan.</p>',
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------
# Agent execution
# ---------------------------------------------------------------------
AGENT_META = {
    "flight_agent": ("✈️", "Flight research"),
    "hotel_agent": ("🏨", "Hotel discovery"),
    "itinerary_agent": ("🗺️", "Itinerary planning"),
    "final_agent": ("✨", "Final trip plan"),
}


def extract_final_text(state_update):
    """Extract final assistant text from a LangGraph node update."""
    messages = state_update.get("messages", [])
    if not messages:
        return ""
    last_message = messages[-1]
    return getattr(last_message, "content", str(last_message))


if generate:
    if not user_query.strip():
        st.warning("Add a destination or describe the trip you have in mind first.")
    elif not thread_id.strip():
        st.warning("Please provide a session / user ID.")
    else:
        config = {"configurable": {"thread_id": thread_id.strip()}}
        collected = {
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "final_response": "",
            "llm_calls": 0,
            "nodes_seen": [],
        }

        st.divider()
        st.markdown('<div class="section-kicker">Working on your request</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Travely agent activity</div>', unsafe_allow_html=True)

        try:
            with st.spinner("Coordinating your travel agents..."):
                for chunk in app.stream(
                    {
                        "messages": [HumanMessage(content=user_query)],
                        "user_query": user_query,
                        "flight_results": "",
                        "hotel_results": "",
                        "itinerary": "",
                        "llm_calls": 0,
                    },
                    config=config,
                    stream_mode="updates",
                ):
                    for node_name, state_update in chunk.items():
                        icon, label = AGENT_META.get(node_name, ("⚙️", node_name))
                        collected["nodes_seen"].append(node_name)

                        with st.status(f"{icon}  {label}", state="complete", expanded=True):
                            if node_name == "flight_agent":
                                value = state_update.get("flight_results", "")
                                collected["flight_results"] = value
                                st.markdown(value or "_No flight information returned._")
                            elif node_name == "hotel_agent":
                                value = state_update.get("hotel_results", "")
                                collected["hotel_results"] = value
                                st.markdown(value or "_No hotel information returned._")
                            elif node_name == "itinerary_agent":
                                value = state_update.get("itinerary", "")
                                collected["itinerary"] = value
                                st.markdown(value or "_No itinerary returned._")
                            elif node_name == "final_agent":
                                value = extract_final_text(state_update)
                                collected["final_response"] = value
                                st.markdown(value or "_No final response returned._")

                            collected["llm_calls"] = state_update.get(
                                "llm_calls", collected["llm_calls"]
                            )

            st.session_state.last_run = collected

        except Exception as exc:
            st.error(f"Travely could not complete this request: {exc}")
            st.exception(exc)


# ---------------------------------------------------------------------
# Results and export
# ---------------------------------------------------------------------
result = st.session_state.last_run
if result:
    st.divider()
    st.markdown('<div class="section-kicker">Your results</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Trip planning summary</div>', unsafe_allow_html=True)

    metric_cols = st.columns(3)
    metrics = [
        (str(len(set(result.get("nodes_seen", [])))), "Workflow nodes executed"),
        (str(result.get("llm_calls", 0)), "LLM calls"),
        ("Ready" if result.get("final_response") else "Partial", "Plan status"),
    ]
    for col, (value, label) in zip(metric_cols, metrics):
        with col:
            st.markdown(
                f'<div class="info-panel"><div class="info-label">{escape(label)}</div>'
                f'<div class="info-value">{escape(value)}</div></div>',
                unsafe_allow_html=True,
            )

    sections = [
        ("✈️ Flight information", "flight_results"),
        ("🏨 Hotel information", "hotel_results"),
        ("🗺️ Itinerary", "itinerary"),
    ]
    for heading, key in sections:
        value = result.get(key, "")
        if value:
            with st.expander(heading, expanded=False):
                st.markdown(value)

    final_response = result.get("final_response", "")
    if final_response:
        st.markdown('<div class="section-title">✨ Your Travely plan</div>', unsafe_allow_html=True)
        st.markdown(final_response)

    # Build a Markdown export. The browser download works even on hosts where
    # the app's filesystem is ephemeral.
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"travely_plan_{timestamp}.md"
    file_content = f"""# Travely — Travel Plan

**Request:** {user_query}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Session ID:** {thread_id}

---

## Flight information
{result.get("flight_results") or "N/A"}

---

## Hotel information
{result.get("hotel_results") or "N/A"}

---

## Itinerary
{result.get("itinerary") or "N/A"}

---

## Final travel plan
{final_response or "N/A"}

---

**Workflow nodes executed:** {", ".join(sorted(set(result.get("nodes_seen", []))))}
**LLM calls:** {result.get("llm_calls", 0)}
"""
    st.download_button(
        "⬇️ Download travel plan",
        data=file_content,
        file_name=filename,
        mime="text/markdown",
        use_container_width=False,
    )
