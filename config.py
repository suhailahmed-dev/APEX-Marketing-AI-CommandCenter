import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8800"))
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini-3.5-flash-lite")
FALLBACK_MODELS = ["gemini-3-flash-preview", "gemini-3.8-flash"]
DB_PATH = BASE_DIR / "marketing_hub.db"

# Language options helper
LANGUAGE_FIELD = {
    "name": "language",
    "label": "Output Language / Style",
    "type": "select",
    "options": [
        "English (Global Professional)",
        "Roman Urdu (Relatable & Conversational)",
        "Urdu (اردو Script)",
        "Bilingual (English Hook + Roman Urdu Body)"
    ],
    "default": "English (Global Professional)"
}

# The 15 Core Marketing Modules with input specifications
MARKETING_MODULES = {
    "social_content": {
        "id": "social_content",
        "name": "Social Media Content",
        "icon": "fa-brands fa-hashtag",
        "category": "Social & Creative",
        "badge": "Viral",
        "description": "Facebook, Instagram & LinkedIn captions, hook variations, and trending hashtags.",
        "fields": [
            {"name": "topic", "label": "Topic / Theme", "type": "text", "placeholder": "e.g., 5 Summer Fashion Mistakes to Avoid, or New Product Launch", "required": True},
            {"name": "platform", "label": "Primary Platform", "type": "select", "options": ["All Platforms (FB, IG, LinkedIn, X)", "Instagram (Visual + Hashtags)", "Facebook (Engagement + Discussion)", "LinkedIn (Professional / B2B)", "Twitter/X (Punchy Thread)"], "default": "All Platforms (FB, IG, LinkedIn, X)"},
            {"name": "goal", "label": "Primary Goal", "type": "select", "options": ["Engagement / Comments", "Drive Website Clicks / Sales", "Brand Authority / Education", "Viral Shareability"], "default": "Engagement / Comments"},
            {"name": "tone", "label": "Brand Tone", "type": "select", "options": ["Energetic & Friendly", "Authoritative & Professional", "Humorous & Witty", "Direct & Urgency-driven", "Inspiring & Story-driven"], "default": "Energetic & Friendly"},
            LANGUAGE_FIELD
        ]
    },
    "content_calendar": {
        "id": "content_calendar",
        "name": "Content Calendar",
        "icon": "fa-regular fa-calendar-days",
        "category": "Social & Creative",
        "badge": "Planner",
        "description": "Generate complete 7, 15, or 30-day multi-channel content roadmaps with hooks, formats & CTAs.",
        "fields": [
            {"name": "duration", "label": "Calendar Duration", "type": "select", "options": ["7 Days Sprint", "15 Days Growth Plan", "30 Days Complete Blueprint"], "default": "15 Days Growth Plan"},
            {"name": "focus_area", "label": "Key Focus / Campaign Goal", "type": "text", "placeholder": "e.g., E-commerce Season Sale, SaaS free trials, Local brand awareness", "required": True},
            {"name": "posting_frequency", "label": "Posting Cadence", "type": "select", "options": ["1 Post Per Day", "2 Posts Per Day (Reel + Static)", "3 Posts Per Week"], "default": "1 Post Per Day"},
            LANGUAGE_FIELD
        ]
    },
    "post_ideas": {
        "id": "post_ideas",
        "name": "Post & Reel Ideas",
        "icon": "fa-solid fa-lightbulb",
        "category": "Social & Creative",
        "badge": "Ideation",
        "description": "High-converting ideas for Reels, TikToks, Carousels, Polls, and Story series for your business.",
        "fields": [
            {"name": "business_type", "label": "Business Niche / Industry", "type": "text", "placeholder": "e.g., Fitness Coach, Luxury Perfume Brand, Digital Marketing Agency", "required": True},
            {"name": "target_audience", "label": "Target Audience", "type": "text", "placeholder": "e.g., Busy working professionals, Gen Z fashion shoppers, Local homeowners"},
            {"name": "content_format", "label": "Preferred Format", "type": "select", "options": ["Mix of Everything (Reels, Carousels, Stories)", "Viral Short-Form Reels / TikToks", "Educational Carousel Slides", "Behind-the-Scenes & Trust Builders"], "default": "Mix of Everything (Reels, Carousels, Stories)"},
            LANGUAGE_FIELD
        ]
    },
    "content_writing": {
        "id": "content_writing",
        "name": "Copywriting Engine",
        "icon": "fa-solid fa-pen-nib",
        "category": "Copy & Conversion",
        "badge": "High-Converting",
        "description": "Sales letters, landing page copy, video scripts, elevator pitches, and brand storytelling.",
        "fields": [
            {"name": "copy_type", "label": "Copywriting Format", "type": "select", "options": ["Landing Page Hero & Benefits", "Video Sales Letter (VSL) Script", "AIDA Framework Sales Copy", "PAS Framework Problem-Agitate-Solve", "Brand Story / About Us Page"], "default": "Landing Page Hero & Benefits"},
            {"name": "product_service", "label": "Product or Service Name", "type": "text", "placeholder": "e.g., APEX AI Marketing Suite, Organic Herbal Hair Oil", "required": True},
            {"name": "key_benefits", "label": "Core Benefits / UVP", "type": "textarea", "placeholder": "What makes this irresistible? Results achieved, time saved, problems solved..."},
            LANGUAGE_FIELD
        ]
    },
    "seo_optimizer": {
        "id": "seo_optimizer",
        "name": "SEO On-Page Architect",
        "icon": "fa-solid fa-magnifying-glass-chart",
        "category": "SEO & Traffic",
        "badge": "Rank #1",
        "description": "Search intent analysis, click-magnet Title tags, Meta descriptions, H1/H2 hierarchies, and FAQ schema.",
        "fields": [
            {"name": "target_topic", "label": "Target Topic / Page Subject", "type": "text", "placeholder": "e.g., Best CRM software for small businesses 2026", "required": True},
            {"name": "primary_keyword", "label": "Primary Keyword", "type": "text", "placeholder": "e.g., best small business crm"},
            {"name": "secondary_keywords", "label": "Secondary / LSI Keywords", "type": "text", "placeholder": "e.g., affordable crm, cloud crm tools, lead management software"}
        ]
    },
    "keyword_research": {
        "id": "keyword_research",
        "name": "Keyword Research & Clusters",
        "icon": "fa-solid fa-chart-pie",
        "category": "SEO & Traffic",
        "badge": "Topical Authority",
        "description": "Transform seed keywords into organized topical clusters, search intent tiers (Informational, Transactional).",
        "fields": [
            {"name": "seed_keyword", "label": "Seed Keyword / Niche", "type": "text", "placeholder": "e.g., Digital marketing course, Dropshipping, Men's grooming", "required": True},
            {"name": "market_region", "label": "Target Geography", "type": "select", "options": ["Global (English)", "USA / North America", "UK / Europe", "South Asia (Pakistan/India)", "Middle East / UAE"], "default": "Global (English)"}
        ]
    },
    "blog_generation": {
        "id": "blog_generation",
        "name": "SEO Blog Generator",
        "icon": "fa-solid fa-newspaper",
        "category": "SEO & Traffic",
        "badge": "Full Draft",
        "description": "Comprehensive, human-like, SEO-optimized articles with structured H2/H3s, key takeaways, and FAQs.",
        "fields": [
            {"name": "blog_title_or_keyword", "label": "Article Title or Focus Keyword", "type": "text", "placeholder": "e.g., Complete Guide to Dropshipping on eBay in 2026", "required": True},
            {"name": "word_count_tier", "label": "Target Length", "type": "select", "options": ["Comprehensive Guide (~1,500 - 2,000 words)", "Standard In-Depth Post (~1,000 - 1,200 words)", "Quick Quick-Hit Listicle (~700 - 900 words)"], "default": "Comprehensive Guide (~1,500 - 2,000 words)"},
            {"name": "tone", "label": "Writing Style", "type": "select", "options": ["Practical & Actionable Expert", "Conversational & Engaging", "Deep Technical / Academic", "Storyteller / Case Study Style"], "default": "Practical & Actionable Expert"}
        ]
    },
    "ad_studio": {
        "id": "ad_studio",
        "name": "High-ROAS Ad Studio",
        "icon": "fa-solid fa-bullseye",
        "category": "Advertising & Sales",
        "badge": "Meta & Google",
        "description": "Generate high-converting Facebook/Instagram ad copies, thumb-stopping headlines, hooks, and targeting angles.",
        "fields": [
            {"name": "offer_details", "label": "Offer / Promotion", "type": "text", "placeholder": "e.g., 50% Off First Month Subscription, Free Consultation, Buy 1 Get 1 Free", "required": True},
            {"name": "platform", "label": "Ad Platform", "type": "select", "options": ["Facebook & Instagram Feed/Reels", "Google Search Ads (Headlines + Descriptions)", "TikTok Spark Ads (Script + Hook)", "LinkedIn Sponsored InMail / Feed"], "default": "Facebook & Instagram Feed/Reels"},
            {"name": "pain_point", "label": "Audience Pain Point to Agitate", "type": "text", "placeholder": "e.g., Wasting money on ads that don't convert; Tired of low energy and poor results"},
            LANGUAGE_FIELD
        ]
    },
    "seo_report": {
        "id": "seo_report",
        "name": "SEO Audit & Health Report",
        "icon": "fa-solid fa-chart-line",
        "category": "SEO & Traffic",
        "badge": "Diagnostic",
        "description": "Input website stats, rankings, or crawl issues to generate an executive SEO audit report with step-by-step action plan.",
        "fields": [
            {"name": "website_url", "label": "Website URL / Brand", "type": "text", "placeholder": "e.g., https://mybrandstore.com", "required": True},
            {"name": "observed_problems", "label": "Known Issues / Analytics Summary", "type": "textarea", "placeholder": "e.g., Traffic dropped 20% last month, slow mobile page speed, low ranking for primary keyword, high bounce rate on checkout"}
        ]
    },
    "client_communication": {
        "id": "client_communication",
        "name": "Client Communications & Pitch",
        "icon": "fa-solid fa-comments",
        "category": "Agency & Client Ops",
        "badge": "Professional",
        "description": "Proposals, monthly client updates, scope of work, handling tricky objections, and WhatsApp follow-ups.",
        "fields": [
            {"name": "comm_type", "label": "Communication Objective", "type": "select", "options": ["WhatsApp Client / Lead Follow-up (High-Converting Closing)", "Monthly Performance & Wins Update", "New Client Proposal / Pitch Summary", "Scope Creep / Boundary Setting Message", "Project Milestone Delivery Handover", "Polite Payment / Invoice Follow-up"], "default": "WhatsApp Client / Lead Follow-up (High-Converting Closing)"},
            {"name": "client_name", "label": "Client / Prospect Name", "type": "text", "placeholder": "e.g., Apex Atelier / Mr. Bilal / New Customer"},
            {"name": "key_highlights", "label": "Key Details / Offer / Context", "type": "textarea", "placeholder": "e.g., Client inquired about pricing, wants to know timeline, offered 15% discount if finalized this week"},
            LANGUAGE_FIELD
        ]
    },
    "email_marketing": {
        "id": "email_marketing",
        "name": "Email Marketing Sequences",
        "icon": "fa-solid fa-envelope-open-text",
        "category": "Advertising & Sales",
        "badge": "High Open-Rate",
        "description": "Nurture sequences, flash sale blasts, weekly newsletter editions, and abandoned cart recovery emails.",
        "fields": [
            {"name": "email_type", "label": "Email Objective", "type": "select", "options": ["Promotional Flash Sale / Offer Announcement", "Welcome & Onboarding Sequence (3-Part)", "Value-Packed Weekly Newsletter", "Abandoned Cart / Re-engagement", "Cold Outreach B2B Pitch"], "default": "Promotional Flash Sale / Offer Announcement"},
            {"name": "subject_focus", "label": "Core Offer / Topic", "type": "text", "placeholder": "e.g., Flash 48-Hour Weekend VIP Sale, or 3 Secrets to 10x ROI", "required": True},
            {"name": "call_to_action", "label": "Primary Call to Action (CTA)", "type": "text", "placeholder": "e.g., Claim Your 40% Discount, Book a 15-min Call"},
            LANGUAGE_FIELD
        ]
    },
    "product_content": {
        "id": "product_content",
        "name": "E-Commerce Product Content",
        "icon": "fa-solid fa-bag-shopping",
        "category": "Copy & Conversion",
        "badge": "E-Commerce",
        "description": "Catchy e-commerce titles, bulleted benefits (Amazon/Shopify style), FAQ accordion copy, and social sales angles.",
        "fields": [
            {"name": "product_name", "label": "Product Name", "type": "text", "placeholder": "e.g., Lumina Pro Ergonomic Office Chair", "required": True},
            {"name": "product_features", "label": "Raw Features / Specs", "type": "textarea", "placeholder": "e.g., Memory foam cushion, 3D adjustable armrests, breathable mesh, 300 lbs capacity, 5-year warranty"},
            {"name": "platform", "label": "Target Store Platform", "type": "select", "options": ["Shopify Store", "Amazon Product Listing", "Etsy / Handmade", "TikTok Shop Listing"], "default": "Shopify Store"},
            LANGUAGE_FIELD
        ]
    },
    "marketing_strategy": {
        "id": "marketing_strategy",
        "name": "360° Marketing Strategy Blueprint",
        "icon": "fa-solid fa-chess-knight",
        "category": "Strategy & Reports",
        "badge": "Executive",
        "description": "End-to-end GTM marketing strategy including ideal customer profiles (ICP), funnel architecture, and channel allocation.",
        "fields": [
            {"name": "business_model", "label": "Business Model & Offering", "type": "text", "placeholder": "e.g., B2B SaaS for HR managers, Local aesthetic clinic, D2C streetwear brand", "required": True},
            {"name": "current_stage", "label": "Business Stage", "type": "select", "options": ["Launch / Brand New ($0 - $5k/mo)", "Scaling Fast ($5k - $50k/mo)", "Established Leader Looking to Expand"], "default": "Scaling Fast ($5k - $50k/mo)"},
            {"name": "monthly_budget", "label": "Rough Monthly Ad/Marketing Budget", "type": "text", "placeholder": "e.g., $1,000 - $3,000 / month, or Organic-first low budget"}
        ]
    },
    "competitor_analysis": {
        "id": "competitor_analysis",
        "name": "Competitor Intelligence & Gaps",
        "icon": "fa-solid fa-brain",
        "category": "Strategy & Reports",
        "badge": "Strategic",
        "description": "Teardown of competitor strengths, weaknesses, messaging angles, and unexplored content gaps you can dominate.",
        "fields": [
            {"name": "my_brand", "label": "Your Brand & Offer", "type": "text", "placeholder": "e.g., Nova Skin - Clean botanical skincare with transparent ingredients", "required": True},
            {"name": "competitors", "label": "Competitor Brands / URLs", "type": "textarea", "placeholder": "e.g., Competitor A, Competitor B - their pricing is high and customer support is slow", "required": True}
        ]
    },
    "executive_reports": {
        "id": "executive_reports",
        "name": "Executive Marketing Report",
        "icon": "fa-solid fa-file-invoice",
        "category": "Strategy & Reports",
        "badge": "Client-Ready",
        "description": "Automated professional Weekly or Monthly Marketing Review formatted with KPIs, milestones, and ROI for owners/stakeholders.",
        "fields": [
            {"name": "report_period", "label": "Reporting Window", "type": "select", "options": ["Monthly Marketing Review (Comprehensive)", "Weekly Sprint Summary", "Quarterly Executive Retrospective"], "default": "Monthly Marketing Review (Comprehensive)"},
            {"name": "metrics_summary", "label": "Raw Metrics & Achievements", "type": "textarea", "placeholder": "e.g., Ad Spend: $3,200, Revenue: $11,800, Leads: 142, Top Post: Reel on Tips reached 48k views, 4 blog posts published.", "required": True},
            {"name": "next_month_goals", "label": "Next Period Priorities", "type": "text", "placeholder": "e.g., Scale TikTok ads, launch email welcome sequence, improve mobile checkout conversion"}
        ]
    }
}
