"""
Max — adaptive sales training coach prompt engine.
Reads last 5 sessions from DB on every turn.
Calibrates level, engagement, skill track and scenario automatically.

Repurposed from TrueSkills L2L child tutor engine.
Now targets adult sales professionals.
"""

import json
import sales_curriculum as cur
from models import db, QuestionBank, SessionSummary


# ── PHASE CONFIGURATION ──────────────────────────────────────────

THRESHOLDS = {
    'rapport':   3,
    'returning': 1,
    'i_do':      3,
    'we_do':     8,
    'you_do':    3,
    'bonus':     2,
    'debrief':   2,
}
PHASE_ORDER = ['rapport', 'i_do', 'we_do', 'you_do', 'bonus', 'debrief', 'done']


# ── SCENARIO WRAPPERS ────────────────────────────────────────────
# Replaces child narrative wrappers with professional sales contexts

SCENARIO_WRAPPERS = {
    'tech_saas': {
        'frame':   'Deal Room',
        'task':    'deal',
        'correct': 'Strong move',
        'hint':    'sales tip',
        'intro':   'New scenario',
        'finish':  'Deal closed',
    },
    'pharma': {
        'frame':   'Territory Brief',
        'task':    'call',
        'correct': 'Solid approach',
        'hint':    'clinical cue',
        'intro':   'Next call',
        'finish':  'Territory updated',
    },
    'financial_services': {
        'frame':   'Client Brief',
        'task':    'meeting',
        'correct': 'Sharp insight',
        'hint':    'compliance note',
        'intro':   'Next meeting',
        'finish':  'Brief filed',
    },
    'construction': {
        'frame':   'Bid Room',
        'task':    'pitch',
        'correct': 'Bid secured',
        'hint':    'specs tip',
        'intro':   'Next tender',
        'finish':  'Contract won',
    },
    'recruitment': {
        'frame':   'Candidate Pipeline',
        'task':    'placement',
        'correct': 'Strong fit',
        'hint':    'sourcing tip',
        'intro':   'New role',
        'finish':  'Placed',
    },
    'retail': {
        'frame':   'Shop Floor',
        'task':    'sale',
        'correct': 'Good upsell',
        'hint':    'floor tip',
        'intro':   'Next customer',
        'finish':  'Till closed',
    },
    'general': {
        'frame':   'Sales Playbook',
        'task':    'scenario',
        'correct': 'Nailed it',
        'hint':    'coaching tip',
        'intro':   'Next scenario',
        'finish':  'Session complete',
    },
}

def _nav(industry):
    return SCENARIO_WRAPPERS.get(industry, SCENARIO_WRAPPERS['general'])


# ── SESSION HISTORY ───────────────────────────────────────────────

def get_last_context(child_id):
    """
    Read last 5 sessions. Returns a dict used by build_prompt on every turn.
    child_id here is actually the learner/user ID — kept same param name
    for model compatibility.
    """
    sessions = (SessionSummary.query
                .filter_by(child_id=child_id)
                .order_by(SessionSummary.created_at.desc())
                .limit(5).all())
    if not sessions:
        return None

    latest          = sessions[0]
    recent_units    = [s.unit_name    for s in sessions if s.unit_name]
    recent_subjects = list(dict.fromkeys(s.subject for s in sessions if s.subject))
    struggles       = [s.struggled_with for s in sessions if s.struggled_with]
    strengths       = [s.went_well      for s in sessions if s.went_well]
    active_times    = [s.active_minutes for s in sessions if s.active_minutes]

    phase_rank = {p: i for i, p in enumerate(PHASE_ORDER)}
    best_phase = max(
        (s.phase_reached for s in sessions if s.phase_reached and s.phase_reached in phase_rank),
        key=lambda p: phase_rank.get(p, 0),
        default='rapport'
    )

    avg_mins = round(sum(active_times) / len(active_times), 1) if active_times else 0
    if avg_mins < 10:
        engagement = 'low'
    elif avg_mins < 25:
        engagement = 'medium'
    else:
        engagement = 'high'

    struggle_freq = {}
    for item in struggles:
        if item:
            struggle_freq[item] = struggle_freq.get(item, 0) + 1
    recurring = [k for k, v in struggle_freq.items() if v > 1]

    return {
        'subject':          latest.subject,
        'unit_name':        latest.unit_name,
        'phase_reached':    latest.phase_reached,
        'went_well':        latest.went_well,
        'struggled_with':   latest.struggled_with,
        'next_unit_id':     latest.next_unit_id,
        'next_unit_name':   latest.next_unit_name,
        'recent_units':     recent_units,
        'recent_subjects':  recent_subjects,
        'struggles':        struggles,
        'strengths':        strengths,
        'best_phase':       best_phase,
        'session_count':    len(sessions),
        'engagement':       engagement,
        'avg_session_mins': avg_mins,
        'recurring':        recurring,
    }


# ── LEARNER PROFILE ────────────────────────────────────────────────

def detect_child_profile(chat_log):
    """
    Classify learner as advanced / struggling / standard from first messages.
    Reused for adult learners: 'gifted' = experienced rep, 'sen' = needs extra support.
    """
    learner_msgs = [m.get('text', '') for m in chat_log if m.get('role') == 'user']
    if len(learner_msgs) < 2:
        return 'standard'

    sample = learner_msgs[:5]
    avg_words = sum(len(m.split()) for m in sample) / len(sample)

    experienced_vocab = [
        'pipeline', 'objection', 'discovery', 'cadence', 'quota', 'close',
        'stakeholder', 'champion', 'meddic', 'bant', 'spiced', 'value prop',
        'forecast', 'conversion', 'churn', 'expansion', 'arpu', 'account',
        'because', 'however', 'i find', 'in my experience', 'we typically',
    ]
    exp_hits = sum(1 for m in sample for w in experienced_vocab if w in m.lower())

    if avg_words >= 15 or exp_hits >= 2:
        return 'gifted'   # Experienced rep — push harder

    # Struggling: very short, non-technical answers
    short_non_numeric = [
        m for m in sample
        if len(m.strip()) < 5 and not any(c.isdigit() for c in m)
    ]
    if len(short_non_numeric) >= 3:
        return 'sen'      # Needs slower pace and more scaffolding

    return 'standard'


# ── DETECT STRUGGLE ───────────────────────────────────────────────

def detect_struggle(chat_log, last_n=6):
    msgs = [m for m in chat_log if m.get('role') == 'user']
    if len(msgs) < last_n:
        return False
    recent = msgs[-last_n:]
    blank = [
        m for m in recent
        if len(m.get('text', '').strip()) < 4
        and not any(c.isdigit() for c in m.get('text', ''))
    ]
    return len(blank) >= last_n - 1


# ── DETECT INDUSTRY / SECTOR ──────────────────────────────────────

def detect_interest(text):
    """Detect which sales sector the learner works in."""
    keywords = {
        'tech_saas':          ['saas', 'software', 'tech', 'cloud', 'api', 'startup', 'b2b', 'crm', 'platform'],
        'pharma':             ['pharma', 'pharmaceutical', 'medical', 'clinical', 'nhs', 'drug', 'rep', 'healthcare'],
        'financial_services': ['finance', 'banking', 'insurance', 'mortgage', 'wealth', 'investment', 'ifa', 'broker'],
        'construction':       ['construction', 'building', 'contractor', 'tender', 'civil', 'site', 'surveyor'],
        'recruitment':        ['recruitment', 'recruiter', 'staffing', 'talent', 'headhunt', 'candidate', 'hr'],
        'retail':             ['retail', 'shop', 'store', 'floor', 'upsell', 'customer service'],
    }
    t = text.lower()
    for sector, kws in keywords.items():
        if any(k in t for k in kws):
            return sector
    return 'general'


# ── QUESTION BANK ─────────────────────────────────────────────────

def ensure_question_bank(unit_id, subject, year_group, interest, gemini_client, model):
    """Generate roleplay scenarios for a sales unit — shared by all learners."""
    we  = QuestionBank.query.filter_by(unit_id=unit_id, phase='we_do').count()
    you = QuestionBank.query.filter_by(unit_id=unit_id, phase='you_do').count()
    if we >= 20 and you >= 5:
        return
    all_topics = cur.get_curriculum(year_group, subject)
    topic = next((t for t in all_topics if t['id'] == unit_id), None)
    if not topic:
        return
    if we < 20:
        _gen_questions(unit_id, subject, year_group, 'we_do',  20 - we,  topic, gemini_client, model, interest)
    if you < 5:
        _gen_questions(unit_id, subject, year_group, 'you_do',  5 - you, topic, gemini_client, model, interest)


def _gen_questions(unit_id, subject, year_group, phase, count, topic, gemini_client, model, interest='general'):
    if not gemini_client:
        return
    level = year_group  # e.g. 'junior', 'mid', 'senior'
    style = "coached roleplay (coach helps)" if phase == 'we_do' else "solo roleplay (no help)"
    sector = interest or 'general B2B'

    prompt = (
        f"Generate {count} {style} sales training scenarios for a {level}-level sales rep in the {sector} sector.\n"
        f"Topic: {topic['topic']}\n"
        f"Core concept: {topic['leo_intro']}\n"
        f"Common mistakes: {topic.get('common_mistakes', [])}\n"
        f"Rules: realistic objections or customer lines, varied scenarios, professional tone.\n"
        f"Return ONLY JSON array: "
        f'[{{"question":"The prospect says: \'...\'  What do you say?","answer_guide":"..."}}]\n'
        f"No markdown, no preamble."
    )
    try:
        from google.genai import types
        r = gemini_client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(max_output_tokens=2000, temperature=0.8),
        )
        text = r.text.strip()
        if '```' in text:
            text = text.split('```')[1]
            if text.startswith('json'):
                text = text[4:]
        text = text.strip()
        try:
            qs = json.loads(text)
        except json.JSONDecodeError:
            cleaned = (text
                .replace('\u2019', "'").replace('\u2018', "'")
                .replace('\u201c', '"').replace('\u201d', '"'))
            try:
                qs = json.loads(cleaned)
            except Exception:
                import re
                pairs = re.findall(
                    r'"question"\s*:\s*"((?:[^"\\]|\\.)*)"\s*,\s*"answer_guide"\s*:\s*"((?:[^"\\]|\\.)*)"',
                    text, re.DOTALL)
                qs = [{"question": q, "answer_guide": a} for q, a in pairs] if pairs else []
        if not qs:
            print(f"[QB] {unit_id}/{phase}: could not parse")
            return
        for q in qs[:count]:
            if q.get('question'):
                db.session.add(QuestionBank(
                    unit_id=unit_id, subject=subject, year_group=year_group,
                    phase=phase, question_text=q['question'],
                    answer_guide=q.get('answer_guide', ''),
                ))
        db.session.commit()
        print(f"[QB] generated {count} {phase} scenarios for {unit_id}")
    except Exception as e:
        print(f"[QB] {unit_id}/{phase}: {e}")
        db.session.rollback()


def get_next_question(unit_id, phase, idx):
    qs = (QuestionBank.query
          .filter_by(unit_id=unit_id, phase=phase)
          .order_by(QuestionBank.id).all())
    if not qs:
        return None
    return qs[idx % len(qs)]


# ── SESSION SUMMARY ───────────────────────────────────────────────

def write_session_summary(ls, child, gemini_client, model):
    if SessionSummary.query.filter_by(session_id=ls.session_id).first():
        return
    went_well = struggled_with = None
    chat_log  = ls.chat_log or []
    if gemini_client and len(chat_log) >= 4:
        try:
            transcript = '\n'.join(
                f"{'Rep' if m['role'] == 'user' else 'Max'}: {m['text']}"
                for m in chat_log[-20:]
            )
            from google.genai import types
            r = gemini_client.models.generate_content(
                model=model,
                contents=(
                    'Sales coaching transcript. Return ONLY JSON: '
                    '{"went_well":"one sentence","struggled_with":"one sentence"}\n\n'
                    + transcript
                ),
                config=types.GenerateContentConfig(max_output_tokens=80, temperature=0.2),
            )
            data           = json.loads(r.text.strip().replace('```json', '').replace('```', ''))
            went_well      = data.get('went_well')
            struggled_with = data.get('struggled_with')
        except Exception as e:
            print(f"[SUMMARY] {e}")

    covered    = ls.leo_concepts_covered or []
    subject    = ls.session_type or 'prospecting'
    year_group = ls.year_group or 'junior'
    nxt        = cur.get_next_topic(year_group, subject, covered)

    db.session.add(SessionSummary(
        child_id=child.id, session_id=ls.session_id,
        subject=subject, year_group=year_group,
        unit_id=ls.unit_id, unit_name=ls.unit_name,
        phase_reached=ls.leo_phase, units_covered=covered,
        active_minutes=ls.active_minutes or 0,
        went_well=went_well, struggled_with=struggled_with,
        next_unit_id=nxt['id'] if nxt else None,
        next_unit_name=nxt['topic'] if nxt else None,
    ))
    db.session.commit()


# ── PROACTIVE NUDGES ──────────────────────────────────────────────

def get_proactive_nudge(child, ls, active_minutes):
    name       = child.first_name
    chat_log   = ls.chat_log or []
    child_msgs = [m for m in chat_log if m.get('role') == 'user']
    flags      = list(ls.behaviour_flags or [])
    fired      = {f for f in flags if f.startswith('nudge:')}

    if active_minutes >= 2 and len(child_msgs) == 0 and 'nudge:open' not in fired:
        flags.append('nudge:open')
        ls.behaviour_flags = flags
        return f"Whenever you're ready, {name}. No rush — take a moment to settle in."

    if active_minutes >= 6 and 'nudge:silent' not in fired:
        last_rep = next((m for m in reversed(chat_log) if m.get('role') == 'user'), None)
        if not last_rep:
            flags.append('nudge:silent')
            ls.behaviour_flags = flags
            return f"Still here, {name}. Jump in whenever — there are no wrong answers in practice."

    if len(child_msgs) >= 3 and 'nudge:struggle' not in fired:
        if all(len(m.get('text', '').strip()) < 8 for m in child_msgs[-3:]):
            flags.append('nudge:struggle')
            ls.behaviour_flags = flags
            return f"Let's slow it down, {name}. We can work through this one step at a time."

    if active_minutes == 30 and 'nudge:30min' not in fired:
        flags.append('nudge:30min')
        ls.behaviour_flags = flags
        return f"30 minutes of focused practice, {name}. That is a real training commitment."

    return None


# ── PHASE LOGIC ───────────────────────────────────────────────────

def should_advance(phase, msgs_in_phase, we_do_attempts):
    if phase == 'we_do':
        return we_do_attempts >= THRESHOLDS['we_do']
    return msgs_in_phase >= THRESHOLDS.get(phase, 999)


def next_phase(current):
    if current == 'returning':
        return 'i_do'
    try:
        idx = PHASE_ORDER.index(current)
        return PHASE_ORDER[idx + 1] if idx + 1 < len(PHASE_ORDER) else 'done'
    except ValueError:
        return 'rapport'


# ── PROMPT BUILDER ────────────────────────────────────────────────

def build_prompt(child, topic, phase, question_row, last_context, story_mode=False):
    name     = child.first_name
    industry = (child.interests or {}).get('primary', 'general')
    nav      = _nav(industry)
    level    = (child.year_group or 'junior')  # junior / mid / senior

    # ── 1. Detect profile from live chat log ─────────────────────
    live_log = []
    try:
        from models import LearningSession
        from flask import session as fsess
        _ls = LearningSession.query.filter_by(session_id=fsess.get('ls_id')).first()
        if _ls:
            live_log = _ls.chat_log or []
    except Exception:
        pass
    profile = detect_child_profile(live_log)

    # ── 2. Language register ──────────────────────────────────────
    if profile == 'gifted':
        register = (
            f"REGISTER — EXPERIENCED REP: {name} knows the game. Skip basics. "
            f"Go straight to nuance, edge cases, and advanced technique. "
            f"Challenge their assumptions. Push for excellence, not just competency. "
            f"Treat them as a peer you're sharpening."
        )
    elif profile == 'sen':
        register = (
            f"REGISTER — BUILDING CONFIDENCE: {name} is finding their footing. "
            f"ONE idea per turn. Short, clear language. No jargon without explanation. "
            f"Make every small win feel real. Keep momentum low and steady."
        )
    else:
        register = (
            f"REGISTER — STANDARD: Professional, direct, one idea at a time. "
            f"No corporate waffle. Natural coaching tone. Never two questions at once."
        )

    # ── 3. Current skill track ────────────────────────────────────
    current_subject = 'sales skills'
    try:
        from flask import session as fsess
        from models import LearningSession
        _ls2 = LearningSession.query.filter_by(session_id=fsess.get('ls_id')).first()
        if _ls2 and _ls2.session_type:
            current_subject = _ls2.session_type.replace('_', ' ').title()
    except Exception:
        pass

    # ── 4. 5-session history block ────────────────────────────────
    if last_context:
        n          = last_context.get('session_count', 0)
        units      = last_context.get('recent_units', [])
        subjects   = last_context.get('recent_subjects', [])
        struggles  = last_context.get('struggles', [])
        strengths  = last_context.get('strengths', [])
        best       = last_context.get('best_phase', 'rapport')
        engagement = last_context.get('engagement', 'medium')
        avg        = last_context.get('avg_session_mins', 0)
        recurring  = last_context.get('recurring', [])

        units_str     = ', '.join(units[-5:])     if units     else 'none yet'
        subjects_str  = ', '.join(subjects)        if subjects  else 'none yet'
        struggles_str = '; '.join(struggles[-3:])  if struggles else 'nothing notable'
        strengths_str = '; '.join(strengths[-3:])  if strengths else 'nothing noted yet'
        recurring_str = '; '.join(recurring)       if recurring else ''

        if engagement == 'low':
            eng_note = (f"{name} averages {avg} mins — possibly time-poor or disengaged. "
                        f"Start fast, make it relevant immediately.")
        elif engagement == 'medium':
            eng_note = f"{name} typically stays {avg} mins. Keep energy up."
        else:
            eng_note = f"{name} does full sessions ({avg} mins avg). Highly engaged — stretch them."

        teach_reason = ''
        try:
            from flask import session as fsess
            teach_reason = fsess.get('teach_reason', '') or ''
        except Exception:
            pass

        history = (
            f"\nLEARNER HISTORY — last {n} sessions:\n"
            f"  Topics covered: {units_str}\n"
            f"  Skill tracks done: {subjects_str}\n"
            f"  Struggled with: {struggles_str}\n"
            f"  Performed well on: {strengths_str}\n"
            f"  Best phase reached: {best}\n"
            f"  Engagement: {eng_note}\n"
        )
        if recurring_str:
            history += f"  RECURRING WEAK SPOTS — need extra work: {recurring_str}\n"
        if teach_reason and teach_reason != 'all_covered':
            history += f"  WHY TODAY'S SESSION: {teach_reason}\n"
        history += (
            f"CALIBRATION: Do NOT re-teach already mastered topics. "
            f"Do NOT pitch this below {name}'s demonstrated level."
        )
    else:
        history = (
            f"\nFIRST SESSION: {name} is new to this platform. "
            f"Start by understanding their background — sector, current role, and biggest sales challenge."
        )

    # ── 5. Core character block ───────────────────────────────────
    level_label = {'junior': 'new to sales', 'mid': 'developing rep', 'senior': 'experienced seller'}.get(level, 'sales professional')

    char = (
        f"You are Max, {name}'s personal sales coach. "
        f"{name} is a {level_label} in the {industry.replace('_',' ')} sector. "
        f"You are a high-performance coach — direct, warm, precise. Not a trainer reading slides. Not a bot.\n\n"
        f"{register}\n"
        f"{history}\n\n"
        f"SCENARIO CONTEXT — {nav['frame'].upper()}:\n"
        f"- ALL practice lives inside realistic {industry.replace('_',' ')} scenarios. "
        f"Tasks are called {nav['task']}s. Correct moves = '{nav['correct']}'. Coaching cues = {nav['hint']}s.\n"
        f"- NEVER use generic training-course language: no 'let us explore', 'great learning point', 'fantastic contribution'.\n\n"
        f"CURRENT SKILL TRACK: {current_subject}\n"
        f"- Focus on {current_subject} until this topic is mastered.\n"
        f"- If {name} asks to switch track: switch immediately. No detour.\n\n"
        f"ACCURACY — NON-NEGOTIABLE:\n"
        f"- NEVER validate a weak sales response. NEVER say 'good answer' to a poor technique.\n"
        f"- SOFT-STOP for errors: 'Hold on — let us look at that differently. What is the risk with that approach?'\n"
        f"- ONE coaching cue only. Do not give the script outright.\n"
        f"- If wrong twice: step back and reteach with a concrete scenario example.\n"
        f"- Acknowledge what was right specifically before correcting.\n\n"
        f"NO APOLOGIES:\n"
        f"- NEVER say 'My mistake', 'Sorry', or 'I was wrong'.\n"
        f"- If stuck: 'Let me come at this from a different angle.'\n\n"
        f"NEVER SAY:\n"
        f"- 'Wrong', 'incorrect', 'no', 'that is not right'\n"
        f"- 'Well done', 'great job', 'fantastic', 'brilliant'\n"
        f"- 'Let us explore', 'great learning point', 'as a sales professional'\n"
        f"- Two questions at once — always ONE\n"
        f"- Any reference to XP, points, scores, or rewards in dialogue\n\n"
        f"IF {name.upper()} STRUGGLES: slow down, reduce to first principles, new scenario angle.\n"
        f"IF {name.upper()} IS DEFENSIVE: 'Fair push-back. Let me show you why this matters in practice.'\n"
        f"COACHING PRAISE: 'That is exactly the instinct.' / 'You caught that fast — let us build on it.'\n\n"
        f"Max 80 words per reply. Conversational speech only. No bullet points. No headers."
    )

    # ── 6. Phase instruction ──────────────────────────────────────
    if story_mode:
        inst = (
            f"Tell {name} a brief, real-world sales scenario (3 sentences, no quiz). "
            f"End with: 'Want to try again? We can take it slower.'"
        )

    elif phase == 'rapport':
        inst = (
            f"Open the {nav['frame']} — welcome {name} genuinely. "
            f"No wrong answers, no pressure. "
            f"Ask ONE question about their current role or biggest sales challenge. "
            f"Listen for sector context — it informs the whole session."
        )

    elif phase == 'i_do':
        examples   = topic.examples   if hasattr(topic, 'examples')   else topic.get('examples', {})
        topic_name = topic.topic_name if hasattr(topic, 'topic_name') else topic.get('topic', '')
        intro      = topic.leo_intro  if hasattr(topic, 'leo_intro')  else topic.get('leo_intro', '')
        example    = cur.get_example(examples, industry)
        inst = (
            f"{nav['intro'].upper()}: Coach {name} on '{topic_name}'.\n"
            f"Core concept: {intro}\n"
            f"Use this {industry.replace('_',' ')} example: {example}\n"
            f"Walk through it as a coach, not a lecturer. "
            f"End with: 'Tell me when you are ready to try it.' "
            f"Do NOT ask a practice question this turn."
        )

    elif phase == 'we_do':
        topic_name = topic.topic_name if hasattr(topic, 'topic_name') else topic.get('topic', '')
        mistakes   = (topic.common_mistakes if hasattr(topic, 'common_mistakes')
                      else topic.get('common_mistakes', [])) or []
        q    = question_row.question_text if question_row else f"a {topic_name} roleplay scenario"
        hint = question_row.answer_guide   if question_row else ''
        watch = mistakes[0] if mistakes else ''
        inst = (
            f"{nav['frame']} {nav['task'].upper()}: Give {name} this scenario: '{q}'\n"
            f"[Internal only — never say aloud: ideal response={hint}, watch for={watch}]\n"
            f"If STRONG response: name exactly what worked ('{nav['correct']}'), "
            f"then: 'Let us try another {nav['task']}.'\n"
            f"If WEAK response: SOFT-STOP only. One {nav['hint']}. Do NOT give the script."
        )

    elif phase == 'you_do':
        q = question_row.question_text if question_row else 'a scenario on today\'s topic'
        inst = (
            f"SOLO {nav['task'].upper()}: Tell {name} this is an uncoached rep — "
            f"frame it as the real test of the {nav['frame']}. "
            f"Scenario: '{q}'. Wait. No help unless they ask."
        )

    elif phase == 'bonus':
        topic_name = topic.topic_name if hasattr(topic, 'topic_name') else topic.get('topic', '')
        inst = (
            f"ADVANCED SCENARIO: {name} has earned a harder challenge. "
            f"Introduce a high-pressure or ambiguous angle of '{topic_name}' — "
            f"multi-stakeholder, price-sensitive, or near-loss scenario. "
            f"One deepening question. Make it feel like a real stretch."
        )

    elif phase == 'debrief':
        topic_name = topic.topic_name if hasattr(topic, 'topic_name') else topic.get('topic', '')
        inst = (
            f"SESSION DEBRIEF: Tell {name} ONE specific skill they demonstrated well — "
            f"precise, not vague. Then give ONE clear action item they can use in a real {nav['task']} this week. "
            f"Two sentences maximum. Make the close feel earned."
        )

    elif phase == 'returning':
        topic_name = topic.topic_name if hasattr(topic, 'topic_name') else (
            topic.get('topic', '') if topic else '')
        prev      = last_context.get('unit_name', topic_name) if last_context else topic_name
        struggled = last_context.get('struggled_with', '')    if last_context else ''
        streak    = child.current_streak or 1
        streak_msg = f" {streak} sessions in — you are building real momentum." if streak > 1 else ""
        note = f" Last time we were working on {struggled} together." if struggled else ""
        inst = (
            f"Reopen the {nav['frame']} — welcome {name} back.{streak_msg}"
            f" We were on {prev}.{note}"
            f" Tell {name} you are ready to push further today. ONE question to re-engage."
        )

    else:
        inst = f"Respond professionally to {name}. Under 60 words."

    return char + "\n\n" + inst
