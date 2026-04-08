"""
Sales Training Curriculum — TrueSkills Sales Coach
====================================================
Covers 8 core sales skill tracks across 3 experience levels.
Mirrors the structure of curriculum.py for model compatibility.

Experience levels (replaces year_group):
  junior  — 0-2 years selling
  mid     — 2-5 years
  senior  — 5+ years / team lead

Skill tracks (replaces subjects):
  prospecting       — finding and qualifying leads
  discovery         — needs analysis and questioning
  presentation      — value proposition and demos
  objection_handling — overcoming resistance
  closing           — gaining commitment
  negotiation       — terms, price, and win-win
  account_management — retention and expansion
  sales_mindset     — resilience, psychology, habits
"""


# ══════════════════════════════════════════════════════════════════
# CURRICULUM DATA
# ══════════════════════════════════════════════════════════════════

CURRICULUM = {

    # ── PROSPECTING ───────────────────────────────────────────────
    'prospecting': [
        {
            'id': 'icp_definition',
            'topic': 'Defining Your Ideal Customer Profile (ICP)',
            'leo_intro': (
                'An ICP is a detailed description of the company and buyer '
                'most likely to buy from you, stay, and grow. Without a clear ICP '
                'you waste pipeline time on deals that will never close.'
            ),
            'examples': {
                'tech_saas':          'A 50-200 person SaaS company with a RevOps team and at least one failed CRM migration.',
                'pharma':             'A GP surgery with a high repeat-prescription patient base and an open formulary.',
                'financial_services': 'A self-employed professional aged 35-55 with pension gap and no current IFA.',
                'construction':       'A tier-2 contractor bidding on public-sector contracts between £500k-£5m.',
                'recruitment':        'A scale-up that has just raised a Series A and is hiring a commercial team.',
                'general':            'A business with a clearly felt pain, budget authority, and a 90-day buying window.',
            },
            'common_mistakes': [
                'Defining ICP too broadly — "any company with a sales team"',
                'Confusing the user with the buyer',
                'Ignoring churn data when building ICP criteria',
            ],
        },
        {
            'id': 'cold_outreach',
            'topic': 'Cold Outreach — Email and Phone',
            'leo_intro': (
                'Cold outreach earns attention by leading with relevance, not product. '
                'The first sentence must be about them, not you. '
                'Pattern: trigger event → relevant insight → low-friction ask.'
            ),
            'examples': {
                'tech_saas':          '"Saw you just expanded to Germany — compliance automation gets painful fast at that stage. Worth a 15-minute call?"',
                'pharma':             '"Your trust is moving to a new prescribing framework in Q2 — I have a protocol that is saving other GPs two admin hours a week."',
                'financial_services': '"You were promoted to director last month. Congratulations. Have you updated your protection planning since the salary jump?"',
                'construction':       '"You won the Riverside contract — managing subcontractor compliance on projects that size is a common squeeze point. Can we show you how others handle it?"',
                'general':            '"I noticed [specific trigger]. Other [similar companies] are tackling it by [insight]. Worth a 15-minute conversation?"',
            },
            'common_mistakes': [
                'Opening with "I hope this finds you well"',
                'Describing the product before establishing relevance',
                'Asking for a 30-minute meeting in message one',
                'No clear call to action',
            ],
        },
        {
            'id': 'linkedin_prospecting',
            'topic': 'LinkedIn Prospecting and Social Selling',
            'leo_intro': (
                'Social selling is about being findable, credible, and warm before the call. '
                'Engage genuinely before you pitch. Build signal — comments, shares, and DMs '
                'that add value first.'
            ),
            'examples': {
                'tech_saas':          'Comment on a CTO\'s post about scaling pain before sending a connection request.',
                'pharma':             'Share a clinical brief with a genuine insight note — not a product mention.',
                'general':            'Connect → comment on 2-3 posts → warm DM referencing their content → soft ask.',
            },
            'common_mistakes': [
                'Pitching in the connection request message',
                'Generic "I would love to connect" without context',
                'No profile optimisation — buyer perspective missing',
            ],
        },
        {
            'id': 'lead_qualification',
            'topic': 'Lead Qualification — BANT, MEDDIC, SPICED',
            'leo_intro': (
                'Qualification is about protecting your time. BANT: Budget, Authority, Need, Timeline. '
                'MEDDIC adds Metrics, Economic Buyer, Decision Criteria, Decision Process, Identify Pain, Champion. '
                'SPICED: Situation, Pain, Impact, Critical Event, Decision. '
                'Pick one framework and use it consistently.'
            ),
            'examples': {
                'tech_saas':          'MEDDIC for enterprise. SPICED for mid-market. BANT too shallow for complex sales.',
                'financial_services': 'BANT works well — budget and authority are paramount in regulated sales.',
                'general':            'At minimum: Does this person have pain, money, and the authority to say yes?',
            },
            'common_mistakes': [
                'Treating qualification as a one-time event rather than ongoing',
                'Accepting "we have budget" without probing timing and sign-off',
                'Moving to demo without a confirmed pain statement',
            ],
        },
    ],

    # ── DISCOVERY ─────────────────────────────────────────────────
    'discovery': [
        {
            'id': 'discovery_call_structure',
            'topic': 'Discovery Call Structure',
            'leo_intro': (
                'A discovery call is not a pitch. It is a diagnostic. '
                'Structure: set the agenda → ask about current state → uncover pain → '
                'quantify impact → explore desired future state → qualify → agree next step. '
                'Talk less than 40% of the time.'
            ),
            'examples': {
                'tech_saas':          '"Before I show you anything — help me understand what is breaking in your current pipeline process."',
                'pharma':             '"How are you currently managing your formulary decisions? What is taking the most time?"',
                'general':            '"What does the problem cost you today — in time, money, or missed opportunity?"',
            },
            'common_mistakes': [
                'Talking more than listening',
                'Jumping to solution before quantifying pain',
                'Not agreeing a next step before hanging up',
                'Asking closed questions when open ones would get more signal',
            ],
        },
        {
            'id': 'spin_selling',
            'topic': 'SPIN Selling — Situation, Problem, Implication, Need-Payoff',
            'leo_intro': (
                'SPIN is a questioning sequence. Situation establishes context. '
                'Problem surfaces the pain. Implication amplifies the cost of inaction. '
                'Need-Payoff gets the buyer to articulate the value of solving it themselves. '
                'The buyer who sells themselves closes faster.'
            ),
            'examples': {
                'tech_saas':          'Implication: "If this reporting lag continues into Q4, what does that do to your board presentation?"',
                'financial_services': 'Need-Payoff: "If we could solve the protection gap now, what would that peace of mind mean for you?"',
                'general':            '"What happens if this problem is still here in 12 months?"',
            },
            'common_mistakes': [
                'Using implication questions aggressively — they feel manipulative if overdone',
                'Skipping situation questions and looking uninformed',
                'Not recording answers — discovery insights must feed the proposal',
            ],
        },
        {
            'id': 'stakeholder_mapping',
            'topic': 'Stakeholder Mapping and Champion Building',
            'leo_intro': (
                'Most B2B deals involve 5-8 stakeholders. Map them: Champion (wants it), '
                'Economic Buyer (signs off), Decision Maker (owns the outcome), '
                'Blocker (threatened by change). '
                'Build your champion into a coach — give them the internal pitch.'
            ),
            'examples': {
                'tech_saas':          'Your champion is the RevOps lead. The blocker is the CFO. Get RevOps to quantify the ROI in CFO language.',
                'construction':       'Your champion is the project manager. The economic buyer is the commercial director. Never skip the commercial director.',
                'general':            '"Who else is going to look at this before a decision is made?"',
            },
            'common_mistakes': [
                'Selling only to your contact and ignoring the real decision maker',
                'Not arming the champion with the internal business case',
                'Failing to identify blockers early',
            ],
        },
    ],

    # ── PRESENTATION ──────────────────────────────────────────────
    'presentation': [
        {
            'id': 'value_proposition',
            'topic': 'Building a Sharp Value Proposition',
            'leo_intro': (
                'A value proposition is not a feature list. It is: '
                'For [specific customer] who has [specific problem], '
                'we provide [specific solution] that delivers [specific measurable outcome], '
                'unlike [alternative] which [weakness].'
            ),
            'examples': {
                'tech_saas':          '"For RevOps teams frustrated by broken CRM data, we clean and enrich pipeline automatically — cutting report prep from 3 hours to 20 minutes, unlike manual hygiene tools that still need daily admin."',
                'pharma':             '"For GPs managing high-volume formulary decisions, our protocol reduces prescribing admin by two hours per week without changing clinical workflow."',
                'general':            'One sentence: specific customer, specific pain, specific outcome, specific differentiator.',
            },
            'common_mistakes': [
                'Leading with features, not outcomes',
                'Using vague language: "best-in-class", "end-to-end solution"',
                'No quantified claim',
                'No differentiation from the obvious alternative',
            ],
        },
        {
            'id': 'demo_skills',
            'topic': 'Running a High-Impact Demo',
            'leo_intro': (
                'A demo is not a tour of the product. It is a story about the buyer\'s future. '
                'Structure: recap discovery pain → show ONLY the features that solve that pain → '
                'narrate outcomes, not clicks → stop and check. '
                'Lead with "Here is the problem you described. Watch what happens."'
            ),
            'examples': {
                'tech_saas':          '"You told me reporting takes your team 3 hours on Monday. Here is Monday at 8am after we go live."',
                'financial_services': '"You said your biggest concern was your family\'s income if you were unable to work. Let me show you exactly what that protection looks like."',
                'general':            'Show the before → show the after → let them feel the gap.',
            },
            'common_mistakes': [
                'Screen-sharing everything — loss of attention after 4 minutes',
                'Talking through every feature nobody asked about',
                'Not pausing to ask "Does this solve what you described?"',
                'No clear next step at the end of the demo',
            ],
        },
        {
            'id': 'proposal_writing',
            'topic': 'Writing Proposals That Get Read',
            'leo_intro': (
                'Proposals fail because they are about you, not the buyer. '
                'Structure: their situation as you understood it → the problem in their words → '
                'your recommended approach → expected outcomes → investment → next step. '
                'Use their language, not your brochure language.'
            ),
            'examples': {
                'tech_saas':          'Section 1: "Based on our conversation, your pipeline visibility problem is costing your team X hours per week..."',
                'construction':       'Mirror the specification language from their tender brief exactly.',
                'general':            'If the buyer reads only the first paragraph, they should still know exactly why this proposal was written for them.',
            },
            'common_mistakes': [
                'Starting with company history and awards',
                'No executive summary',
                'Sending without a follow-up plan',
                'Price before value is established',
            ],
        },
    ],

    # ── OBJECTION HANDLING ─────────────────────────────────────────
    'objection_handling': [
        {
            'id': 'objection_types',
            'topic': 'Classifying Objections — Real vs Stall vs Condition',
            'leo_intro': (
                'Not all objections are equal. A condition is a genuine blocker '
                '(no budget, no authority — qualification failure). '
                'A stall is a delay tactic. A real objection is a concern worth addressing. '
                'Misreading a stall as a condition kills pipeline.'
            ),
            'examples': {
                'general': '"It is too expensive" — real objection or stall? Ask: "Too expensive compared to what?" If they disengage, stall. If they engage, real.',
            },
            'common_mistakes': [
                'Accepting "we will think about it" without probing',
                'Overcoming conditions — waste of both parties\' time',
                'Responding to a price objection before understanding the root cause',
            ],
        },
        {
            'id': 'price_objection',
            'topic': 'Handling the Price Objection',
            'leo_intro': (
                'Price objections are almost always value gaps, not budget problems. '
                'Sequence: acknowledge → explore ("too expensive compared to what?") → '
                'reframe to cost of inaction → restate ROI in their terms → '
                'if genuine, explore flexibility (phased, pilot, scope reduction). '
                'Never discount before you have defended value.'
            ),
            'examples': {
                'tech_saas':          '"You mentioned reporting costs your team 12 hours a week. At £40/hour, that is £25k a year. Our platform is £18k. Help me understand where the mismatch is."',
                'financial_services': '"The premium is £80 a month. The cover is £300,000. What would replacing your income cost your family if the worst happened?"',
                'general':            'Make the cost of inaction bigger than the price of action.',
            },
            'common_mistakes': [
                'Discounting immediately — destroys margin and credibility',
                'Apologising for the price',
                'Not having a ROI calculation ready',
                'Matching competitor price without exploring value first',
            ],
        },
        {
            'id': 'competitor_objection',
            'topic': 'Handling "We Are Looking at Your Competitor"',
            'leo_intro': (
                'Never criticise the competitor. Instead: acknowledge → get curious '
                '("what is drawing you to them?") → find the gap → reframe around '
                'your specific strengths. '
                'The goal is to make the evaluation criteria favour you.'
            ),
            'examples': {
                'tech_saas':          '"What specifically are they offering that you are hoping to solve?" Then: "That is interesting — here is where our customers typically find the difference matters..."',
                'general':            '"Great — it means you have budget and intent to solve this. Let me help you make sure you are comparing the right things."',
            },
            'common_mistakes': [
                'Badmouthing the competitor — immediately reduces credibility',
                'Going silent or defensive',
                'Not understanding your own competitive differentiation',
            ],
        },
        {
            'id': 'timing_objection',
            'topic': 'Handling "Not the Right Time"',
            'leo_intro': (
                '"Not now" usually means "not convinced yet." '
                'Probe the real reason: "What would need to be true for the timing to be right?" '
                'Then look for a critical event — a board review, fiscal year end, headcount freeze — '
                'that creates urgency they own, not you.'
            ),
            'examples': {
                'tech_saas':          '"Totally understand. When does your next planning cycle start? If we solve this after that, you are adding another quarter of the problem."',
                'general':            '"What is happening in the business right now that makes this a lower priority than it was when we first spoke?"',
            },
            'common_mistakes': [
                'Accepting the timing objection and disappearing for 6 months',
                'Creating fake urgency — "offer ends Friday"',
                'Not finding the real critical event',
            ],
        },
    ],

    # ── CLOSING ───────────────────────────────────────────────────
    'closing': [
        {
            'id': 'trial_closes',
            'topic': 'Trial Closes and Buying Signals',
            'leo_intro': (
                'Trial closes test readiness without pressure. '
                'Use them throughout the conversation: '
                '"If we could solve X, would that be valuable to you?" '
                '"How does this compare to what you were hoping to see?" '
                'Buying signals: future-tense language, questions about implementation, '
                'involving other stakeholders.'
            ),
            'examples': {
                'tech_saas':          'Buying signal: "How long does onboarding typically take?" — they are mentally past the purchase.',
                'financial_services': '"How does this feel compared to what you were looking for?" — check temperature before the summary.',
                'general':            'Any question about logistics, start dates, or "what happens next" is a buying signal.',
            },
            'common_mistakes': [
                'Ignoring buying signals and continuing to pitch',
                'Using closing techniques as pressure tactics — destroys trust',
                'Waiting for the buyer to ask to buy',
            ],
        },
        {
            'id': 'closing_techniques',
            'topic': 'Closing Techniques That Do Not Feel Manipulative',
            'leo_intro': (
                'The best close is a natural next step from a well-run process. '
                'Summary close: recap the agreed value → ask for commitment. '
                'Assumptive close: "Shall we get the paperwork started?" '
                'Alternative close: "Do you want to start with the standard package or the enterprise?" '
                'Direct close: "Are you ready to move forward?"'
            ),
            'examples': {
                'tech_saas':          '"We have agreed it solves the pipeline visibility problem and pays back in 4 months. Are you comfortable moving forward?"',
                'construction':       '"Based on the spec and your timeline, we can mobilise on the 14th. Shall I confirm the order?"',
                'general':            'Always earn the close — the ask should feel like the natural conclusion, not a surprise.',
            },
            'common_mistakes': [
                'Not asking for the business at all',
                'Closing before value is established',
                'Asking "What do you think?" instead of "Shall we move forward?"',
                'Talking past the close — continuing to sell after they have said yes',
            ],
        },
        {
            'id': 'next_step_discipline',
            'topic': 'Next Step Discipline — Never Leave Without One',
            'leo_intro': (
                'Every interaction must end with a specific, committed, time-stamped next step. '
                '"I will follow up next week" is not a next step. '
                '"Let us book 30 minutes on Tuesday at 2pm with your CFO included" is. '
                'Deals stall because next steps are vague.'
            ),
            'examples': {
                'tech_saas':          '"Before we end — can we lock in Tuesday at 2pm for the technical review with your IT lead?"',
                'general':            '"What needs to happen on your side before we can move forward — and when can we reconnect to confirm that?"',
            },
            'common_mistakes': [
                '"I\'ll send you a proposal" with no follow-up date agreed',
                'Letting the buyer set a vague timeline',
                'Not confirming who owns the next action',
            ],
        },
    ],

    # ── NEGOTIATION ───────────────────────────────────────────────
    'negotiation': [
        {
            'id': 'negotiation_preparation',
            'topic': 'Negotiation Preparation — Know Your Positions',
            'leo_intro': (
                'Walk into every negotiation knowing three things: '
                'your ideal outcome, your acceptable outcome, and your walk-away point. '
                'Also know: what the buyer values most (not always price), '
                'what you can flex (payment terms, scope, support level), '
                'and what you cannot.'
            ),
            'examples': {
                'tech_saas':          'They want 20% off. You can flex to 10% if they agree to a 2-year term and case study rights.',
                'construction':       'They want a faster delivery. You can meet it if they accept a 5% premium for overtime.',
                'general':            'Never negotiate price in isolation. Always trade: "I can do X if you can do Y."',
            },
            'common_mistakes': [
                'Going in without knowing your walk-away',
                'Giving concessions without getting anything in return',
                'Negotiating against yourself — conceding before they push',
            ],
        },
        {
            'id': 'anchoring',
            'topic': 'Anchoring and the Psychology of First Numbers',
            'leo_intro': (
                'The first number in a negotiation acts as an anchor. '
                'Whoever names the first number usually wins. '
                'Always present your price with confidence — not as a question. '
                'If pushed to discount, re-anchor around value, not the discount amount.'
            ),
            'examples': {
                'general':            '"The investment is £24,000 per year." — not "It is around £24k, though we can look at that..."',
            },
            'common_mistakes': [
                'Apologising before naming the price',
                'Volunteering a discount before the buyer asks',
                'Accepting the buyer\'s anchor without challenge',
            ],
        },
        {
            'id': 'win_win_close',
            'topic': 'Finding the Win-Win Without Losing Margin',
            'leo_intro': (
                'Win-win is not about splitting the difference. It is about finding '
                'what each party values differently and trading those things. '
                'You might value cash flow; they might value flexibility. '
                'They might value speed; you might value volume. '
                'The best deals are asymmetric trades, not equal cuts.'
            ),
            'examples': {
                'tech_saas':          'They want lower monthly cost. You want annual commitment. Solution: annual upfront at 8% discount.',
                'financial_services': 'They want lower premium. You want policy longevity. Solution: index-linked with review in year 3.',
                'general':            '"What is most important to you in making this work?" — then trade against that.',
            },
            'common_mistakes': [
                'Meeting in the middle on price when other variables could close the gap',
                'Not asking what the buyer values most before conceding',
                'Treating negotiation as a battle rather than a design problem',
            ],
        },
    ],

    # ── ACCOUNT MANAGEMENT ─────────────────────────────────────────
    'account_management': [
        {
            'id': 'qbr_skills',
            'topic': 'Running an Effective QBR (Quarterly Business Review)',
            'leo_intro': (
                'A QBR is not a support call or a status update. '
                'It is a strategic conversation about the customer\'s goals and how you are helping them hit those goals. '
                'Structure: their goals this quarter → your contribution → what is not working → next quarter plan → expansion opportunity.'
            ),
            'examples': {
                'tech_saas':          '"Last quarter your goal was to reduce sales cycle by 20%. Here is what the data shows. What is the priority for Q2?"',
                'general':            'Lead with their metrics, not your product usage statistics.',
            },
            'common_mistakes': [
                'Making it a product update presentation',
                'No agenda sent in advance',
                'Not involving the economic buyer — QBR with only the user is a missed opportunity',
                'No expansion conversation',
            ],
        },
        {
            'id': 'expansion_selling',
            'topic': 'Expansion Selling — Upsell and Cross-sell',
            'leo_intro': (
                'Expansion is easier than new business — the trust is already there. '
                'The trigger is always the customer\'s next goal, not your next product release. '
                '"You hit X. Your next challenge is Y. Here is how we solve Y." '
                'Never pitch an upsell before the customer has realised value from the existing deal.'
            ),
            'examples': {
                'tech_saas':          '"Your team is now saving 3 hours a week on reporting. The next bottleneck your ops lead mentioned was forecasting accuracy — that is exactly what our Analytics tier solves."',
                'general':            'Expansion pitch = their new goal + your next product + bridge between the two.',
            },
            'common_mistakes': [
                'Upselling before proving ROI on current contract',
                'Leading with the product rather than the new pain',
                'Pitching the upsell to the wrong stakeholder',
            ],
        },
        {
            'id': 'churn_prevention',
            'topic': 'Churn Prevention and At-Risk Account Signals',
            'leo_intro': (
                'Churn rarely surprises you if you are paying attention. '
                'Early signals: reduced product usage, support ticket spike, champion leaves, '
                'missed QBR, non-renewal of secondary contract, budget freeze. '
                'Intervene early with a save call — not a renewal pitch.'
            ),
            'examples': {
                'tech_saas':          '"I noticed login activity dropped 40% last month. Can we spend 20 minutes understanding what has changed?"',
                'general':            '"Your renewal is in 90 days. Before we get there, I want to make sure you are getting full value. Can we do a health check call this week?"',
            },
            'common_mistakes': [
                'Only calling when the renewal is 30 days out',
                'Sending a renewal invoice without a conversation first',
                'Not identifying the champion\'s departure as a churn risk',
            ],
        },
    ],

    # ── SALES MINDSET ──────────────────────────────────────────────
    'sales_mindset': [
        {
            'id': 'rejection_resilience',
            'topic': 'Rejection Resilience and the Numbers Game',
            'leo_intro': (
                'Rejection is data, not verdict. Every no is qualification — it narrows your pipeline to people who can buy. '
                'Know your conversion rates at each stage. If you need 10 demos to close 2, '
                'a no to a demo request is just the pipeline doing its job. '
                'Detachment from individual outcomes is a competitive advantage.'
            ),
            'examples': {
                'general':            '"I need 50 calls to book 10 meetings to close 2 deals. That no is call 37 of 50."',
            },
            'common_mistakes': [
                'Taking rejection personally — the no is about fit, not worth',
                'Stopping at the first objection',
                'Not tracking conversion rates to understand where the pipeline leaks',
            ],
        },
        {
            'id': 'daily_discipline',
            'topic': 'Daily Sales Discipline — Habits That Compound',
            'leo_intro': (
                'Top performers protect two things: prospecting time and pipeline hygiene. '
                'Block 90 minutes every morning for outbound — non-negotiable. '
                'Update your CRM same-day. Review your pipeline weekly against criteria, not gut feel. '
                'Discipline is the differentiator when skills are equal.'
            ),
            'examples': {
                'general':            '8:30-10:00am: outbound only. No email, no Slack, no admin. Every day.',
            },
            'common_mistakes': [
                'Letting admin eat prospecting time',
                'CRM updates left to Friday — memory degrades, data is wrong',
                'Pipeline reviews based on "I feel good about this one"',
            ],
        },
        {
            'id': 'growth_mindset_sales',
            'topic': 'Growth Mindset in Sales — Learning from Lost Deals',
            'leo_intro': (
                'Every lost deal has a lesson. The discipline is extracting it. '
                'Run a win/loss debrief on every closed deal — won and lost. '
                'Ask the buyer directly: "What could we have done differently?" '
                'Most will tell you. Most reps never ask.'
            ),
            'examples': {
                'general':            '"We lost the deal. Before we move on — what did we learn about our qualification, our demo, our proposal, or our timing?"',
            },
            'common_mistakes': [
                'Moving on from a lost deal without debriefing it',
                'Blaming the price without examining the value case',
                'Not asking the buyer for feedback directly',
            ],
        },
    ],
}


# ══════════════════════════════════════════════════════════════════
# CURRICULUM API — mirrors curriculum.py interface
# ══════════════════════════════════════════════════════════════════

def get_curriculum(experience_level, skill_track):
    """
    Returns topic list for a given experience level and skill track.
    experience_level: 'junior' | 'mid' | 'senior'
    skill_track: key from CURRICULUM dict
    All tracks are available at all levels — Max adjusts depth via prompt.
    """
    track = CURRICULUM.get(skill_track, [])
    if not track:
        # Fallback — return first available track
        first_key = next(iter(CURRICULUM))
        track = CURRICULUM[first_key]
    return track


def get_next_topic(experience_level, skill_track, covered_unit_ids):
    """
    Returns the next uncovered topic in the track.
    Falls back to first topic if all covered (for review).
    """
    track = get_curriculum(experience_level, skill_track)
    covered = set(covered_unit_ids or [])
    for topic in track:
        if topic['id'] not in covered:
            return topic
    # All covered — return first for revision
    return track[0] if track else None


def get_example(examples_dict, industry):
    """
    Returns the most relevant scenario example for the learner's industry.
    Falls back to 'general' if their sector is not mapped.
    """
    if not examples_dict:
        return 'a realistic sales scenario relevant to your sector.'
    return (
        examples_dict.get(industry)
        or examples_dict.get('general')
        or next(iter(examples_dict.values()))
    )


def get_all_tracks():
    """Returns list of available skill track IDs."""
    return list(CURRICULUM.keys())


def get_track_topics(skill_track):
    """Returns all topic IDs in a track."""
    return [t['id'] for t in CURRICULUM.get(skill_track, [])]


def get_topic_by_id(unit_id):
    """Find a topic across all tracks by ID."""
    for track in CURRICULUM.values():
        for topic in track:
            if topic['id'] == unit_id:
                return topic
    return None
