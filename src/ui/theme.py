from __future__ import annotations

import streamlit as st


def inject_theme() -> None:
    st.markdown(
        """
        <style>
        /* ═══════════════════════════════════════════════════════════════════
           PIFF-0054-ng · INDUSTRIAL PRECISION · Steel & Amber
           Hydraulic cylinder testing — instrument-panel aesthetic
        ═══════════════════════════════════════════════════════════════════ */

        @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;500;600;700&family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;1,400&family=Barlow:wght@400;500;600&display=swap');

        /* ── Token System ─────────────────────────────────────────────── */
        :root {
          --p-bg:          #14181c;
          --p-surface:     #1a1f24;
          --p-glass:       rgba(26, 31, 36, 0.84);
          --p-ink:         #ece8de;
          --p-ink-dim:     rgba(236, 232, 222, 0.68);
          --p-accent:      #f0883e;
          --p-accent-lo:   rgba(240, 136, 62, 0.09);
          --p-accent-glow: 0 0 20px rgba(240, 136, 62, 0.28);
          --p-data:        #5b9bd5;
          --p-data-lo:     rgba(91, 155, 213, 0.09);
          --p-data-glow:   0 0 16px rgba(91, 155, 213, 0.25);
          --p-danger:      #e05555;
          --p-warn:        #e8c84a;
          --p-success:     #6bbf6b;
          --p-grid:        rgba(240, 136, 62, 0.05);
          --p-border:      rgba(240, 136, 62, 0.18);
          --p-shadow:      0 8px 32px rgba(0, 0, 0, 0.55);
          --p-r:           6px;
          --p-ease:        cubic-bezier(0.22, 0.61, 0.36, 1);
          --p-dur:         0.30s;
        }

        /* ── App Background ──────────────────────────────────────────── */
        .stApp {
          background-color: var(--p-bg) !important;
          background-image:
            radial-gradient(ellipse 55% 30% at 5% 0%,
              rgba(240, 136, 62, 0.04) 0%, transparent 55%),
            radial-gradient(ellipse 45% 25% at 95% 100%,
              rgba(91, 155, 213, 0.03) 0%, transparent 50%);
          color: var(--p-ink) !important;
        }

        .stAppViewContainer,
        .stMainBlockContainer,
        [data-testid="stAppViewBlockContainer"] {
          background: transparent !important;
        }

        .stMainBlockContainer {
          padding-top: 1rem !important;
          max-width: 1400px !important;
        }

        /* ── Header ──────────────────────────────────────────────────── */
        [data-testid="stHeader"] {
          background: rgba(20, 24, 28, 0.88) !important;
          backdrop-filter: blur(14px) !important;
          -webkit-backdrop-filter: blur(14px) !important;
          border-bottom: 1px solid var(--p-border) !important;
        }

        /* ── Sidebar ─────────────────────────────────────────────────── */
        [data-testid="stSidebar"] {
          background: var(--p-surface) !important;
          border-right: 1px solid var(--p-border) !important;
          box-shadow: 3px 0 36px rgba(0, 0, 0, 0.45) !important;
        }

        [data-testid="stSidebar"] > div,
        [data-testid="stSidebarContent"] {
          background: transparent !important;
        }

        /* ── Typography ──────────────────────────────────────────────── */
        h1 {
          font-family: 'Barlow Condensed', sans-serif !important;
          font-weight: 600 !important;
          font-size: clamp(1.4rem, 2.8vw, 2.2rem) !important;
          letter-spacing: 0.02em !important;
          color: var(--p-ink) !important;
          line-height: 1.08 !important;
        }

        h2 {
          font-family: 'Barlow Condensed', sans-serif !important;
          font-weight: 500 !important;
          font-size: clamp(1.05rem, 2vw, 1.4rem) !important;
          color: var(--p-ink) !important;
          letter-spacing: 0.01em !important;
        }

        h3 {
          font-family: 'Barlow', sans-serif !important;
          font-weight: 600 !important;
          font-size: clamp(0.88rem, 1.6vw, 1.1rem) !important;
          color: var(--p-accent) !important;
          letter-spacing: 0.04em !important;
          text-transform: uppercase !important;
          border-bottom: 1px solid var(--p-grid) !important;
          padding-bottom: 0.35rem !important;
          margin-bottom: 0.6rem !important;
        }

        p, li, .stMarkdown p, .stCaption {
          font-family: 'IBM Plex Mono', monospace !important;
          color: var(--p-ink-dim) !important;
          font-size: 0.78rem !important;
          line-height: 1.62 !important;
        }

        label,
        .stSelectbox label,
        .stMultiSelect label,
        .stTextArea label,
        .stTextInput label,
        .stNumberInput label,
        .stRadio label {
          font-family: 'IBM Plex Mono', monospace !important;
          color: var(--p-ink-dim) !important;
          font-size: 0.70rem !important;
          letter-spacing: 0.06em !important;
          text-transform: uppercase !important;
        }

        /* ── Inputs ──────────────────────────────────────────────────── */
        .stTextInput input,
        .stTextArea textarea,
        .stNumberInput input {
          background: var(--p-glass) !important;
          border: 1px solid var(--p-border) !important;
          border-radius: var(--p-r) !important;
          color: var(--p-ink) !important;
          font-family: 'IBM Plex Mono', monospace !important;
          font-size: 0.80rem !important;
          transition:
            border-color var(--p-dur) var(--p-ease),
            box-shadow var(--p-dur) var(--p-ease) !important;
        }

        .stTextInput input:focus,
        .stTextArea textarea:focus {
          border-color: var(--p-accent) !important;
          box-shadow: 0 0 0 2px rgba(240, 136, 62, 0.20),
                      0 0 14px rgba(240, 136, 62, 0.10) !important;
          outline: none !important;
        }

        .stTextInput input:disabled,
        .stTextArea textarea:disabled {
          opacity: 0.40 !important;
          cursor: not-allowed !important;
        }

        /* ── Select ──────────────────────────────────────────────────── */
        .stSelectbox [data-baseweb="select"] > div,
        .stMultiSelect [data-baseweb="select"] > div {
          background: var(--p-glass) !important;
          border: 1px solid var(--p-border) !important;
          border-radius: var(--p-r) !important;
          transition: border-color var(--p-dur) var(--p-ease),
                      box-shadow var(--p-dur) var(--p-ease) !important;
        }

        .stSelectbox [data-baseweb="select"] > div:hover,
        .stMultiSelect [data-baseweb="select"] > div:hover {
          border-color: var(--p-accent) !important;
          box-shadow: 0 0 10px rgba(240, 136, 62, 0.15) !important;
        }

        [data-baseweb="select"] span,
        [data-baseweb="select"] input {
          color: var(--p-ink) !important;
          font-family: 'IBM Plex Mono', monospace !important;
          font-size: 0.80rem !important;
        }

        [data-baseweb="popover"],
        [data-baseweb="menu"] {
          background: #1e2429 !important;
          border: 1px solid var(--p-border) !important;
          border-radius: var(--p-r) !important;
          box-shadow: var(--p-shadow), 0 0 18px rgba(240, 136, 62, 0.04) !important;
        }

        [data-baseweb="option"] {
          background: transparent !important;
          color: var(--p-ink-dim) !important;
          font-family: 'IBM Plex Mono', monospace !important;
          font-size: 0.78rem !important;
          transition: background var(--p-dur) var(--p-ease) !important;
        }

        [data-baseweb="option"]:hover,
        [data-baseweb="option"][aria-selected="true"] {
          background: var(--p-accent-lo) !important;
          color: var(--p-accent) !important;
        }

        [data-baseweb="tag"] {
          background: var(--p-accent-lo) !important;
          border: 1px solid rgba(240, 136, 62, 0.35) !important;
          border-radius: 4px !important;
        }

        [data-baseweb="tag"] span { color: var(--p-accent) !important; }

        /* ── Radio ───────────────────────────────────────────────────── */
        .stRadio [data-baseweb="radio"] span:first-child {
          border-color: var(--p-border) !important;
          background: var(--p-glass) !important;
        }

        .stRadio [data-baseweb="radio"] input:checked + span span:first-child {
          background: var(--p-accent) !important;
          border-color: var(--p-accent) !important;
        }

        /* ── Buttons ─────────────────────────────────────────────────── */
        .stButton button,
        .stDownloadButton button {
          font-family: 'Barlow Condensed', sans-serif !important;
          font-weight: 600 !important;
          font-size: 0.88rem !important;
          letter-spacing: 0.06em !important;
          text-transform: uppercase !important;
          border-radius: var(--p-r) !important;
          padding: 0.40rem 1rem !important;
          transition:
            transform var(--p-dur) var(--p-ease),
            box-shadow var(--p-dur) var(--p-ease),
            background var(--p-dur) var(--p-ease),
            border-color var(--p-dur) var(--p-ease) !important;
          will-change: transform !important;
        }

        .stButton button[kind="primary"],
        .stButton button[data-testid="baseButton-primary"] {
          background: linear-gradient(135deg, #f0883e 0%, #e07030 100%) !important;
          color: #14181c !important;
          border: none !important;
          box-shadow: 0 3px 16px rgba(240, 136, 62, 0.32) !important;
        }

        @media (hover: hover) and (pointer: fine) {
          .stButton button[kind="primary"]:hover,
          .stButton button[data-testid="baseButton-primary"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 24px rgba(240, 136, 62, 0.40) !important;
          }

          .stButton button[kind="secondary"]:hover,
          .stButton button[data-testid="baseButton-secondary"]:hover {
            transform: translateY(-1px) !important;
            border-color: var(--p-accent) !important;
            color: var(--p-accent) !important;
            box-shadow: 0 0 10px rgba(240, 136, 62, 0.15) !important;
          }

          .stDownloadButton button:hover {
            border-color: var(--p-data) !important;
            color: var(--p-data) !important;
            transform: translateY(-1px) !important;
            box-shadow: var(--p-data-glow) !important;
          }

          .piff-gauge-step:hover {
            border-color: var(--p-accent) !important;
            box-shadow: 0 0 14px rgba(240, 136, 62, 0.12) !important;
            transform: translateY(-1px) !important;
          }

          .piff-kpi:hover {
            border-color: rgba(240, 136, 62, 0.35) !important;
            box-shadow: 0 0 16px rgba(240, 136, 62, 0.10) !important;
            transform: translateY(-1px) !important;
          }
        }

        .stButton button[kind="secondary"],
        .stButton button[data-testid="baseButton-secondary"] {
          background: var(--p-glass) !important;
          color: var(--p-ink) !important;
          border: 1px solid var(--p-border) !important;
        }

        .stDownloadButton button {
          background: var(--p-glass) !important;
          color: var(--p-ink) !important;
          border: 1px solid var(--p-border) !important;
        }

        /* ── Tabs ─────────────────────────────────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {
          background: transparent !important;
          border-bottom: 1px solid var(--p-grid) !important;
          gap: 2px !important;
        }

        .stTabs [data-baseweb="tab"] {
          font-family: 'Barlow Condensed', sans-serif !important;
          font-weight: 500 !important;
          font-size: 0.85rem !important;
          letter-spacing: 0.06em !important;
          text-transform: uppercase !important;
          color: var(--p-ink-dim) !important;
          background: transparent !important;
          border-radius: var(--p-r) var(--p-r) 0 0 !important;
          padding: 0.45rem 1.1rem !important;
          border: 1px solid transparent !important;
          transition: color var(--p-dur) var(--p-ease),
                      background var(--p-dur) var(--p-ease),
                      border-color var(--p-dur) var(--p-ease) !important;
        }

        .stTabs [data-baseweb="tab"]:hover {
          color: var(--p-accent) !important;
          background: var(--p-accent-lo) !important;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
          color: var(--p-accent) !important;
          background: var(--p-accent-lo) !important;
          border-color: var(--p-border) var(--p-border) transparent !important;
        }

        .stTabs [data-baseweb="tab-highlight"],
        [data-baseweb="tab-border"] {
          background: var(--p-accent) !important;
          height: 2px !important;
        }

        /* ── Alerts ──────────────────────────────────────────────────── */
        [data-testid="stSuccess"], .stSuccess {
          background: rgba(107, 191, 107, 0.06) !important;
          border-left: 3px solid var(--p-success) !important;
          border-radius: 0 var(--p-r) var(--p-r) 0 !important;
        }

        [data-testid="stError"], .stError {
          background: rgba(224, 85, 85, 0.06) !important;
          border-left: 3px solid var(--p-danger) !important;
          border-radius: 0 var(--p-r) var(--p-r) 0 !important;
        }

        [data-testid="stWarning"], .stWarning {
          background: rgba(232, 200, 74, 0.06) !important;
          border-left: 3px solid var(--p-warn) !important;
          border-radius: 0 var(--p-r) var(--p-r) 0 !important;
        }

        [data-testid="stInfo"], .stInfo {
          background: rgba(240, 136, 62, 0.03) !important;
          border-left: 3px solid rgba(240, 136, 62, 0.30) !important;
          border-radius: 0 var(--p-r) var(--p-r) 0 !important;
        }

        [data-testid="stSuccess"] p, .stSuccess p { color: var(--p-success) !important; }
        [data-testid="stError"] p, .stError p { color: var(--p-danger) !important; }
        [data-testid="stWarning"] p, .stWarning p { color: var(--p-warn) !important; }
        [data-testid="stInfo"] p, .stInfo p { color: var(--p-ink-dim) !important; }

        .stAlert p {
          font-family: 'IBM Plex Mono', monospace !important;
          font-size: 0.78rem !important;
        }

        /* ── Plotly container ────────────────────────────────────────── */
        .stPlotlyChart {
          border: 1px solid var(--p-border) !important;
          border-radius: var(--p-r) !important;
          overflow: hidden !important;
          box-shadow: var(--p-shadow) !important;
        }

        /* ── Scrollbar ───────────────────────────────────────────────── */
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: var(--p-bg); }
        ::-webkit-scrollbar-thumb {
          background: var(--p-border);
          border-radius: 2px;
        }
        ::-webkit-scrollbar-thumb:hover { background: var(--p-accent); }

        /* ── Focus Ring ──────────────────────────────────────────────── */
        button:focus-visible,
        [role="button"]:focus-visible,
        input:focus-visible,
        textarea:focus-visible,
        select:focus-visible {
          outline: 2px solid var(--p-accent) !important;
          outline-offset: 2px !important;
          border-radius: 4px !important;
        }

        /* ═══════════════════════════════════════════════════════════════
           TOOLTIPS — High Contrast
        ═══════════════════════════════════════════════════════════════ */

        [data-testid="stTooltipIcon"] {
          display: inline-flex !important;
          align-items: center !important;
          opacity: 0.50 !important;
          transition: opacity var(--p-dur) var(--p-ease) !important;
          margin-left: 2px !important;
        }

        [data-testid="stTooltipIcon"]:hover { opacity: 1 !important; }

        [data-testid="stTooltipIcon"] svg {
          fill: var(--p-accent) !important;
          width: 12px !important;
          height: 12px !important;
        }

        [role="tooltip"],
        [data-baseweb="tooltip"] {
          background: #232a30 !important;
          border: 1px solid rgba(240, 136, 62, 0.45) !important;
          border-radius: 6px !important;
          box-shadow: 0 14px 44px rgba(0, 0, 0, 0.80),
                      0 0 16px rgba(240, 136, 62, 0.06) !important;
          max-width: 320px !important;
          padding: 11px 15px !important;
        }

        [role="tooltip"] *,
        [data-baseweb="tooltip"] * {
          background: transparent !important;
          color: #f2efe8 !important;
          font-family: 'IBM Plex Mono', monospace !important;
          font-size: 0.73rem !important;
          line-height: 1.65 !important;
        }

        /* ═══════════════════════════════════════════════════════════════
           CUSTOM COMPONENTS
        ═══════════════════════════════════════════════════════════════ */

        /* ── Sidebar Brand ───────────────────────────────────────────── */
        .piff-brand {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 12px 2px 6px;
        }

        .piff-brand-icon {
          font-size: 1.5rem;
          color: var(--p-accent);
          line-height: 1;
          flex-shrink: 0;
        }

        .piff-brand-name {
          font-family: 'Barlow Condensed', sans-serif;
          font-weight: 600;
          font-size: 1.15rem;
          color: var(--p-ink);
          letter-spacing: 0.08em;
          text-transform: uppercase;
          line-height: 1.05;
        }

        .piff-brand-tag {
          font-family: 'IBM Plex Mono', monospace;
          font-size: 0.58rem;
          color: var(--p-ink-dim);
          letter-spacing: 0.06em;
          margin-top: 1px;
        }

        .piff-hr {
          height: 1px;
          background: linear-gradient(90deg,
            rgba(240,136,62,0.50) 0%,
            rgba(240,136,62,0.08) 70%,
            transparent 100%);
          margin: 8px 0 16px;
          border: none;
        }

        .piff-sidebar-label {
          font-family: 'IBM Plex Mono', monospace;
          font-size: 0.58rem;
          color: var(--p-ink-dim);
          letter-spacing: 0.16em;
          text-transform: uppercase;
          display: block;
          margin-bottom: 8px;
          padding-bottom: 5px;
          border-bottom: 1px solid var(--p-grid);
        }

        /* ── Page Header ─────────────────────────────────────────────── */
        .piff-page-header {
          padding-bottom: 10px;
          margin-bottom: 12px;
          border-bottom: 1px solid var(--p-grid);
        }

        .piff-page-title {
          font-family: 'Barlow Condensed', sans-serif;
          font-weight: 600;
          font-size: clamp(1.5rem, 3.2vw, 2.4rem);
          color: var(--p-ink);
          letter-spacing: 0.01em;
          line-height: 1.04;
        }

        .piff-page-sub {
          font-family: 'IBM Plex Mono', monospace;
          font-size: 0.70rem;
          color: var(--p-accent);
          letter-spacing: 0.04em;
          margin-top: 4px;
        }

        /* ── Gauge Strip ─────────────────────────────────────────────── */
        .piff-gauge-strip {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 0;
          margin: 0 0 16px;
          border: 1px solid var(--p-border);
          border-radius: 8px;
          overflow: hidden;
          background: var(--p-glass);
        }

        .piff-gauge-step {
          position: relative;
          padding: 12px 14px 10px;
          text-align: center;
          border-right: 1px solid var(--p-grid);
          transition: border-color var(--p-dur) var(--p-ease),
                      box-shadow var(--p-dur) var(--p-ease),
                      transform var(--p-dur) var(--p-ease);
        }

        .piff-gauge-step:last-child { border-right: none; }

        .piff-gauge-step .num {
          font-family: 'Barlow Condensed', sans-serif;
          font-weight: 600;
          font-size: 1.3rem;
          color: var(--p-accent);
          letter-spacing: 0.03em;
          line-height: 1;
          display: block;
          margin-bottom: 4px;
        }

        .piff-gauge-step b {
          display: block;
          font-family: 'Barlow Condensed', sans-serif;
          font-weight: 600;
          font-size: 0.80rem;
          color: var(--p-ink);
          letter-spacing: 0.06em;
          text-transform: uppercase;
          margin-bottom: 3px;
        }

        .piff-gauge-step .desc {
          font-family: 'IBM Plex Mono', monospace;
          font-size: 0.62rem;
          color: var(--p-ink-dim);
          line-height: 1.4;
        }

        /* ── KPI Cards ──────────────────────────────────────────────── */
        .piff-kpis {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 10px;
          margin: 8px 0 16px;
        }

        .piff-kpi {
          border-radius: 8px;
          border: 1px solid var(--p-border);
          background: var(--p-glass);
          backdrop-filter: blur(8px);
          -webkit-backdrop-filter: blur(8px);
          padding: 12px 14px;
          transition: border-color var(--p-dur) var(--p-ease),
                      box-shadow var(--p-dur) var(--p-ease),
                      transform var(--p-dur) var(--p-ease);
        }

        .piff-kpi .k {
          font-size: 0.64rem;
          color: var(--p-ink-dim);
          font-family: 'IBM Plex Mono', monospace;
          letter-spacing: 0.05em;
          text-transform: uppercase;
          margin-bottom: 5px;
        }

        .piff-kpi .v {
          font-size: clamp(1.05rem, 2vw, 1.4rem);
          color: var(--p-accent);
          font-family: 'Barlow Condensed', sans-serif;
          font-weight: 600;
          letter-spacing: 0.01em;
        }

        .piff-kpi .v.data { color: var(--p-data); }

        /* ── Empty State ─────────────────────────────────────────────── */
        .piff-empty {
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 72px 24px 64px;
          text-align: center;
          border: 1px dashed rgba(240, 136, 62, 0.16);
          border-radius: 10px;
          margin: 20px 0 8px;
          background: rgba(240, 136, 62, 0.012);
        }

        .piff-empty-icon {
          font-size: 2.2rem;
          color: var(--p-accent);
          opacity: 0.22;
          margin-bottom: 16px;
          line-height: 1;
        }

        .piff-empty-title {
          font-family: 'Barlow Condensed', sans-serif;
          font-weight: 500;
          font-size: 1.1rem;
          color: var(--p-ink);
          letter-spacing: 0.04em;
          text-transform: uppercase;
          margin-bottom: 10px;
        }

        .piff-empty-desc {
          font-family: 'IBM Plex Mono', monospace;
          font-size: 0.72rem;
          color: var(--p-ink-dim);
          line-height: 1.68;
          max-width: 400px;
        }

        .piff-empty-desc strong {
          color: var(--p-accent);
          font-weight: 600;
        }

        /* ── Form Section Labels ──────────────────────────────────────── */
        .piff-form-section {
          display: flex;
          align-items: center;
          gap: 8px;
          font-family: 'IBM Plex Mono', monospace;
          font-size: 0.60rem;
          color: var(--p-accent);
          letter-spacing: 0.14em;
          text-transform: uppercase;
          margin: 22px 0 10px;
          padding-bottom: 6px;
          border-bottom: 1px solid var(--p-grid);
        }

        .piff-form-section::before {
          content: '';
          width: 3px;
          height: 12px;
          background: var(--p-accent);
          border-radius: 1px;
          flex-shrink: 0;
        }

        /* ── Export Cards ─────────────────────────────────────────────── */
        .piff-export-card {
          border: 1px solid var(--p-border);
          border-radius: 8px;
          padding: 16px 18px 14px;
          background: var(--p-glass);
          height: 100%;
          box-sizing: border-box;
        }

        .piff-export-title {
          font-family: 'Barlow Condensed', sans-serif;
          font-weight: 600;
          font-size: 0.85rem;
          color: var(--p-ink);
          letter-spacing: 0.06em;
          text-transform: uppercase;
          margin-bottom: 5px;
        }

        .piff-export-desc {
          font-family: 'IBM Plex Mono', monospace;
          font-size: 0.66rem;
          color: var(--p-ink-dim);
          line-height: 1.55;
          margin-bottom: 10px;
        }

        /* ── Diagnostics JSON ────────────────────────────────────────── */
        .stJson {
          border: 1px solid var(--p-border) !important;
          border-radius: var(--p-r) !important;
          overflow: hidden !important;
        }

        /* ── Responsive ──────────────────────────────────────────────── */
        @media (max-width: 900px) {
          .piff-gauge-strip { grid-template-columns: repeat(2, 1fr); }
          .piff-kpis { grid-template-columns: repeat(2, 1fr); }
        }

        @media (max-width: 600px) {
          .piff-gauge-strip { grid-template-columns: 1fr; }
          .piff-kpis { grid-template-columns: 1fr; }
        }

        /* ── Reduced Motion ──────────────────────────────────────────── */
        @media (prefers-reduced-motion: reduce) {
          *, *::before, *::after {
            animation: none !important;
            transition: none !important;
            scroll-behavior: auto !important;
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_signature_flow() -> None:
    st.markdown(
        """
        <div class="piff-gauge-strip">
          <div class="piff-gauge-step">
            <span class="num">①</span>
            <b>Selecionar</b>
            <span class="desc">Cilindro e ID_Teste no painel lateral</span>
          </div>
          <div class="piff-gauge-step">
            <span class="num">②</span>
            <b>Ler</b>
            <span class="desc">Serie temporal ordenada por LocalCol</span>
          </div>
          <div class="piff-gauge-step">
            <span class="num">③</span>
            <b>Anotar</b>
            <span class="desc">Observacao em coordenada de interesse</span>
          </div>
          <div class="piff-gauge-step">
            <span class="num">④</span>
            <b>Exportar</b>
            <span class="desc">CSV e PDF tecnico</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpis(*, total_rows: int, y_selected: int, obs_ready: bool) -> None:
    readiness = "Pronto" if obs_ready else "Aguardando"
    ready_class = "" if obs_ready else ' style="color:var(--p-ink-dim)"'
    st.markdown(
        f"""
        <div class="piff-kpis">
          <div class="piff-kpi">
            <div class="k">Linhas Carregadas</div>
            <div class="v">{total_rows:,}</div>
          </div>
          <div class="piff-kpi">
            <div class="k">Series no Grafico</div>
            <div class="v data">{y_selected}</div>
          </div>
          <div class="piff-kpi">
            <div class="k">Anotacao</div>
            <div class="v"{ready_class}>{readiness}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
