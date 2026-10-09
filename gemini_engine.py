import os
import json
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, DEFAULT_MODEL, FALLBACK_MODELS, MARKETING_MODULES
from database import get_active_brand

def get_gemini_client():
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured in .env file.")
    return genai.Client(api_key=GEMINI_API_KEY)

MASTER_SYSTEM_INSTRUCTION = """
You are APEX MARKETING AI, the world's most elite autonomous Chief Marketing Officer (CMO), veteran copywriter, and growth marketing strategist.
You work directly for business owners, agency founders, and growth teams.

YOUR PHILOSOPHY:
1. Every piece of content, copy, strategy, or report must be PRODUCTION-READY, HIGH-CONVERTING, and IMMEDIATELY DEPLOYABLE.
2. Avoid generic, lazy advice. Provide specific hooks, numbers, psychological triggers, and actionable steps.
3. Format with clean, beautiful Markdown: use bolding, bullet points, markdown tables, callout blocks, and emojis where appropriate.
4. Incorporate the user's specific brand profile (Tone, Industry, Target Audience, USP) into every deliverable seamlessly.
5. LANGUAGE & LOCALIZATION RULES:
   - If the user selects "Roman Urdu", write natural, punchy, conversational Roman Urdu (Pakistani/South Asian conversational style, e.g., 'Agar aap bhi...', 'Yeh 3 galtiyan jo 90% log karte hain...', 'Aaj hi order karein'). Do NOT make it sound robotic. Keep technical marketing terms in English (e.g., ROI, CTA, Website, Reel).
   - If the user selects "Urdu (اردو Script)", write professional, eloquent Urdu script.
   - If the user selects "Bilingual", use punchy English hooks with Roman Urdu explanations and strong CTAs.
   - If the user selects "English", use world-class direct-response American/Global English copywriting.
"""

def generate_marketing_asset(module_id: str, input_params: dict) -> str:
    """
    Executes the specialized marketing agent for the requested module using Google Gemini.
    """
    client = get_gemini_client()
    brand = get_active_brand()

    module_info = MARKETING_MODULES.get(module_id, {})
    module_name = module_info.get("name", module_id)
    language_choice = input_params.get("language", "English (Global Professional)")

    brand_context = f"""
### BRAND PROFILE & CONTEXT:
- **Brand / Business Name**: {brand.get('brand_name', 'Our Brand')}
- **Industry / Niche**: {brand.get('industry', 'Business')}
- **Target Audience / ICP**: {brand.get('target_audience', 'Prospective buyers')}
- **Brand Tone**: {brand.get('tone', 'Authoritative, friendly, high-converting')}
- **Unique Selling Proposition (USP)**: {brand.get('usp', 'High quality and results')}
- **Website**: {brand.get('website', '')}
- **Selected Output Language**: {language_choice}
"""

    prompt = build_module_prompt(module_id, input_params, brand_context)

    models_to_try = [DEFAULT_MODEL] + [m for m in FALLBACK_MODELS if m != DEFAULT_MODEL]
    last_error = None

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=MASTER_SYSTEM_INSTRUCTION,
                    temperature=0.7,
                )
            )
            if response and response.text:
                return response.text
        except Exception as e:
            last_error = e
            continue

    return f"### ⚠️ Generation Error\n\nCould not generate content: {str(last_error)}\n\nPlease ensure your `GEMINI_API_KEY` is valid and active."

def build_module_prompt(module_id: str, inputs: dict, brand_context: str) -> str:
    """Constructs deep, high-converting prompts for each of the 15 modules."""
    lang_instruction = f"\n**IMPORTANT INSTRUCTION:** Write all output in: **{inputs.get('language', 'English')}**.\n"
    
    if module_id == "social_content":
        return f"""
{brand_context}
{lang_instruction}
### TASK: Elite Social Media Content Generation
- **Topic / Focus**: {inputs.get('topic', 'Brand awareness')}
- **Target Platform**: {inputs.get('platform', 'Instagram & Facebook')}
- **Primary Goal**: {inputs.get('goal', 'Engagement')}
- **Tone**: {inputs.get('tone', 'Energetic & Friendly')}

Deliver a complete social media pack including:
1. **5 Viral Hook Variations** (Curiosity, Negative Bias, Data-driven, Story, Contrarian)
2. **2 Full Post Captions**:
   - Caption Option A: Long-form storytelling with line breaks and clear CTA.
   - Caption Option B: Punchy, high-impact bulleted format with high CTA urgency.
3. **Carousel / Visual Creative Direction**: Slide-by-slide outline (5-7 slides) or Reel video prompt idea.
4. **Hashtag Matrix**: 15 targeted hashtags grouped into: High-Volume (5), Niche-Specific (5), and Brand/Intent-focused (5).
"""

    elif module_id == "content_calendar":
        return f"""
{brand_context}
{lang_instruction}
### TASK: High-ROI Content Calendar Blueprint
- **Duration**: {inputs.get('duration', '15 Days')}
- **Focus Area / Campaign**: {inputs.get('focus_area', 'Brand growth')}
- **Cadence**: {inputs.get('posting_frequency', '1 Post Per Day')}

Generate a day-by-day, highly structured Content Calendar formatted as a comprehensive Markdown Table:
Columns: `| Day | Platform | Content Pillar / Angle | Hook / Headline | Format (Reel/Carousel/Post) | CTA |`

Followed by:
- **Campaign Milestone Strategy**: Key objectives for Week 1, Week 2 (and onwards).
- **Repurposing Playbook**: How 1 main piece of content converts into 3 secondary assets.
"""

    elif module_id == "post_ideas":
        return f"""
{brand_context}
{lang_instruction}
### TASK: High-Converting Post & Reel Ideation Lab
- **Business Niche**: {inputs.get('business_type', 'General Business')}
- **Audience**: {inputs.get('target_audience', 'Prospects')}
- **Preferred Format**: {inputs.get('content_format', 'Mix')}

Generate 10 fresh, viral, non-cliché content ideas tailored specifically to this business:
For each idea, specify:
1. **Content Angle & Hook**: Exact first 3 seconds verbal or visual hook.
2. **Core Concept / Storyline**: What happens in the post/reel/carousel.
3. **Psychological Trigger**: (FOMO, Social Proof, Counter-intuitive revelation, Relatability).
4. **Target CTA**: (Comment word 'GUIDE', Save this post, DM for link, Visit bio).
"""

    elif module_id == "content_writing":
        return f"""
{brand_context}
{lang_instruction}
### TASK: High-Converting Copywriting & Sales Engine
- **Copy Format**: {inputs.get('copy_type', 'Landing Page Hero & Benefits')}
- **Product / Service**: {inputs.get('product_service', 'Our Product')}
- **Key Benefits / UVP**: {inputs.get('key_benefits', 'Saves time, increases revenue')}

Write full, psychology-grounded sales copy using proven direct-response copywriting principles:
- Compelling, thumb-stopping Headline & Sub-headline.
- Agitate the reader's painful reality, then present the breakthrough solution.
- Irresistible Bullet Points formatted with `Benefit -> Emotional Outcome`.
- Risk-reversal & Guarantee statement.
- Uncompromising Call-to-Action (CTA) buttons and urgency driver.
"""

    elif module_id == "seo_optimizer":
        return f"""
{brand_context}
### TASK: On-Page SEO Architecture & Search Intent Optimization
- **Target Topic**: {inputs.get('target_topic', 'SEO guide')}
- **Primary Keyword**: {inputs.get('primary_keyword', 'targeted keyword')}
- **Secondary / LSI Keywords**: {inputs.get('secondary_keywords', 'related keywords')}

Generate a comprehensive on-page SEO blueprint:
1. **Search Intent Teardown**: (Informational / Commercial / Transactional) and why users search this.
2. **3 High-CTR Title Tags** (Under 60 chars, power words + primary keyword).
3. **2 Click-Magnet Meta Descriptions** (Under 155 chars with embedded CTA).
4. **Optimal Heading Hierarchy**: Exact H1, H2, and H3 layout for Google ranking.
5. **Topical Entities & FAQ Section**: 4 high-value questions with concise, schema-ready answers.
"""

    elif module_id == "keyword_research":
        return f"""
{brand_context}
### TASK: Comprehensive Keyword Research & Topical Clusters
- **Seed Keyword / Niche**: {inputs.get('seed_keyword', 'Seed')}
- **Target Geography**: {inputs.get('market_region', 'Global')}

Produce an extensive Keyword Strategy categorized into 4 Topical Clusters:
1. **Topical Cluster Breakdown** (Pillar topic + 4 supporting clusters).
2. **Keyword Opportunity Table** with columns:
   `| Keyword | Search Intent | Funnel Stage (TOFU/MOFU/BOFU) | Est. Competition | Priority |`
3. **Content Silo Architecture**: How to interlink these articles for topical authority.
4. **Zero-Click & "People Also Ask" Opportunities**: 5 high-converting conversational questions.
"""

    elif module_id == "blog_generation":
        return f"""
{brand_context}
### TASK: Publish-Ready, Human-Like SEO Blog Article
- **Article Title / Focus Keyword**: {inputs.get('blog_title_or_keyword', 'Complete Guide')}
- **Target Length**: {inputs.get('word_count_tier', 'Comprehensive Guide')}
- **Writing Tone**: {inputs.get('tone', 'Practical & Actionable Expert')}

Write a complete, deeply engaging, authoritative article that sounds written by a top human industry practitioner:
- **Title**: Engaging, search-optimized.
- **Hook & Executive Summary**: Grab attention in the first 2 paragraphs.
- **Deep Content Sections**: Well-structured H2 and H3 subheadings with real-world examples, step-by-step methodologies, and actionable frameworks.
- **Key Takeaways Callout Box**.
- **FAQ Section**: 3 crucial questions answered cleanly.
- **Concluding Call to Action**: Seamlessly bridge into the brand's services/products.
"""

    elif module_id == "ad_studio":
        return f"""
{brand_context}
{lang_instruction}
### TASK: High-ROAS Paid Advertising Studio (Meta / Google / TikTok)
- **Offer / Promotion**: {inputs.get('offer_details', 'Special offer')}
- **Ad Platform**: {inputs.get('platform', 'Facebook & Instagram Feed/Reels')}
- **Audience Pain Point**: {inputs.get('pain_point', 'Frustrated with current options')}

Deliver a complete paid ad campaign package:
1. **Audience Targeting Recommendations**:
   - Demographics, Detailed Interests, Behaviors, and Exclusions.
2. **3 Distinct Ad Copy Angles**:
   - Angle 1 (Direct Problem / Agitation / Solution)
   - Angle 2 (Curiosity / Story / Case Study)
   - Angle 3 (Short & Punchy Offer-Led)
3. **Headlines**: 5 high-CTR headline options (under 40 chars).
4. **Visual Creative Brief**: Exact instructions for image or video creative (what to show, text overlay, thumbnail idea).
"""

    elif module_id == "seo_report":
        return f"""
{brand_context}
### TASK: Professional SEO Audit & Actionable Health Report
- **Website URL**: {inputs.get('website_url', 'Website')}
- **Observed Problems / Metrics**: {inputs.get('observed_problems', 'Traffic drop')}

Generate an Executive SEO Audit & Roadmap:
1. **Executive Summary**: Core health diagnosis and business impact.
2. **Critical Findings Matrix**: Categorized into Technical SEO, On-Page SEO, Content Quality, and Backlink/Authority.
3. **Priority Action Matrix**:
   `| Issue | Severity (High/Med/Low) | Effort to Fix | Expected Impact | Recommended Solution |`
4. **90-Day Organic Recovery Roadmap**: Month 1 (Fix foundation), Month 2 (Topical authority), Month 3 (Scale).
"""

    elif module_id == "client_communication":
        comm_type = inputs.get('comm_type', '')
        if "WhatsApp" in comm_type or "Inquiry" in comm_type or "Closing" in comm_type:
            return f"""
{brand_context}
{lang_instruction}
### TASK: High-Converting WhatsApp Client / Lead Inquiry & Deal Closing Sequence
- **Client / Prospect Name**: {inputs.get('client_name', 'Client')}
- **Context / Key Details / Offer**: {inputs.get('key_highlights', 'Inquired about service details and pricing')}

Draft a multi-part high-conversion WhatsApp communication sequence tailored for direct closing:
1. **Instant Response Template (Warm & Welcoming)**: Polite greeting, acknowledging their interest, and establishing instant credibility.
2. **Value & Differentiator Breakdown**: Bulleted points highlighting why our solution is superior, results achieved, and clear proof.
3. **Pricing & Incentive Presentation**: Professional way to present pricing/discount without sounding cheap or desperate.
4. **Top 3 Objection Busters**: Exact replies for:
   - "Price thori zyada hai" / "Budget tight hai"
   - "Main baad mein soch kar bataoonga"
   - "Kya guarantee hai ke results aayenge?"
5. **Frictionless Call to Action (CTA)**: Low-friction next step (e.g. 10-min free audit, demo preview, or quick call).
6. **24-Hour Polite Follow-up Reminder**: Gentle 2-sentence follow-up message.
"""
        return f"""
{brand_context}
{lang_instruction}
### TASK: High-Stakes Client Communications & Proposals
- **Objective**: {inputs.get('comm_type', 'Monthly Performance Update')}
- **Client / Recipient**: {inputs.get('client_name', 'Client')}
- **Key Data / Highlights**: {inputs.get('key_highlights', 'Strong performance metrics')}

Draft polished, executive-ready communication:
1. **Email / Message Draft**: Clear, courteous, assertive, highlighting wins, ownership, and clarity.
2. **Executive Highlights Callout**: Bulleted summary of achievements and metrics.
3. **Next Steps & Deadlines**: Clear alignment on deliverables.
4. **Optional Short WhatsApp / Slack Brief**: A 3-sentence casual summary for instant messaging.
"""

    elif module_id == "email_marketing":
        return f"""
{brand_context}
{lang_instruction}
### TASK: High-Open-Rate Email Marketing Sequences
- **Email Objective**: {inputs.get('email_type', 'Promotional Flash Sale')}
- **Subject Focus**: {inputs.get('subject_focus', 'Exclusive Offer')}
- **Call to Action (CTA)**: {inputs.get('call_to_action', 'Shop Now')}

Deliver complete email copies ready to paste into Klaviyo, Mailchimp, or ActiveCampaign:
1. **5 High-Open Subject Lines** + Preview Text (Curiosity, Urgency, Benefit, Mystery).
2. **Full Email Body Copy**:
   - Engaging opening hook.
   - Core value proposition / story.
   - Benefit bullets.
   - Frictionless, clear CTA button placement.
   - P.S. line (high conversion secret).
"""

    elif module_id == "product_content":
        return f"""
{brand_context}
{lang_instruction}
### TASK: High-Converting E-Commerce Product Content
- **Product Name**: {inputs.get('product_name', 'Product')}
- **Raw Features / Specs**: {inputs.get('product_features', 'Features')}
- **Platform**: {inputs.get('platform', 'Shopify')}

Generate a multi-faceted product copywriting kit:
1. **SEO-Optimized Product Title**: High conversion & search visibility.
2. **Punchy Tagline / Hook**: One-sentence hook.
3. **Product Story / Description**: Sensory, benefit-led description.
4. **5 Amazon/Shopify Feature-to-Benefit Bullets** (Format: **[FEATURE IN BOLD]** - Why the buyer cares).
5. **3 Objection-Busting FAQs**: Addressing shipping, durability, or ease of use.
6. **Social Commerce Caption**: Short caption for TikTok Shop / Instagram Shoppable post.
"""

    elif module_id == "marketing_strategy":
        return f"""
{brand_context}
### TASK: 360° Comprehensive Growth Marketing Strategy
- **Business Model**: {inputs.get('business_model', 'E-commerce / Services')}
- **Current Stage**: {inputs.get('current_stage', 'Scaling')}
- **Budget**: {inputs.get('monthly_budget', '$2,000/mo')}

Construct a battle-tested, end-to-end Marketing Strategy:
1. **Ideal Customer Profile (ICP) & Persona Breakdown**: Demographics, core psychographics, desires, fears.
2. **Positioning & Unique Value Proposition (UVP)**: Market differentiation angle.
3. **Full-Funnel Acquisition Strategy**:
   - Top of Funnel (TOFU - Awareness & Organic Reach)
   - Middle of Funnel (MOFU - Nurture, Retargeting & Trust)
   - Bottom of Funnel (BOFU - Conversion, Offers & Closing)
4. **Budget Allocation & Channel Matrix**: Percentage breakdown across Paid Ads, Content/SEO, Email, and Influencers.
5. **Key Performance Indicators (KPIs) to Track**: Exact metrics that define success.
"""

    elif module_id == "competitor_analysis":
        return f"""
{brand_context}
### TASK: Competitor Teardown & Strategic Gap Analysis
- **Your Brand**: {inputs.get('my_brand', 'Our Brand')}
- **Competitors**: {inputs.get('competitors', 'Main competitors')}

Deliver an in-depth Competitor Intelligence Report:
1. **Competitor Teardown**: Strengths, weaknesses, pricing strategy, and positioning vulnerabilities.
2. **Competitor Comparison Table**: Feature, Pricing, Speed, Tone, Customer Loyalty.
3. **Uncovered Market Gaps & White Space**: 3 specific angles/audiences your competitors are neglecting.
4. **Offensive Growth Playbook**: 3 specific marketing campaigns you should launch to capture their market share.
"""

    elif module_id == "executive_reports":
        return f"""
{brand_context}
### TASK: Executive Marketing & ROI Review
- **Report Period**: {inputs.get('report_period', 'Monthly Review')}
- **Raw Metrics**: {inputs.get('metrics_summary', 'Positive ROI')}
- **Next Goals**: {inputs.get('next_month_goals', 'Scale winning channels')}

Generate a polished Executive Marketing Report designed to impress stakeholders and business owners:
1. **Executive Highlights & ROI Summary**: High-level wins, efficiency gains, and top-line growth.
2. **KPI Scorecard**: Formatted Markdown table comparing Targets vs. Actual Results.
3. **What Worked (Winning Initiatives)**: Analysis of top campaigns and creative assets.
4. **What Needs Optimization**: Bottlenecks identified and countermeasures taken.
5. **Strategic Action Plan for Next Period**: 3 critical milestones and expected revenue impact.
"""

    else:
        return f"""
{brand_context}
{lang_instruction}
### TASK: {module_name}
User Input Parameters:
{json.dumps(inputs, indent=2)}

Please provide a comprehensive, expert, high-impact marketing deliverable formatted cleanly in Markdown.
"""
