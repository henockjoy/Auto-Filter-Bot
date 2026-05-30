from info import BIN_CHANNEL, URL
from utils import temp
from web.utils.custom_dl import TGCustomYield
import urllib.parse
import html


webapp_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Filmotainment</title>
    <meta name="description" content="Browse trending movies and TV shows. Find and download files instantly.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        :root {
            --bg: #0a0a0f;
            --bg2: #111118;
            --card: #16161f;
            --card2: #1e1e2a;
            --border: rgba(255,255,255,0.07);
            --accent: #e50914;
            --accent2: #ff6b35;
            --gold: #f5c518;
            --text: #ffffff;
            --text2: #b0b0c0;
            --text3: #666680;
            --glass: rgba(10,10,20,0.85);
            --radius: 12px;
            --radius-sm: 8px;
        }
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        html { scroll-behavior: smooth; }

        body {
            font-family: 'Outfit', sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            overflow-x: hidden;
            -webkit-font-smoothing: antialiased;
        }

        /* ── NAVBAR ── */
        .navbar {
            position: fixed; top: 0; left: 0; right: 0; z-index: 100;
            display: flex; align-items: center; justify-content: space-between;
            padding: env(safe-area-inset-top, 0px) 20px 0; height: calc(60px + env(safe-area-inset-top, 0px));
            background: linear-gradient(to bottom, rgba(0,0,0,0.9) 0%, transparent 100%);
            transition: background 0.3s;
        }
        .navbar.solid { background: var(--bg); border-bottom: 1px solid var(--border); }
        .nav-logo {
            font-size: 18px; font-weight: 900; letter-spacing: -0.3px;
            background: linear-gradient(135deg, #fff 0%, var(--accent) 60%, var(--accent2) 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
            white-space: nowrap;
        }
        .nav-right { display: flex; align-items: center; gap: 6px; }
        .nav-search-toggle {
            background: none; border: none; color: var(--text2); cursor: pointer;
            width: 38px; height: 38px; display: flex; align-items: center; justify-content: center;
            border-radius: 50%; transition: background 0.2s, color 0.2s;
        }
        .nav-search-toggle:hover { background: var(--card2); color: #fff; }

        /* ── SEARCH OVERLAY ── */
        .search-overlay {
            position: fixed; inset: 0; z-index: 200;
            background: rgba(10,10,15,0.95); backdrop-filter: blur(32px);
            display: flex; flex-direction: column;
            opacity: 0; visibility: hidden;
            transition: opacity 0.3s ease, visibility 0.3s ease;
            padding: 0;
        }
        .search-overlay.open { opacity: 1; visibility: visible; }
        /* Top bar: search input + cancel button side-by-side */
        .search-top-bar {
            display: flex; align-items: center; gap: 10px;
            /* Use safe-area fallback; in Telegram add extra top space */
            padding: calc(52px + env(safe-area-inset-top, 0px)) 16px 12px;
            flex-shrink: 0;
        }
        .search-field-wrap {
            display: flex; align-items: center; gap: 10px;
            background: var(--card2); border-radius: var(--radius);
            border: 1px solid var(--border); padding: 0 14px;
            flex: 1; min-width: 0;
            transition: border-color 0.25s, box-shadow 0.25s;
        }
        .search-field-wrap:focus-within {
            border-color: rgba(229, 9, 20, 0.4);
            box-shadow: 0 0 14px rgba(229, 9, 20, 0.25);
        }
        .search-field-wrap svg { color: var(--text3); flex-shrink: 0; }
        .search-field {
            flex: 1; background: none; border: none; outline: none;
            color: #fff; font-family: 'Outfit', sans-serif; font-size: 16px;
            padding: 14px 0; min-width: 0;
        }
        .search-field::placeholder { color: var(--text3); }
        .search-close {
            background: none; border: none; color: var(--accent); cursor: pointer;
            font-size: 15px; font-weight: 700; white-space: nowrap;
            padding: 8px 4px; flex-shrink: 0;
            transition: opacity 0.2s, transform 0.15s;
        }
        .search-close:hover { opacity: 0.8; }
        .search-close:active { transform: scale(0.96); }

        /* Search meta bar */
        .search-meta-bar {
            padding: 0 16px 12px; flex-shrink: 0;
            font-size: 12px; color: var(--text3); letter-spacing: 0.2px;
        }
        .search-meta-bar b { color: var(--text2); }

        /* Premium search results grid (3 columns on mobile) */
        .search-results-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px; overflow-y: auto; flex: 1;
            padding: 0 16px 60px; align-content: start;
        }

        /* Override poster card styles when inside search grid to make them fluid */
        .search-results-grid .poster-card {
            width: 100%;
            margin: 0 !important; /* Reset horizontal scroll margin spacing */
        }
        .search-results-grid .poster-img-wrap {
            width: 100%;
            height: 0;
            padding-bottom: 150%; /* Strict 2:3 portrait aspect ratio */
            position: relative;
            border-radius: var(--radius-sm);
            overflow: hidden;
        }
        .search-results-grid .poster-img-wrap img,
        .search-results-grid .poster-img-wrap .poster-placeholder {
            position: absolute;
            inset: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .search-hint {
            text-align: center; color: var(--text3); font-size: 14px;
            padding: 60px 20px; grid-column: 1 / -1;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
        }
        .search-hint svg { display: block; margin: 0 auto 16px; opacity: 0.25; }

        /* ── HERO ── */
        .hero {
            position: relative; width: 100%;
            /* tall enough to show behind navbar + full content */
            height: calc(75vw + 60px); max-height: 560px; min-height: 400px;
            overflow: hidden; margin-top: 0;
        }
        .hero-bg {
            position: absolute; inset: 0;
            background-size: cover; background-position: center top;
            transition: opacity 1s ease;
        }
        .hero-gradient {
            position: absolute; inset: 0;
            background: linear-gradient(
                0deg,
                var(--bg) 0%,
                rgba(10,10,15,0.7) 40%,
                rgba(10,10,15,0.2) 70%,
                rgba(10,10,15,0.5) 100%
            );
        }
        .hero-gradient-side {
            position: absolute; inset: 0;
            background: linear-gradient(90deg, rgba(10,10,15,0.8) 0%, transparent 50%);
        }
        .hero-content {
            position: absolute; bottom: 0; left: 0; right: 0;
            padding: 0 20px 32px;
        }
        .hero-badge {
            display: inline-flex; align-items: center; gap: 5px;
            background: var(--accent); color: #fff;
            font-size: 10px; font-weight: 700; letter-spacing: 1.5px;
            padding: 3px 10px; border-radius: 3px; text-transform: uppercase;
            margin-bottom: 10px;
        }
        .hero-title {
            font-size: clamp(22px, 6vw, 38px); font-weight: 800;
            line-height: 1.1; letter-spacing: -0.5px;
            text-shadow: 0 2px 20px rgba(0,0,0,0.8);
            margin-bottom: 8px;
            max-width: 75%;
        }
        .hero-meta {
            display: flex; align-items: center; gap: 10px;
            font-size: 13px; color: var(--text2); margin-bottom: 16px;
        }
        .hero-meta .rating { color: var(--gold); font-weight: 700; }
        .hero-meta .dot { width: 3px; height: 3px; border-radius: 50%; background: var(--text3); }
        .hero-overview {
            font-size: 13px; color: var(--text2); line-height: 1.5;
            max-width: 75%; display: -webkit-box;
            -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
            margin-bottom: 16px;
        }
        .hero-btn {
            display: inline-flex; align-items: center; gap: 8px;
            background: var(--accent); color: #fff;
            padding: 12px 26px; border-radius: var(--radius);
            font-family: 'Outfit', sans-serif; font-size: 14px; font-weight: 700;
            border: none; cursor: pointer;
            transition: background 0.25s, transform 0.15s, box-shadow 0.25s;
            text-transform: uppercase; letter-spacing: 0.5px;
            box-shadow: 0 4px 14px rgba(229, 9, 20, 0.3);
        }
        .hero-btn:hover { background: #ff0f1b; box-shadow: 0 6px 20px rgba(229, 9, 20, 0.45); }
        .hero-btn:active { transform: scale(0.97); }
        .hero-dots {
            display: flex; gap: 6px; margin-top: 16px;
        }
        .hero-dot {
            width: 24px; height: 3px; border-radius: 2px;
            background: rgba(255,255,255,0.25); cursor: pointer;
            transition: background 0.3s, width 0.3s;
        }
        .hero-dot.active { background: var(--accent); width: 36px; }

        /* ── MAIN CONTENT ── */
        .main { padding: 0 0 20px; }

        /* ── ROWS ── */
        .row-section { margin-bottom: 32px; }
        .row-header {
            display: flex; align-items: center; justify-content: space-between;
            padding: 0 20px; margin-bottom: 14px;
        }
        .row-title {
            font-size: 17px; font-weight: 700; letter-spacing: -0.2px;
            color: #fff;
        }
        .row-title span {
            display: inline-block; width: 4px; height: 16px;
            background: var(--accent); border-radius: 2px; margin-right: 8px;
            vertical-align: middle;
        }
        .row-see-all {
            font-size: 12px; color: var(--text3); cursor: pointer;
            font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;
        }
        /* PC: show thin custom scrollbar, mobile: hide */
        .poster-scroll {
            display: flex; gap: 12px; overflow-x: auto;
            padding: 12px 16px 20px;
            scroll-snap-type: x mandatory;
            scroll-padding: 0 16px;
            cursor: grab;
            scrollbar-width: thin;
            scrollbar-color: rgba(229,9,20,0.4) transparent;
        }
        .poster-scroll:active { cursor: grabbing; }
        .poster-scroll::-webkit-scrollbar { height: 4px; }
        .poster-scroll::-webkit-scrollbar-track { background: transparent; }
        .poster-scroll::-webkit-scrollbar-thumb { background: rgba(229,9,20,0.4); border-radius: 2px; }
        @media (pointer: coarse) {
            .poster-scroll { scrollbar-width: none; }
            .poster-scroll::-webkit-scrollbar { display: none; }
        }

        /* ── POSTER CARD ── */
        .poster-card {
            flex-shrink: 0; width: 120px; scroll-snap-align: start;
            cursor: pointer; position: relative;
            transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1), box-shadow 0.3s ease;
        }
        .poster-card:hover {
            transform: translateY(-5px) scale(1.04);
            z-index: 5;
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.5);
        }
        .poster-card:active { transform: scale(0.97); }
        .poster-img-wrap {
            width: 120px; height: 178px; border-radius: var(--radius-sm);
            overflow: hidden; background: var(--card2);
            position: relative;
            border: 1px solid var(--border);
            transition: border-color 0.3s ease;
        }
        .poster-card:hover .poster-img-wrap {
            border-color: rgba(229, 9, 20, 0.4);
        }
        .poster-img {
            width: 100%; height: 100%; object-fit: cover;
            transition: transform 0.5s cubic-bezier(0.25, 0.8, 0.25, 1);
        }
        .poster-card:hover .poster-img {
            transform: scale(1.06);
        }
        .poster-placeholder {
            width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
            background: linear-gradient(135deg, #1e1e2f 0%, #11111d 100%);
            border: 1px solid rgba(255, 255, 255, 0.03);
            color: var(--text3); font-size: 30px;
            border-radius: var(--radius-sm);
        }
        .poster-rating {
            position: absolute; top: 6px; right: 6px;
            background: rgba(0,0,0,0.8); backdrop-filter: blur(8px);
            color: var(--gold); font-size: 10px; font-weight: 700;
            padding: 2px 6px; border-radius: 4px;
            display: flex; align-items: center; gap: 3px;
        }
        .poster-type-badge {
            position: absolute; bottom: 6px; left: 6px;
            background: rgba(0,0,0,0.75); backdrop-filter: blur(8px);
            color: var(--text2); font-size: 9px; font-weight: 600;
            padding: 2px 6px; border-radius: 3px; text-transform: uppercase; letter-spacing: 0.5px;
        }
        .poster-title {
            font-size: 11px; font-weight: 600; color: var(--text2);
            margin-top: 7px; line-height: 1.3;
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .poster-year { font-size: 10px; color: var(--text3); margin-top: 2px; }

        /* ── FILE MODAL ── */
        .modal-backdrop {
            position: fixed; inset: 0; z-index: 300;
            background: rgba(0,0,0,0.88); backdrop-filter: blur(16px);
            display: flex; align-items: flex-end; justify-content: center;
            opacity: 0; visibility: hidden;
            transition: opacity 0.3s, visibility 0.3s;
        }
        .modal-backdrop.open { opacity: 1; visibility: visible; }
        .modal-sheet {
            background: var(--card); border-radius: 20px 20px 0 0;
            width: 100%; max-width: 600px; max-height: 85vh;
            display: flex; flex-direction: column;
            transform: translateY(100%); transition: transform 0.35s cubic-bezier(0.4,0,0.2,1);
            overflow: hidden;
        }
        .modal-backdrop.open .modal-sheet { transform: translateY(0); }
        .modal-handle {
            width: 36px; height: 4px; background: var(--text3);
            border-radius: 2px; margin: 14px auto 0; flex-shrink: 0;
        }
        .modal-header {
            display: flex; align-items: flex-start; gap: 14px;
            padding: 16px 20px; flex-shrink: 0;
        }
        .modal-poster {
            width: 64px; height: 95px; border-radius: var(--radius-sm);
            object-fit: cover; flex-shrink: 0; background: var(--card2);
        }
        .modal-poster-placeholder {
            width: 64px; height: 95px; border-radius: var(--radius-sm);
            background: var(--card2); display: flex; align-items: center;
            justify-content: center; font-size: 24px; flex-shrink: 0;
        }
        .modal-info { flex: 1; min-width: 0; }
        .modal-title {
            font-size: 18px; font-weight: 800; line-height: 1.2;
            margin-bottom: 5px; letter-spacing: -0.3px;
        }
        .modal-meta {
            display: flex; align-items: center; gap: 8px;
            font-size: 12px; color: var(--text2); margin-bottom: 8px;
        }
        .modal-meta .rating { color: var(--gold); font-weight: 700; }
        .modal-overview {
            font-size: 12px; color: var(--text3); line-height: 1.5;
            display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .modal-close-btn {
            width: 32px; height: 32px; flex-shrink: 0; background: var(--card2);
            border: none; border-radius: 50%; cursor: pointer; color: var(--text2);
            display: flex; align-items: center; justify-content: center;
            transition: background 0.2s, color 0.2s, transform 0.2s;
        }
        .modal-close-btn:hover { background: var(--border); color: #fff; transform: rotate(90deg); }
        .modal-divider { height: 1px; background: var(--border); flex-shrink: 0; }
        .modal-files-label {
            padding: 14px 20px 10px; font-size: 12px; font-weight: 700;
            color: var(--text3); text-transform: uppercase; letter-spacing: 1px;
            flex-shrink: 0;
        }
        .modal-files {
            overflow-y: auto; flex: 1; padding: 0 12px 20px;
        }
        .file-item {
            display: flex; align-items: center; gap: 12px;
            padding: 14px 12px; border-radius: var(--radius);
            cursor: pointer; transition: background 0.2s, transform 0.1s;
            border-bottom: 1px solid var(--border);
            margin-bottom: 4px;
        }
        .file-item:last-child { border-bottom: none; }
        .file-item:hover { background: var(--card2); transform: translateX(2px); }
        .file-item:active { background: rgba(229,9,20,0.1); transform: scale(0.99); }
        
        /* Genre pills in modal */
        .modal-genres {
            display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0;
        }
        .genre-pill {
            background: rgba(255,255,255,0.04); border: 1px solid var(--border);
            color: var(--text2); font-size: 10px; font-weight: 600;
            padding: 3px 8px; border-radius: 20px;
            letter-spacing: 0.2px;
        }
        .file-icon {
            width: 38px; height: 38px; border-radius: var(--radius-sm);
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            display: flex; align-items: center; justify-content: center;
            flex-shrink: 0;
        }
        .file-item-info { flex: 1; min-width: 0; }
        .file-item-name {
            font-size: 13px; font-weight: 600; color: #fff;
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
            overflow: hidden; line-height: 1.4; margin-bottom: 3px;
        }
        .file-item-size { font-size: 11px; color: var(--text3); font-weight: 500; }
        .file-item-get {
            width: 30px; height: 30px; flex-shrink: 0;
            background: rgba(229,9,20,0.15); border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            color: var(--accent);
        }
        .modal-loading {
            text-align: center; padding: 40px 20px; color: var(--text3);
            font-size: 14px;
        }
        .season-scroll{
            display:flex;
            overflow-x:auto;
            gap:10px;
            padding-bottom:10px;
            margin-bottom:15px;
            scrollbar-width:none;
        }

        .season-scroll::-webkit-scrollbar{
            display:none;
        }

        .season-btn{
            flex:0 0 auto;
            border:none;
            border-radius:12px;
            padding:10px 16px;
            cursor:pointer;
            background:#222;
            color:#fff;
            white-space:nowrap;
        }
        .modal-empty {
            text-align: center; padding: 40px 20px;
        }
        .modal-empty-icon { font-size: 40px; margin-bottom: 12px; }
        .modal-empty-title { font-size: 16px; font-weight: 700; margin-bottom: 6px; }
        .modal-empty-sub { font-size: 13px; color: var(--text3); line-height: 1.5; }

        /* ── REPAIR OVERLAY ── */
        .repair-overlay {
            position: fixed; inset: 0; z-index: 500;
            background: var(--bg);
            display: none; align-items: center; justify-content: center;
            flex-direction: column; text-align: center; padding: 40px 30px;
        }
        .repair-overlay.show { display: flex; }
        .repair-icon { font-size: 72px; margin-bottom: 24px; }
        .repair-title { font-size: 26px; font-weight: 800; margin-bottom: 10px; }
        .repair-sub { font-size: 15px; color: var(--text2); line-height: 1.6; max-width: 320px; }

        /* ── SKELETON ── */
        .skel { background: linear-gradient(90deg, var(--card) 25%, var(--card2) 50%, var(--card) 75%); background-size: 200% 100%; animation: shimmer 1.4s infinite; border-radius: var(--radius-sm); }
        @keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }
        .skel-poster { width: 120px; height: 178px; border-radius: var(--radius-sm); flex-shrink: 0; }
        .skel-text { height: 12px; border-radius: 6px; margin-top: 8px; }

        /* ── SPINNER ── */
        .spinner {
            width: 28px; height: 28px; border: 3px solid var(--border);
            border-top-color: var(--accent); border-radius: 50%;
            animation: spin 0.7s linear infinite; margin: 0 auto 12px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        /* ── FADE ANIMATIONS ── */
        @keyframes fadeUp { from { opacity:0; transform:translateY(16px); } to { opacity:1; transform:translateY(0); } }
        .fade-up { animation: fadeUp 0.4s ease both; }

        /* ── TOAST ── */
        .toast {
            position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%) translateY(20px);
            background: var(--card2); border: 1px solid var(--border);
            color: #fff; font-size: 13px; font-weight: 600;
            padding: 10px 20px; border-radius: 20px;
            opacity: 0; transition: opacity 0.3s, transform 0.3s; z-index: 999;
            white-space: nowrap;
        }
        .toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }

        /* ── FOOTER ── */
        .site-footer {
            background: linear-gradient(to top, rgba(0,0,0,0.6) 0%, transparent 100%);
            border-top: 1px solid var(--border);
            padding: 36px 24px 40px;
            text-align: center;
            margin-top: 10px;
        }
        .footer-logo {
            font-size: 20px; font-weight: 900; letter-spacing: -0.3px;
            background: linear-gradient(135deg, #fff 0%, var(--accent) 60%, var(--accent2) 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
            display: inline-block; margin-bottom: 8px;
        }
        .footer-tagline {
            font-size: 12px; color: var(--text3); margin-bottom: 20px; letter-spacing: 0.3px;
        }
        .footer-links {
            display: flex; align-items: center; justify-content: center;
            gap: 20px; margin-bottom: 20px; flex-wrap: wrap;
        }
        .footer-link {
            font-size: 12px; color: var(--text2); text-decoration: none; font-weight: 600;
            letter-spacing: 0.3px; transition: color 0.2s;
        }
        .footer-link:hover { color: var(--accent); }
        .footer-divider {
            width: 40px; height: 2px; border-radius: 1px;
            background: linear-gradient(90deg, transparent, var(--accent), transparent);
            margin: 0 auto 16px;
        }
        .footer-copy {
            font-size: 11px; color: var(--text3); line-height: 1.6;
        }
        .footer-powered {
            display: inline-flex; align-items: center; gap: 5px;
            font-size: 11px; color: var(--text3); margin-top: 6px;
        }
        .footer-powered a { color: var(--accent); text-decoration: none; font-weight: 700; }
        .footer-tmdb {
            font-size: 10px; color: var(--text3); margin-top: 8px; opacity: 0.6;
        }

        @media (min-width: 600px) {
            .poster-card { width: 150px; }
            .poster-img-wrap { width: 150px; height: 224px; }
            .skel-poster { width: 150px; height: 224px; }
            .search-top-bar { padding-top: 80px; padding-left: 24px; padding-right: 24px; }
            .search-results-grid { padding-left: 24px; padding-right: 24px; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 16px; }
        }
        @media (min-width: 900px) {
            .poster-card { width: 170px; }
            .poster-img-wrap { width: 170px; height: 255px; }
            .skel-poster { width: 170px; height: 255px; }
            .row-header { padding: 0 36px; }
            .poster-scroll { padding: 12px 24px 20px; scroll-padding: 0 24px; }
            .hero-content { padding: 0 48px 44px; }
            .hero-title { font-size: 52px; max-width: 58%; }
            .hero-overview { max-width: 52%; font-size: 15px; }
            .search-results-grid { grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 20px; }
        }
    </style>
</head>
<body>

<!-- REPAIR MODE OVERLAY -->
<div class="repair-overlay" id="repairOverlay">
    <div class="repair-icon">🔧</div>
    <div class="repair-title">Under Maintenance</div>
    <div class="repair-sub">Sorry for the inconvenience, we are under Maintenance. We'll be back soon!</div>
</div>

<!-- NAVBAR -->
<nav class="navbar" id="navbar">
    <div class="nav-logo">Filmotainment</div>
    <div class="nav-right">
        <button class="nav-search-toggle" id="searchToggle" onclick="openSearch()" title="Search">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        </button>
    </div>
</nav>

<!-- SEARCH OVERLAY -->
<div class="search-overlay" id="searchOverlay">
    <!-- Top bar: input + cancel always inline -->
    <div class="search-top-bar">
        <div class="search-field-wrap">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input class="search-field" id="searchField" type="text" placeholder="Movies, TV shows..." autocomplete="off">
        </div>
        <button class="search-close" onclick="closeSearch()">Cancel</button>
    </div>
    <div class="search-results-grid" id="searchResultsGrid">
        <div class="search-hint" style="grid-column:1/-1">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            Search for movies and TV shows
        </div>
    </div>
</div>

<!-- HERO SECTION -->
<section class="hero" id="hero">
    <div class="hero-bg" id="heroBg"></div>
    <div class="hero-gradient"></div>
    <div class="hero-gradient-side"></div>
    <div class="hero-content">
        <div class="hero-badge">🔥 Trending</div>
        <div class="hero-title" id="heroTitle">Loading...</div>
        <div class="hero-meta" id="heroMeta"></div>
        <div class="hero-overview" id="heroOverview"></div>
        <button class="hero-btn" id="heroBtn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M5 3l14 9-14 9V3z"/></svg>
            Get Files
        </button>
        <div class="hero-dots" id="heroDots"></div>
    </div>
</section>

<!-- MAIN CONTENT ROWS -->
<main class="main" id="main">

    <!-- Trending Row -->
    <section class="row-section fade-up">
        <div class="row-header">
            <div class="row-title"><span></span>Trending This Week</div>
        </div>
        <div class="poster-scroll" id="rowTrending">
            <!-- skeleton -->
            <div class="skel skel-poster"></div><div class="skel skel-poster"></div>
            <div class="skel skel-poster"></div><div class="skel skel-poster"></div>
            <div class="skel skel-poster"></div>
        </div>
    </section>

    <!-- Popular Movies Row -->
    <section class="row-section fade-up" style="animation-delay:0.08s">
        <div class="row-header">
            <div class="row-title"><span></span>Popular Movies</div>
        </div>
        <div class="poster-scroll" id="rowMovies">
            <div class="skel skel-poster"></div><div class="skel skel-poster"></div>
            <div class="skel skel-poster"></div><div class="skel skel-poster"></div>
            <div class="skel skel-poster"></div>
        </div>
    </section>

    <!-- Popular TV Row -->
    <section class="row-section fade-up" style="animation-delay:0.16s">
        <div class="row-header">
            <div class="row-title"><span></span>Popular TV Shows</div>
        </div>
        <div class="poster-scroll" id="rowTV">
            <div class="skel skel-poster"></div><div class="skel skel-poster"></div>
            <div class="skel skel-poster"></div><div class="skel skel-poster"></div>
            <div class="skel skel-poster"></div>
        </div>
    </section>

    <!-- Top Rated Row -->
    <section class="row-section fade-up" style="animation-delay:0.24s">
        <div class="row-header">
            <div class="row-title"><span></span>Top Rated</div>
        </div>
        <div class="poster-scroll" id="rowTopRated">
            <div class="skel skel-poster"></div><div class="skel skel-poster"></div>
            <div class="skel skel-poster"></div><div class="skel skel-poster"></div>
            <div class="skel skel-poster"></div>
        </div>
    </section>

</main>

<!-- PREMIUM FOOTER -->
<footer class="site-footer">
    <div class="footer-logo">Filmotainment</div>
    <div class="footer-tagline">Your premium media discovery platform</div>
    <div class="footer-divider"></div>
    <div class="footer-links">
        <a href="https://t.me/FT_Channels" class="footer-link" target="_blank">Telegram Channel</a>
        <a href="https://t.me/TeamYoonseri" class="footer-link" target="_blank">Support</a>
        <a href="https://www.themoviedb.org" class="footer-link" target="_blank">TMDB</a>
    </div>
    <div class="footer-copy">&copy; <span id="footerYear"></span>Filmotainment. All rights reserved.</div>
    <div class="footer-powered">Powered by <a href="https://t.me/FT_Channels" target="_blank">Filmotainment</a></div>
    <div class="footer-tmdb">This product uses the TMDB API but is not endorsed or certified by TMDB.</div>
</footer>

<!-- FILE MODAL -->
<div class="modal-backdrop" id="modalBackdrop" onclick="handleBackdropClick(event)">
    <div class="modal-sheet" id="modalSheet">
        <div class="modal-handle"></div>
        <div class="modal-header" id="modalHeader">
            <div class="modal-poster-placeholder" id="modalPosterWrap">🎬</div>
            <div class="modal-info" id="modalInfo"></div>
            <button class="modal-close-btn" onclick="closeModal()">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
        </div>
        <div class="modal-divider"></div>
        <div class="modal-files-label">Available Files</div>
        <div class="modal-files" id="modalFiles"></div>
    </div>
</div>

<!-- TOAST -->
<div class="toast" id="toast"></div>

<script>
// ── INIT ──────────────────────────────────────────────────────────────────
const tg = window.Telegram?.WebApp;
if (tg) {
    tg.expand();
    tg.setBackgroundColor('#0a0a0f');
    tg.setHeaderColor('#0a0a0f');
}
const user = tg?.initDataUnsafe?.user;
const userId = user?.id || 'unknown';
let botUsername = '';

// Auto-update copyright year
document.getElementById('footerYear').textContent = new Date().getFullYear();

// Navbar: always solid in Telegram Mini App, scroll-driven in browser
const navEl = document.getElementById('navbar');
if (tg) {
    navEl.classList.add('solid'); // always opaque in Telegram
} else {
    window.addEventListener('scroll', () => {
        navEl.classList.toggle('solid', window.scrollY > 20);
    }, { passive: true });
}

// ── MOUSE-DRAG HORIZONTAL SCROLL (PC) ─────────────────────────────────────
function enableDragScroll(el) {
    let isDown = false, startX, scrollLeft;
    el.addEventListener('mousedown', e => {
        isDown = true; el.classList.add('active');
        startX = e.pageX - el.offsetLeft;
        scrollLeft = el.scrollLeft;
        e.preventDefault();
    });
    el.addEventListener('mouseleave', () => { isDown = false; el.classList.remove('active'); });
    el.addEventListener('mouseup',    () => { isDown = false; el.classList.remove('active'); });
    el.addEventListener('mousemove', e => {
        if (!isDown) return;
        e.preventDefault();
        const x = e.pageX - el.offsetLeft;
        const walk = (x - startX) * 1.5;
        el.scrollLeft = scrollLeft - walk;
    });
}
// Apply to existing rows (also called after dynamic render)
document.querySelectorAll('.poster-scroll').forEach(enableDragScroll);

// ── HERO ──────────────────────────────────────────────────────────────────
let heroItems = [];
let heroIndex = 0;
let heroTimer = null;

function setHero(item) {
    const bg = document.getElementById('heroBg');
    const title = document.getElementById('heroTitle');
    const meta = document.getElementById('heroMeta');
    const overview = document.getElementById('heroOverview');
    const btn = document.getElementById('heroBtn');

    if (item.backdrop) {
        bg.style.backgroundImage = `url('${item.backdrop}')`;
        bg.style.opacity = '1';
    } else {
        bg.style.opacity = '0';
    }
    title.textContent = item.title;
    overview.textContent = item.overview || '';
    meta.innerHTML = `
        ${item.rating > 0 ? `<span class="rating">⭐ ${item.rating}</span><span class="dot"></span>` : ''}
        <span>${item.year || ''}</span>
        ${item.year ? '<span class="dot"></span>' : ''}
        <span style="text-transform:capitalize">${item.type === 'tv' ? 'TV Show' : 'Movie'}</span>
    `;
    btn.onclick = () => openModal(item);
}

function updateDots() {
    const dots = document.getElementById('heroDots');
    [...dots.children].forEach((d, i) => {
        d.classList.toggle('active', i === heroIndex);
    });
}

function startHeroRotation() {
    if (heroItems.length <= 1) return;
    clearInterval(heroTimer);
    heroTimer = setInterval(() => {
        heroIndex = (heroIndex + 1) % Math.min(heroItems.length, 6);
        setHero(heroItems[heroIndex]);
        updateDots();
    }, 5000);
}

// ── RENDER ROW ────────────────────────────────────────────────────────────
function renderRow(containerId, items) {
    const el = document.getElementById(containerId);
    el.innerHTML = '';
    items.forEach((item, i) => {
        const card = document.createElement('div');
        card.className = 'poster-card';
        card.style.animationDelay = `${i * 0.04}s`;
        const posterHTML = item.poster
            ? `<img class="poster-img" src="${item.poster}" alt="${item.title}" loading="lazy" onerror="this.parentElement.innerHTML='<div class=\\'poster-placeholder\\'>🎬</div>'">`
            : `<div class="poster-placeholder">🎬</div>`;
        card.innerHTML = `
            <div class="poster-img-wrap">
                ${posterHTML}
                ${item.rating > 0 ? `<div class="poster-rating">⭐ ${item.rating}</div>` : ''}
                <div class="poster-type-badge">${item.type === 'tv' ? 'TV' : 'Movie'}</div>
            </div>
            <div class="poster-title">${item.title}</div>
            ${item.year ? `<div class="poster-year">${item.year}</div>` : ''}
        `;
        card.onclick = () => openModal(item);
        el.appendChild(card);
    });
}

// ── LOAD HOME ─────────────────────────────────────────────────────────────
async function loadHome() {
    // Check repair mode first
    try {
        const rs = await fetch('/api/repair-status');
        const rd = await rs.json();
        if (rd.repair_mode) {
            document.getElementById('repairOverlay').classList.add('show');
            return;
        }
    } catch(e) {}

    try {
        const resp = await fetch('/api/tmdb-trending');
        const data = await resp.json();
        botUsername = data.bot_username || botUsername;

        // Hero
        heroItems = (data.trending || []).filter(x => x.backdrop).slice(0, 6);
        if (heroItems.length === 0) heroItems = (data.trending || []).slice(0, 6);
        if (heroItems.length > 0) {
            setHero(heroItems[0]);
            // Build dots
            const dotsEl = document.getElementById('heroDots');
            dotsEl.innerHTML = '';
            heroItems.slice(0, 6).forEach((_, i) => {
                const d = document.createElement('div');
                d.className = 'hero-dot' + (i === 0 ? ' active' : '');
                d.onclick = () => { heroIndex = i; setHero(heroItems[i]); updateDots(); clearInterval(heroTimer); startHeroRotation(); };
                dotsEl.appendChild(d);
            });
            startHeroRotation();
        }

        // Rows + re-apply drag scroll after populating
        if (data.trending) { renderRow('rowTrending', data.trending); enableDragScroll(document.getElementById('rowTrending')); }
        if (data.popular_movies) { renderRow('rowMovies', data.popular_movies); enableDragScroll(document.getElementById('rowMovies')); }
        if (data.popular_tv) { renderRow('rowTV', data.popular_tv); enableDragScroll(document.getElementById('rowTV')); }
        if (data.top_rated) { renderRow('rowTopRated', data.top_rated); enableDragScroll(document.getElementById('rowTopRated')); }

    } catch(e) {
        console.error('Failed to load home:', e);
        document.getElementById('heroTitle').textContent = 'Failed to load';
    }
}

// ── SEARCH ────────────────────────────────────────────────────────────────
let searchTimer = null;

function openSearch() {
    document.getElementById('searchOverlay').classList.add('open');
    setTimeout(() => document.getElementById('searchField').focus(), 300);
}

function closeSearch() {
    document.getElementById('searchOverlay').classList.remove('open');
    document.getElementById('searchField').value = '';
    document.getElementById('searchResultsGrid').innerHTML = `
        <div class="search-hint" style="grid-column:1/-1">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            Search for movies and TV shows
        </div>`;
}

// Close search on Escape
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeSearch(); });

document.getElementById('searchField').addEventListener('input', (e) => {
    clearTimeout(searchTimer);
    const q = e.target.value.trim();
    if (!q) {
        closeSearch();
        openSearch();
        return;
    }
    document.getElementById('searchResultsGrid').innerHTML = `
        <div class="search-hint" style="grid-column:1/-1">
            <div class="spinner"></div>Searching...
        </div>`;
    searchTimer = setTimeout(() => doSearch(q), 400);
});

document.getElementById('searchField').addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeSearch();
});

async function doSearch(q) {
    try {
        const resp = await fetch(`/api/tmdb-search?q=${encodeURIComponent(q)}`);
        const data = await resp.json();
        const grid = document.getElementById('searchResultsGrid');
        grid.innerHTML = '';
        if (!data.results || data.results.length === 0) {
            grid.innerHTML = `<div class="search-hint" style="grid-column:1/-1">No results found for "<b>${q}</b>"</div>`;
            return;
        }
        // Results count bar
        const bar = document.createElement('div');
        bar.className = 'search-meta-bar';
        bar.style.gridColumn = '1 / -1';
        bar.innerHTML = `Found <b>${data.results.length}</b> results for "<b>${q}</b>"`;
        grid.appendChild(bar);
        // Render premium cards using the same poster-card structure
        data.results.forEach((item, idx) => {
            const card = document.createElement('div');
            card.className = 'poster-card';
            card.style.animationDelay = `${Math.min(idx * 0.04, 0.5)}s`;
            const posterHTML = item.poster
                ? `<img class="poster-img" src="${item.poster}" alt="${item.title}" loading="lazy" onerror="this.parentElement.innerHTML='<div class=\\'poster-placeholder\\'>🎬</div>'">`
                : `<div class="poster-placeholder">🎬</div>`;
            card.innerHTML = `
                <div class="poster-img-wrap">
                    ${posterHTML}
                    ${item.rating > 0 ? `<div class="poster-rating">⭐ ${item.rating}</div>` : ''}
                    <div class="poster-type-badge">${item.type === 'tv' ? 'TV' : 'Movie'}</div>
                </div>
                <div class="poster-title">${item.title}</div>
                ${item.year ? `<div class="poster-year">${item.year}</div>` : ''}
            `;
            card.onclick = () => { closeSearch(); openModal(item); };
            grid.appendChild(card);
        });
    } catch(e) {
        document.getElementById('searchResultsGrid').innerHTML = `<div class="search-hint" style="grid-column:1/-1">Search failed. Please try again.</div>`;
    }
}

// ── MODAL ─────────────────────────────────────────────────────────────────
let currentItem = null;

async function openModal(item) {
    currentItem = item;
    // Populate header
    const posterWrap = document.getElementById('modalPosterWrap');
    const info = document.getElementById('modalInfo');
    if (item.poster) {
        posterWrap.innerHTML = `<img class="modal-poster" src="${item.poster}" alt="${item.title}">`;
    } else {
        posterWrap.innerHTML = `<div class="modal-poster-placeholder">🎬</div>`;
    }
    
    // Client-side Genre Lookup mapping
    const genreMap = {
        28: 'Action', 12: 'Adventure', 16: 'Animation', 35: 'Comedy', 80: 'Crime',
        99: 'Documentary', 18: 'Drama', 10751: 'Family', 14: 'Fantasy', 36: 'History',
        27: 'Horror', 10402: 'Music', 9648: 'Mystery', 10749: 'Romance', 878: 'Sci-Fi',
        10770: 'TV Movie', 53: 'Thriller', 10752: 'War', 37: 'Western',
        10759: 'Action & Adventure', 10762: 'Kids', 10763: 'News', 10764: 'Reality',
        10765: 'Sci-Fi & Fantasy', 10766: 'Soap', 10767: 'Talk', 10768: 'War & Politics'
    };
    let genrePills = '';
    if (item.genres && item.genres.length > 0) {
        genrePills = `<div class="modal-genres">` + item.genres.slice(0, 3).map(id => `<span class="genre-pill">${genreMap[id] || 'Media'}</span>`).join('') + `</div>`;
    }
    
    info.innerHTML = `
        <div class="modal-title">${item.title}</div>
        <div class="modal-meta">
            ${item.rating > 0 ? `<span class="rating">⭐ ${item.rating}</span>` : ''}
            ${item.year ? `<span>${item.year}</span>` : ''}
            <span style="text-transform:capitalize">${item.type === 'tv' ? 'TV Show' : 'Movie'}</span>
        </div>
        ${genrePills}
        ${item.overview ? `<div class="modal-overview">${item.overview}</div>` : ''}
    `;
    // Show modal
    document.getElementById('modalBackdrop').classList.add('open');
    document.body.style.overflow = 'hidden';
    // Load files
    await loadFilesForItem(item);
}

function closeModal() {
    document.getElementById('modalBackdrop').classList.remove('open');
    document.body.style.overflow = '';
    currentItem = null;
}

function handleBackdropClick(e) {
    if (e.target === document.getElementById('modalBackdrop')) closeModal();
}

async function loadFilesForItem(item) {
    const filesEl = document.getElementById('modalFiles');
    filesEl.innerHTML = `<div class="modal-loading"><div class="spinner"></div>Searching files...</div>`;
    try {
        const resp = await fetch(`/api/search?q=${encodeURIComponent(item.title)}&offset=0`);
        const data = await resp.json();
        botUsername = data.bot_username || botUsername;
        if (!data.files || data.files.length === 0) {
            filesEl.innerHTML = `
                <div class="modal-empty">
                    <div class="modal-empty-icon">📭</div>
                    <div class="modal-empty-title">No files found</div>
                    <div class="modal-empty-sub">We don't have files for "<b>${item.title}</b>" yet. Request it in our group!</div>
                </div>`;
            return;
        }
        filesEl.innerHTML = '';

        // TV Series Mode
        if (item.type === 'tv') {

            const grouped = {};

            data.files.forEach(file => {
                const season = file.season || 1;

                if (!grouped[season]) {
                    grouped[season] = [];
                }

                grouped[season].push(file);
            });

            const seasonBar = document.createElement('div');
            seasonBar.className = 'season-scroll';

            filesEl.appendChild(seasonBar);

            const episodeContainer = document.createElement('div');
            filesEl.appendChild(episodeContainer);

            const renderSeason = (seasonNo) => {

                episodeContainer.innerHTML = '';

                const episodes = {};

                grouped[seasonNo].forEach(file => {

                    const ep = file.episode || 1;

                    if (!episodes[ep]) {
                        episodes[ep] = [];
                    }

                    episodes[ep].push(file);

                });

                Object.keys(episodes)
                    .sort((a, b) => Number(a) - Number(b))
                    .forEach(ep => {

                        const el = document.createElement('div');

                        el.className = 'file-item';

                        el.innerHTML = `
                            <div class="file-icon">
                                <svg width="16" height="16" viewBox="0 0 24 24"
                                    fill="none" stroke="white" stroke-width="2.2"
                                    stroke-linecap="round">
                                    <polygon points="23 7 16 12 23 17 23 7"/>
                                    <rect x="1" y="5" width="15" height="14"
                                        rx="2" ry="2"/>
                                </svg>
                            </div>

                            <div class="file-item-info">
                                <div class="file-item-name">
                                    Episode ${ep}
                                </div>

                                <div class="file-item-size">
                                ${episodes[ep].length} Files Available
                                </div>
                            </div>

                        <div class="file-item-get">
                                →
                            </div>
                        `;

                        el.onclick = () => {
                            episodeContainer.innerHTML = '';

                            episodes[ep].forEach(file => {

                                const fileEl = document.createElement('div');

                                fileEl.className = 'file-item';

                                fileEl.innerHTML = `
                                    <div class="file-icon">
                                        <svg width="16" height="16" viewBox="0 0 24 24"
                                            fill="none" stroke="white" stroke-width="2.2"
                                            stroke-linecap="round">
                                            <polygon points="23 7 16 12 23 17 23 7"/>
                                            <rect x="1" y="5" width="15" height="14"
                                            rx="2" ry="2"/>
                                        </svg>
                                    </div>

                                    <div class="file-item-info">
                                        <div class="file-item-name">
                                            ${file.name}
                                        </div>

                                        <div class="file-item-size">
                                            ${file.size || ''}
                                        </div>
                                        </div>

                                    <div class="file-item-get">
                                        →
                                    </div>
                                `;

                                fileEl.onclick = () => getFile(file.id);

                                episodeContainer.appendChild(fileEl);
                            });
                        };

                        episodeContainer.appendChild(el);
                    });
            };
            function showEpisodeFiles(files) {

                const episodeContainer =
                    document.querySelector('.modal-files');

                episodeContainer.innerHTML = '';

                const languageSet = new Set();
                const qualitySet = new Set();

                files.forEach(file => {

                    const caption = file.caption || '';

                    caption.split(/\s+/).forEach(word => {

                        if (/^\d{3,4}p$/i.test(word)) {
                            qualitySet.add(word);
                        }

                    });

                });

                const filterBar = document.createElement('div');

                filterBar.style.marginBottom = '15px';

                filterBar.innerHTML = `
                    <select id="languageFilter">
                        <option>Language</option>
                    </select>

                    <select id="qualityFilter">
                        <option>Quality</option>
                    </select>
                `;

                episodeContainer.appendChild(filterBar);

                files.forEach(file => {

                    const card = document.createElement('div');

                    card.className = 'file-item';

                    card.innerHTML = `
                        <div class="file-item-info">
                            <div class="file-item-name">
                                ${file.name}
                            </div>

                            <div class="file-item-size">
                                ${file.size}
                            </div>
                        </div>
                    `;

                    card.onclick = () => getFile(file.id);

                    episodeContainer.appendChild(card);

                });

            }

            Object.keys(grouped)
                .sort((a, b) => Number(a) - Number(b))
                .forEach((season, index) => {

                    const btn = document.createElement('button');

                    btn.className = 'season-btn';

                    btn.textContent = `Season ${season}`;

                    btn.onclick = () => renderSeason(season);

                    seasonBar.appendChild(btn);

                    if (index === 0) {
                        renderSeason(season);
                    }
                });

        } else {

            data.files.forEach(file => {
                const el = document.createElement('div');
                el.className = 'file-item';

                el.innerHTML = `
                    <div class="file-icon">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round">
                            <polygon points="23 7 16 12 23 17 23 7"/>
                            <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
                        </svg>
                    </div>

                    <div class="file-item-info">
                        <div class="file-item-name">${file.name}</div>
                        <div class="file-item-size">${file.size}</div>
                    </div>

                    <div class="file-item-get">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
                            <path d="M5 12h14"/>
                            <path d="M12 5l7 7-7 7"/>
                        </svg>
                    </div>
                `;

                el.onclick = () => getFile(file.id);

                filesEl.appendChild(el);
            });
        }
    } catch(e) {
        filesEl.innerHTML = `<div class="modal-empty"><div class="modal-empty-icon">⚠️</div><div class="modal-empty-title">Error</div><div class="modal-empty-sub">Failed to load files.</div></div>`;
    }
}

function getFile(fileId) {
    const link = `https://t.me/${botUsername}?start=file_0_${fileId}`;
    if (userId === 'unknown' || !tg?.openTelegramLink) {
        window.open(link, '_blank');
    } else {
        tg.openTelegramLink(link);
        setTimeout(() => { tg.close(); }, 200);
    }
    showToast('Opening Telegram...');
}

// ── TOAST ─────────────────────────────────────────────────────────────────
function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 2500);
}

// ── BOOT ──────────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', loadHome);
</script>
</body>
</html>
"""

# ── NO TMDB KEY PAGE ──────────────────────────────────────────────────────
no_tmdb_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebApp Unavailable</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        * { box-sizing:border-box; margin:0; padding:0; }
        body {
            font-family:'Outfit',sans-serif; background:#0a0a0f; color:#fff;
            min-height:100vh; display:flex; align-items:center; justify-content:center;
            padding:30px 24px; text-align:center;
            background-image: radial-gradient(ellipse at 50% 0%, rgba(229,9,20,0.08) 0%, transparent 60%);
        }
        .wrap { max-width:380px; }
        .icon {
            width:90px; height:90px; border-radius:24px; margin:0 auto 28px;
            background:linear-gradient(135deg,#1a1a2e,#16213e);
            border:1px solid rgba(229,9,20,0.3);
            display:flex; align-items:center; justify-content:center; font-size:40px;
            box-shadow: 0 0 40px rgba(229,9,20,0.1);
        }
        h1 { font-size:26px; font-weight:800; margin-bottom:12px; letter-spacing:-0.5px; }
        p { font-size:15px; color:#888; line-height:1.7; }
        code {
            display:inline-block; background:#1e1e2a; color:#e50914;
            padding:3px 10px; border-radius:6px; font-size:14px;
            border:1px solid rgba(229,9,20,0.25); margin:4px 0;
            font-family:monospace;
        }
        .divider {
            width:60px; height:2px; background:linear-gradient(90deg,transparent,#e50914,transparent);
            margin:24px auto;
        }
        .note { font-size:12px; color:#444; margin-top:16px; }
    </style>
</head>
<body>
<div class="wrap">
    <div class="icon">🔑</div>
    <h1>WebApp Unavailable</h1>
    <div class="divider"></div>
    <p>The WebApp requires a <b>TMDB API Key</b> to function.</p>
    <p style="margin-top:12px">If you're an admin, set the environment variable:</p>
    <p style="margin-top:10px"><code>TMDB_API_KEY</code></p>
    <p style="margin-top:14px; color:#555">Get your free API key at<br><span style="color:#e50914">themoviedb.org/settings/api</span></p>
    <div class="note">This message is only shown when the key is not configured.</div>
</div>
<script>
    const tg = window.Telegram?.WebApp;
    if (tg) { tg.expand(); tg.setBackgroundColor('#0a0a0f'); }
</script>
</body>
</html>
"""
# ─────────────────────────────────────────────────────────────────────────────
# WATCH PAGE TEMPLATE  (route: /watch/{id})
# ─────────────────────────────────────────────────────────────────────────────
watch_tmplt = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{heading}</title>
    <!-- Plyr CSS -->
    <link rel="stylesheet" href="https://cdn.plyr.io/3.7.8/plyr.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">
    <style>
        :root {
            --p:#818cf8; --p2:#6366f1; --sec:#a78bfa; --acc:#38bdf8;
            --txt:#f1f5f9; --txt2:#94a3b8;
            --bg:#020617; --glass:rgba(10,18,38,.8); --gb:rgba(129,140,248,.13);
        }
        *, *::before, *::after { margin:0; padding:0; box-sizing:border-box; }
        body {
            font-family:'Inter',sans-serif;
            background:var(--bg); color:var(--txt);
            min-height:100vh;
            display:flex; flex-direction:column;
            overflow-x:hidden;
        }
        body::before {
            content:''; position:fixed; inset:0; z-index:-1;
            background:
                radial-gradient(ellipse 75% 50% at 10% 20%, rgba(99,102,241,.12) 0%, transparent 58%),
                radial-gradient(ellipse 60% 40% at 90% 80%, rgba(167,139,250,.09) 0%, transparent 55%),
                linear-gradient(160deg, #020617 0%, #070c1b 45%, #0f172a 100%);
        }

        /* Header */
        header {
            padding:.8rem 1.5rem;
            backdrop-filter:blur(24px) saturate(180%);
            -webkit-backdrop-filter:blur(24px) saturate(180%);
            background:var(--glass);
            border-bottom:1px solid var(--gb);
            display:flex; flex-direction:column; align-items:center; justify-content:center;
            box-shadow:0 1px 32px rgba(0,0,0,.45);
        }
        .header-logo {
            font-size:1rem; font-weight:800; letter-spacing:-.01em;
            background:linear-gradient(90deg,#e2e8f0 0%,var(--p) 50%,var(--acc) 100%);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
        }
        #file-name {
            font-size:.82rem; color:var(--txt2); margin-top:.3rem; font-weight:500;
            white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
            max-width:100%; text-align:center;
        }

        /* Container */
        .container {
            flex:1; display:flex; flex-direction:column; align-items:center;
            padding:2.5rem 1.5rem 3rem; width:100%;
        }

        /* Badge */
        .badge {
            display:inline-flex; align-items:center; gap:.4rem;
            background:rgba(16,185,129,.12); border:1px solid rgba(16,185,129,.3);
            padding:.3rem .9rem; border-radius:30px;
            font-size:.7rem; font-weight:700; letter-spacing:.05em; text-transform:uppercase; color:#10b981;
            margin-bottom:1.5rem; backdrop-filter:blur(8px);
        }
        .badge-dot {
            width:6px; height:6px; background:#10b981; border-radius:50%;
            box-shadow:0 0 10px #10b981; animation:pulse 2s cubic-bezier(.4,0,.6,1) infinite;
        }
        @keyframes pulse { 50% { opacity:.3; box-shadow:none; } }

        /* Player Wrap */
        .player-wrap {
            position:relative; width:100%; max-width:1060px;
            border-radius:24px; padding:1px; z-index:10;
        }
        .player-ambient {
            position:absolute; inset:-2px; z-index:-1;
            background:linear-gradient(135deg,rgba(99,102,241,.4),rgba(167,139,250,.2),rgba(56,189,248,.3));
            filter:blur(35px); opacity:.3; transform:translateZ(0); border-radius:inherit;
        }
        .player-card {
            position:relative; background:#000; border-radius:22px;
            overflow:hidden; box-shadow:0 25px 65px rgba(0,0,0,.5);
            aspect-ratio:16/9; display:flex; align-items:center; justify-content:center;
            width:100%;
        }
        .player-card video, .plyr video {
            width:100% !important; height:100% !important;
            object-fit:cover !important; border-radius:22px;
        }

        /* Load Skeleton */
        .skeleton {
            position:absolute; inset:0; background:#0a0e1c; z-index:20;
            overflow:hidden; pointer-events:none; transition:opacity .4s, visibility .4s;
        }
        .skeleton::after {
            content:''; position:absolute; inset:0;
            background:linear-gradient(90deg,transparent,rgba(129,140,248,.08),transparent);
            transform:translateX(-100%); animation:shimmer 1.8s infinite;
        }
        @keyframes shimmer { 100% { transform:translateX(100%); } }
        .skeleton.gone { opacity:0; visibility:hidden; }

        /* Video Error Overlay */
        .player-err-overlay {
            position:absolute; inset:0; z-index:50;
            background:rgba(2,6,23,.92); backdrop-filter:blur(14px);
            opacity:0; visibility:hidden;
            display:flex; align-items:center; justify-content:center;
            border-radius:22px; text-align:center; padding:2rem;
            transition:opacity .4s ease, visibility .4s ease;
        }
        .player-err-overlay.show { opacity:1; visibility:visible; }
        .err-card-sm { max-width:440px; width:100%; }
        .err-card-sm h2 { font-size:1.4rem; font-weight:800; margin-bottom:.5rem; letter-spacing:-.02em; }
        .err-card-sm p { font-size:.85rem; color:var(--txt2); margin-bottom:1.5rem; line-height:1.5; }
        .err-btn-grid {
            display:grid; grid-template-columns:repeat(3, 1fr); gap:.6rem; margin-top:1.2rem;
        }

        /* Buttons */
        .btn-row {
            display:grid; grid-template-columns:repeat(3, 1fr); gap:.8rem;
            margin-top:1.2rem;
            width:100%; max-width:1060px;
        }
        .xbtn {
            position:relative; overflow:hidden;
            display:flex; align-items:center; justify-content:center; gap:.5rem;
            width:100%; padding:.72rem .9rem;
            border-radius:11px; border:none;
            font-family:'Inter',sans-serif;
            font-size:.84rem; font-weight:600;
            letter-spacing:.01em;
            cursor:pointer; text-decoration:none; color:#fff;
            transition:transform .2s, box-shadow .2s, filter .2s;
        }
        .xbtn::after {
            content:''; position:absolute; inset:0;
            background:rgba(255,255,255,.08);
            opacity:0; transition:opacity .18s;
        }
        .xbtn:hover::after { opacity:1; }
        .xbtn:hover {
            transform:scale(1.02);
            filter:brightness(1.08);
        }
        .xbtn:active { transform:scale(.98); }

        /* Download – indigo */
        .btn-dl {
            background:linear-gradient(135deg,#4f46e5,#818cf8,#a78bfa);
            box-shadow:0 4px 16px rgba(99,102,241,.38);
        }
        .btn-dl:hover { box-shadow:0 7px 24px rgba(99,102,241,.55); }

        /* VLC – amber */
        .btn-vlc {
            background:linear-gradient(135deg,#92400e,#f59e0b,#fde68a);
            box-shadow:0 4px 16px rgba(245,158,11,.35);
        }
        .btn-vlc:hover { box-shadow:0 7px 24px rgba(245,158,11,.52); }

        /* MX – emerald */
        .btn-mx {
            background:linear-gradient(135deg,#065f46,#10b981,#6ee7b7);
            box-shadow:0 4px 16px rgba(16,185,129,.35);
        }
        .btn-mx:hover { box-shadow:0 7px 24px rgba(16,185,129,.52); }

        /* Footer */
        footer {
            padding:.85rem 1.5rem; text-align:center;
            color:var(--txt2); font-size:.73rem;
            margin-top:auto;
        }
        footer::before {
            content:''; display:block;
            width:90px; height:1px;
            background:linear-gradient(90deg,transparent,rgba(129,140,248,.28),transparent);
            margin:0 auto .7rem;
        }
        .ha-link {
            color:var(--p); text-decoration:none; font-weight:600;
            transition:opacity .2s;
        }
        .ha-link:hover { opacity:.7; }

        /* Plyr overrides */
        .plyr { width: 100% !important; height: 100% !important; }
        .plyr__controls {
            width: 100% !important;
            bottom: 0 !important;
            padding: 10px 15px !important;
            justify-content: space-between !important;
        }
        .plyr__progress { flex-grow: 1 !important; display: flex !important; }
        .plyr--video .plyr__control--overlaid {
            position: absolute !important;
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) !important;
            background:linear-gradient(135deg,var(--p2),var(--sec));
            box-shadow:0 0 20px rgba(129,140,248,.5);
            transition:opacity .2s ease, box-shadow .2s ease !important;
        }
        .plyr--video .plyr__control--overlaid:hover {
            transform: translate(-50%, -50%) !important;
            box-shadow:0 0 30px rgba(129,140,248,.7);
        }
        .plyr--video .plyr__control:hover,
        .plyr--video .plyr__control[aria-expanded="true"] { background:var(--p2); }
        .plyr__control.plyr__tab-focus { box-shadow:0 0 0 5px rgba(99,102,241,.4); }
        .plyr--full-ui input[type=range]  { color:var(--p); }
        .plyr__progress input[type=range] { color:var(--p); }
        .plyr__progress__buffer { color:rgba(129,140,248,.2); }
        .plyr__menu__container .plyr__control[role=menuitemradio][aria-checked=true]::before { background:var(--p); }

        /* Responsive */
        @media (max-width:600px) {
            .container { padding:1rem .85rem .85rem; }
            .btn-row, .err-btn-grid { grid-template-columns:1fr; gap:.6rem; }
            .xbtn { padding:.78rem 1rem; }
            #file-name { font-size:.78rem; }
        }
    </style>
</head>
<body>

<header>
    <span class="header-logo">Filmotainment</span>
    <div id="file-name">{file_name}</div>
</header>

<div class="container">

    <div class="badge">
        <span class="badge-dot"></span>
        ONLINE
    </div>

    <div class="player-wrap">
        <div class="player-ambient"></div>
        <div class="player-card">
            <div class="skeleton" id="skel"></div>

            <div class="player-err-overlay" id="vidErr">
                <div class="err-card-sm">
                    <div style="margin-bottom:1.2rem; color:rgba(255,255,255,0.7);">
                        <svg width="42" height="42" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                    </div>
                    <h2>Oops! The video failed to load.</h2>
                    <p>Please try downloading or opening it in an external player.</p>
                </div>
            </div>

            <video src="{src}" class="player" playsinline controls></video>
        </div>
    </div>

    <div class="btn-row">
        <!-- Download -->
        <a href="{src}" class="xbtn btn-dl" download>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            Download
        </a>

        <!-- VLC -->
        <a href="vlc://{src}" class="xbtn btn-vlc">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="5 3 19 12 5 21 5 3"/>
            </svg>
            Play in VLC
        </a>

        <!-- MX Player -->
        <a href="intent:{src}#Intent;package=com.mxtech.videoplayer.ad;end" class="xbtn btn-mx">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <polygon points="10 8 16 12 10 16 10 8"/>
            </svg>
            MX Player
        </a>
    </div>

</div>

<footer>
    <p>Powered by <a href="https://t.me/FT_Channels" class="ha-link" target="_blank" rel="noopener">Filmotainment</a></p>
</footer>

<script src="https://cdn.plyr.io/3.7.8/plyr.js"></script>
<script>
document.addEventListener('DOMContentLoaded', () => {
    const skel    = document.getElementById('skel');
    const vidErr  = document.getElementById('vidErr');
    const videoEl = document.querySelector('.player');

    const player = new Plyr('.player', {
        controls: ['play-large','play','progress','current-time','duration',
                   'mute','volume','captions','settings','pip','airplay','fullscreen'],
        settings: ['captions','quality','speed'],
        hideControls: false,
        tooltips: { controls:true, seek:true }
    });

    let errTriggered = false;
    const hideSkel = () => { if (skel) skel.classList.add('gone'); };
    const showError = () => {
        if (errTriggered) return;
        errTriggered = true;
        hideSkel();
        if (vidErr) vidErr.classList.add('show');
        if (player && player.elements && player.elements.container) {
            player.elements.container.style.display = 'none';
        }
    };
    
    videoEl.addEventListener('loadedmetadata', hideSkel);
    videoEl.addEventListener('canplay', hideSkel);
    
    // Core HTML5 error events
    ['error', 'abort', 'stalled'].forEach(evt => {
        videoEl.addEventListener(evt, () => {
            if (videoEl.error || videoEl.networkState === 3) showError();
        });
    });
    
    // Fallback timeout for unresponsive streams
    let loadTimeout = setTimeout(() => {
        if (videoEl.readyState === 0) showError();
        hideSkel();
    }, 12000);
    
    videoEl.addEventListener('playing', () => clearTimeout(loadTimeout));
});
</script>
</body>
</html>
"""


# ─────────────────────────────────────────────────────────────────────────────
# ERROR PAGE TEMPLATE
# ─────────────────────────────────────────────────────────────────────────────
error_tmplt = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error — Filmotainment</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">
    <style>
        :root {
            --p:#818cf8; --p2:#6366f1; --sec:#a78bfa; --acc:#38bdf8;
            --txt:#f1f5f9; --txt2:#94a3b8;
            --bg:#020617; --glass:rgba(10,18,38,.8); --gb:rgba(129,140,248,.13);
            --err:#f43f5e; --err2:rgba(244,63,94,.15);
        }
        *, *::before, *::after { margin:0; padding:0; box-sizing:border-box; }
        body {
            font-family:'Inter',sans-serif;
            background:var(--bg);
            color:var(--txt);
            min-height:100vh;
            display:flex; flex-direction:column;
            overflow-x:hidden;
        }
        body::before {
            content:''; position:fixed; inset:0; z-index:-1;
            background:
                radial-gradient(ellipse 65% 45% at 50% 40%, rgba(244,63,94,.07) 0%, transparent 62%),
                radial-gradient(ellipse 75% 50% at 10% 20%, rgba(99,102,241,.10) 0%, transparent 58%),
                linear-gradient(160deg, #020617 0%, #070c1b 45%, #0f172a 100%);
        }

        /* Header */
        header {
            padding:.8rem 1.5rem;
            backdrop-filter:blur(24px) saturate(180%);
            -webkit-backdrop-filter:blur(24px) saturate(180%);
            background:var(--glass);
            border-bottom:1px solid var(--gb);
            box-shadow:0 1px 32px rgba(0,0,0,.45);
            display:flex; justify-content:center; align-items:center;
            animation:fadeDown .45s ease both;
        }
        @keyframes fadeDown {
            from { opacity:0; transform:translateY(-12px); }
            to   { opacity:1; transform:translateY(0); }
        }
        .header-logo {
            font-size:1rem; font-weight:800; letter-spacing:-.01em;
            background:linear-gradient(90deg,#e2e8f0 0%,var(--p) 50%,var(--acc) 100%);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
        }

        /* Error layout */
        main {
            flex:1; display:flex; align-items:center; justify-content:center;
            padding:3rem 1.25rem;
        }
        .error-card {
            background:var(--glass);
            border:1px solid rgba(244,63,94,.22);
            border-radius:20px;
            padding:2.5rem 2rem;
            text-align:center;
            max-width:440px; width:100%;
            box-shadow:
                0 0 0 1px rgba(255,255,255,.04),
                0 12px 48px rgba(0,0,0,.5),
                0 0 45px rgba(244,63,94,.09);
            backdrop-filter:blur(20px);
            animation:cardIn .5s ease both;
        }
        @keyframes cardIn {
            from { opacity:0; transform:translateY(22px) scale(.97); }
            to   { opacity:1; transform:translateY(0) scale(1); }
        }

        /* Error icon */
        .err-icon {
            width:66px; height:66px; border-radius:50%;
            margin:0 auto 1.4rem;
            background:var(--err2);
            border:1px solid rgba(244,63,94,.28);
            display:flex; align-items:center; justify-content:center;
            box-shadow:0 0 28px rgba(244,63,94,.18);
        }
        .err-icon svg { color:var(--err); }

        .err-label {
            font-size:.65rem; font-weight:700; letter-spacing:.1em;
            text-transform:uppercase; color:var(--err); margin-bottom:.55rem;
        }
        .error-card h2 {
            font-size:1.6rem; font-weight:800; letter-spacing:-.02em;
            margin-bottom:.65rem;
        }
        .error-card p {
            font-size:.88rem; color:var(--txt2); line-height:1.7;
            margin-bottom:1.75rem;
        }

        /* Buttons */
        .err-btns { display:flex; flex-direction:column; gap:.75rem; width:100%; align-items:center; }
        .ebtn {
            display:flex; align-items:center; justify-content:center; gap:.5rem;
            width:100%; max-width:280px;
            padding:.85rem 1.5rem; border-radius:12px;
            font-family:'Inter',sans-serif; font-size:.9rem; font-weight:700;
            cursor:pointer; text-decoration:none; color:#fff; border:none;
            transition:transform .2s, box-shadow .2s, filter .2s;
            background:linear-gradient(135deg,var(--p2),var(--p),var(--sec));
            box-shadow:0 4px 20px rgba(99,102,241,.45);
        }
        .ebtn:hover {
            transform:scale(1.02);
            box-shadow:0 6px 24px rgba(99,102,241,.55);
            filter:brightness(1.08);
        }
        .ebtn:active { transform:scale(.98); }

        /* Footer */
        footer {
            padding:.85rem 1.5rem; text-align:center;
            color:var(--txt2); font-size:.73rem;
        }
        footer::before {
            content:''; display:block;
            width:90px; height:1px;
            background:linear-gradient(90deg,transparent,rgba(129,140,248,.25),transparent);
            margin:0 auto .7rem;
        }
        .ha-link {
            color:var(--p); text-decoration:none; font-weight:600;
            transition:opacity .2s;
        }
        .ha-link:hover { opacity:.7; }
    </style>
</head>
<body>

<header>
    <span class="header-logo">Filmotainment</span>
</header>

<main>
  <div class="error-card">

    <div class="err-icon">
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
    </div>

    <div class="err-label">Error</div>
    <h2>Something went wrong</h2>
    <p>We couldn't load this file. It may have expired or there was a temporary issue.</p>

    <div class="err-btns">
      <button class="ebtn" onclick="location.reload()">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>
        Try Again
      </button>
      <a href="https://t.me/HA_Bots_Support" class="ebtn" target="_blank" rel="noopener">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
        Support Group
      </a>
    </div>

  </div>
</main>

<footer>
  <p>Powered by <a href="https://t.me/FT_Channels" class="ha-link" target="_blank" rel="noopener">Filmotainment</a></p>
</footer>
</body>
</html>
"""



payment_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Activate Premium</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--tg-theme-bg-color, #121212);
            color: var(--tg-theme-text-color, #ffffff);
            margin: 0; padding: 20px; text-align: center;
        }
        
        #block-screen { display: none; margin-top: 50px; color: #ff4d4d; }
        #app-content { display: none; } 

        .profile-pic { 
            border-radius: 50%; width: 80px; height: 80px; object-fit: cover; 
            border: 2px solid var(--tg-theme-button-color, #3390ec); margin-bottom: 10px;
        }
        .user-name { font-size: 20px; font-weight: 600; margin-bottom: 25px; }

        .plan-btn, .action-btn {
            display: block; width: 100%; padding: 16px; margin: 10px 0;
            background-color: var(--tg-theme-button-color, #3390ec);
            color: var(--tg-theme-button-text-color, #ffffff);
            border: none; border-radius: 12px; font-size: 16px; font-weight: bold; cursor: pointer;
            transition: opacity 0.2s, transform 0.1s;
        }
        .plan-btn:active, .action-btn:active { transform: scale(0.98); opacity: 0.8; }
        .action-btn { background-color: #34c759; } 
        .action-btn:disabled { background-color: #555; cursor: not-allowed; }
        
        #payment-section, #slip-section { display: none; margin-top: 15px; }
        .qr-img { width: 220px; max-width: 100%; border-radius: 12px; margin: 15px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .instruction-text { font-size: 15px; opacity: 0.85; margin: 5px 0 15px 0; }

        .copy-box {
            background-color: var(--tg-theme-secondary-bg-color, #2c2c2e);
            border: 1px solid rgba(255,255,255,0.1); border-radius: 10px;
            padding: 14px; margin: 15px 0; display: flex; align-items: center;
            justify-content: space-between; cursor: pointer; word-break: break-all;
        }
        .copy-text { font-family: monospace; font-size: 14px; text-align: left; flex: 1; margin-right: 10px; color: var(--tg-theme-text-color, #fff); }
        .copy-icon { width: 20px; height: 20px; fill: var(--tg-theme-button-color, #3390ec); flex-shrink: 0; }
        
        .file-upload-wrapper { margin: 20px 0; }
        input[type="file"] {
            background: var(--tg-theme-secondary-bg-color, #2c2c2e);
            padding: 12px; border-radius: 8px; width: 90%; color: var(--tg-theme-text-color, #fff);
        }
    </style>
</head>
<body>

    <div id="block-screen">
        <h2>Access Denied 🛑</h2>
        <p>Please open this inside the Telegram App.</p>
    </div>

    <div id="app-content">
        <img id="user-pic" class="profile-pic" alt="Profile">
        <div id="user-name" class="user-name">Loading...</div>

        <!-- Step 1: Plans Configuration Layout -->
        <div id="plans-section">
            <h3>Select a Premium Plan</h3>
            <div id="buttons-container"></div>
        </div>

        <!-- Step 2: Payment Details Layout -->
        <div id="payment-section">
            <h3>Complete Your Payment</h3>
            <p class="instruction-text">Selected: <strong id="selected-plan-text"></strong></p>
            
            <img src="{{QR_IMG}}" alt="Payment QR" class="qr-img">
            
            <p class="instruction-text">Scan the QR code or tap below to copy the <strong>{{PAYM_TYPE}}</strong> credentials:</p>
            
            <div class="copy-box" onclick="copyAddress()">
                <div class="copy-text" id="pay-address">{{PAYM_ID}}</div>
                <svg class="copy-icon" viewBox="0 0 24 24">
                    <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
                </svg>
            </div>
            
            <button class="action-btn" onclick="goToSlipSection()">I Have Paid, Next Step</button>
            <button class="plan-btn" style="background-color: transparent; border: 1px solid gray;" onclick="goBackToPlans()">Cancel</button>
        </div>

        <!-- Step 3: Transaction Upload Layout -->
        <div id="slip-section">
            <h3>Upload Payment Slip</h3>
            <p class="instruction-text">Please provide a confirmation screenshot of your transfer.</p>
            <div class="file-upload-wrapper">
                <input type="file" id="slip-file" accept="image/png, image/jpeg, image/webp">
            </div>
            <button id="submit-btn" class="action-btn" onclick="submitPayment()">Submit for Verification</button>
        </div>
    </div>

    <script>
        // ── Fallback avatar: inline SVG, no external request needed ──────────
        const FALLBACK_AVATAR = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80' viewBox='0 0 80 80'%3E%3Crect width='80' height='80' rx='40' fill='%233390ec'/%3E%3Ccircle cx='40' cy='30' r='16' fill='%23fff'/%3E%3Cellipse cx='40' cy='70' rx='26' ry='20' fill='%23fff'/%3E%3C/svg%3E";

        const tg = window.Telegram.WebApp;
        tg.expand(); 

        if (!tg.initData) {
            document.getElementById('block-screen').style.display = 'block';
        } else {
            document.getElementById('app-content').style.display = 'block';
        }

        let currentPlanDays = "0"; 
        let tgUserId = "unknown";
        let tgUserName = "User";

        const userPicEl = document.getElementById('user-pic');

        const user = tg.initDataUnsafe?.user;
        if (user) {
            tgUserId   = user.id;
            tgUserName = user.first_name + (user.last_name ? ' ' + user.last_name : '');
            document.getElementById('user-name').innerText = tgUserName;

            if (user.photo_url) {
                // Try loading the real photo; fall back to SVG if it fails
                userPicEl.src = user.photo_url;
                userPicEl.onerror = () => { userPicEl.src = FALLBACK_AVATAR; };
            } else {
                userPicEl.src = FALLBACK_AVATAR;
            }
        } else {
            userPicEl.src = FALLBACK_AVATAR;
        }

        const plans = {{PLANS_JSON}};
        const container = document.getElementById('buttons-container');

        for (const [daysStr, details] of Object.entries(plans)) {
            const planName = details[0];
            const currency = details[1];
            const price    = details[2];
            
            const btn = document.createElement('button');
            btn.className = 'plan-btn';
            btn.innerText = `${planName.toUpperCase()} - ${currency} ${price}`;
            
            btn.onclick = () => {
                currentPlanDays = daysStr; 
                document.getElementById('plans-section').style.display  = 'none';
                document.getElementById('payment-section').style.display = 'block';
                document.getElementById('selected-plan-text').innerText  = `${planName} (${currency} ${price})`;
            };
            container.appendChild(btn);
        }

        function copyAddress() {
            const address = document.getElementById('pay-address').innerText;
            navigator.clipboard.writeText(address).then(() => {
                tg.showAlert("✅ Copied to clipboard!");
            }).catch(err => {
                console.error("Failed to copy", err);
            });
        }

        function goToSlipSection() {
            document.getElementById('payment-section').style.display = 'none';
            document.getElementById('slip-section').style.display    = 'block';
        }
        
        function goBackToPlans() {
            document.getElementById('payment-section').style.display = 'none';
            document.getElementById('plans-section').style.display   = 'block';
        }

        async function submitPayment() {
            const fileInput = document.getElementById('slip-file');
            if (!fileInput.files.length) {
                tg.showAlert("⚠️ Please upload a screenshot of your payment.");
                return;
            }

            const file = fileInput.files[0];
            if (file.size > 5 * 1024 * 1024) {
                tg.showAlert("⚠️ File is too large. Please upload an image under 5MB.");
                return;
            }

            const submitBtn = document.getElementById('submit-btn');
            submitBtn.innerText  = "⏳ Uploading... Please wait";
            submitBtn.disabled   = true;

            const formData = new FormData();
            formData.append("days",      currentPlanDays); 
            formData.append("user_id",   tgUserId);
            formData.append("user_name", tgUserName);
            formData.append("slip",      file);

            try {
                const response = await fetch("/submit-payment", {
                    method: "POST",
                    body: formData
                });

                const result = await response.json();

                if (response.ok && result.status === "success") {
                    tg.showAlert("✅ Slip uploaded successfully! Your plan will be activated after verification.", () => {
                        tg.close();
                    });
                } else {
                    tg.showAlert("❌ " + (result.message || "Error uploading slip. Please try again."));
                    resetButton();
                }
            } catch (error) {
                tg.showAlert("🔌 Network error. Please check your connection and try again.");
                resetButton();
            }
            
            function resetButton() {
                submitBtn.innerText = "Submit for Verification";
                submitBtn.disabled  = false;
            }
        }
    </script>
</body>
</html>
"""


# ─────────────────────────────────────────────────────────────────────────────
# Backend helpers
# ─────────────────────────────────────────────────────────────────────────────
async def media_watch(message_id):
    media_msg = await temp.BOT.get_messages(BIN_CHANNEL, message_id)
    media = getattr(media_msg, media_msg.media.value, None)
    src = urllib.parse.urljoin(URL, f'download/{message_id}')
    tag = media.mime_type.split('/')[0].strip()
    if tag == 'video':
        heading = html.escape(f'Watch — {media.file_name}')
        html_ = (watch_tmplt
                 .replace('{heading}',   heading)
                 .replace('{file_name}', media.file_name)
                 .replace('{src}',       src))
    else:
        html_ = error_tmplt
    return html_
