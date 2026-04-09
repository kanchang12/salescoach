"""
TrueSkills — Love2Learn AI Tutoring Platform
========================================================
Adaptive AI tutor for neurodivergent children, powered by Gemini.


A TrueSkills product — trueskills.ai
"""

import os, json, uuid, random
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from sqlalchemy.orm.attributes import flag_modified
from flask_sock import Sock
from datetime import datetime, timezone

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'trueskills-l2l-2026')
sock = Sock(app)

# ================================================================
# DATABASE SETUP — PostgreSQL
# ================================================================

from models import db, init_db, Admin
init_db(app)



# ================================================================
# LLM BACKEND — Google Gemini via GenAI SDK
# ================================================================

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')


gemini_client = None
LLM_BACKEND = None

if GOOGLE_API_KEY:
    try:
        from google import genai
        gemini_client = genai.Client(api_key=GOOGLE_API_KEY)
        LLM_BACKEND = 'gemini'
        print(f"[LLM] Gemini configured: {GEMINI_MODEL}")
    except Exception as e:
        print(f"[LLM] Gemini setup failed: {e}")

if not LLM_BACKEND:
    print("[LLM] WARNING: No Gemini API key configured. Fallback mode only.")



# ================================================================
# UNIFIED LLM CALLER — Works with either backend
# ================================================================

def call_ai(system_prompt, user_message, max_tokens=540, temperature=0.7):
    """Call Gemini. Returns text."""
    if not gemini_client:
        return None
    try:
        from google.genai import types
        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                max_output_tokens=max_tokens,
                temperature=temperature,
            ),
        )
        return response.text
    except Exception as e:
        print(f"[GEMINI] Error: {e}")
        return None


def call_ai_long(system_prompt, user_message):
    return call_ai(system_prompt, user_message, max_tokens=540, temperature=0.7)


def call_ai_chat(system_prompt, history, user_message):
    """Call Gemini. Last 10 messages only — keeps token cost flat."""
    if not gemini_client:
        return None
    try:
        from google.genai import types
        contents = []
        for m in history[-10:]:   # last 10 only
            role = "user" if m['role'] == 'user' else "model"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m['text'])]))
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=user_message)]))
        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                max_output_tokens=540,
                temperature=0.7,
            ),
        )
        return response.text
    except Exception as e:
        print(f"[GEMINI_CHAT] Error: {e}")
        return None





# ================================================================


# LOVE2LEARN ROUTES — appended to original app.py
# TrueSkills Love2Learn routes
# ================================================================

import hashlib, hmac as _hmac
from datetime import date, timedelta
from models import (Parent, Child, LearningSession, DiamondTransaction,
                    AbsenceRecord, DiamondGoal, DailyProgress, BetaFeedback,
                    Curriculum, ChildCoverage)
import sales_curriculum as curriculum_module

def _hash_pw(password, salt=None):
    if not salt: salt = uuid.uuid4().hex
    h = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 310000)
    return h.hex(), salt

def _verify_pw(password, stored, salt):
    h, _ = _hash_pw(password, salt)
    return _hmac.compare_digest(h, stored)

DIAMOND_RULES = {
    'login_streak':        {'amount':2,  'desc':'+2'},
    'active_30_mins':      {'amount':5,  'desc':'+5'},
    'question_asked':      {'amount':1,  'desc':'+1'},
    'restart_after_fail':  {'amount':3,  'desc':'+3'},
    'problem_solved':      {'amount':5,  'desc':'+5'},
    'honest_absence':      {'amount':3,  'desc':'+3'},
    'showed_up_anyway':    {'amount':5,  'desc':'+5'},
    'story_day_showed_up': {'amount':2,  'desc':'+2'},
    '7_day_streak_bonus':  {'amount':10, 'desc':'+10'},
    'disrespect_deduction':{'amount':-2, 'desc':'-2'},
}

def award_diamonds(child_id, reason, session_id=None):
    rule = DIAMOND_RULES.get(reason)
    if not rule: return None
    child = Child.query.get(child_id)
    if not child: return None
    new_bal = max(0, child.diamond_balance + rule['amount'])
    actual  = new_bal - child.diamond_balance
    child.diamond_balance = new_bal
    if actual > 0: child.total_diamonds_earned += actual
    tx = DiamondTransaction(child_id=child_id, session_id=session_id,
                            amount=actual, balance_after=new_bal,
                            reason=reason, description=rule['desc'])
    db.session.add(tx)
    db.session.commit()
    return {'amount':actual,'balance':new_bal,'description':rule['desc'],'reason':reason}

def update_streak(child):
    today = date.today(); last = child.last_login_date; awards = []
    if last is None:
        child.current_streak = 1; child.last_login_date = today
    elif last == today:
        pass
    elif last == today - timedelta(days=1):
        child.current_streak += 1; child.last_login_date = today
        tx = award_diamonds(child.id, 'login_streak')
        if tx: awards.append(tx)
        if child.current_streak % 7 == 0:
            tx = award_diamonds(child.id, '7_day_streak_bonus')
            if tx: awards.append(tx)
    else:
        child.current_streak = 1; child.last_login_date = today
    if child.current_streak > child.longest_streak:
        child.longest_streak = child.current_streak
    child.last_active = datetime.now(timezone.utc)
    db.session.commit()
    return awards

def check_login_time(child):
    if not child.preferred_login_time: return 'on_time'
    now = datetime.now(timezone.utc).time()
    pref = child.preferred_login_time.hour*60 + child.preferred_login_time.minute
    cur  = now.hour*60 + now.minute
    diff = cur - pref
    if -30 <= diff <= 30: return 'on_time'
    return 'late' if diff > 30 else 'early'

def check_missed_login(child):
    if not child.preferred_login_time or not child.last_login_date: return False
    return child.last_login_date < date.today() - timedelta(days=1)

def _diamond_safe(t):
    """Parent-facing diamond dict — amount and date only, never the reason code."""
    return {
        'amount':      t.amount,
        'balance_after': t.balance_after,
        'created_at':  t.created_at.isoformat() if t.created_at else '',
    }



def get_or_create_ls(child):
    ex = (LearningSession.query.filter_by(child_id=child.id, status='in_progress')
          .order_by(LearningSession.started_at.desc()).first())
    if ex: return ex, False
    sid = str(uuid.uuid4())[:12]
    ls  = LearningSession(session_id=sid, child_id=child.id,
                          year_group=child.year_group,
                          interest_context=(child.interests or {}).get('primary'))
    db.session.add(ls); db.session.commit()
    return ls, True

def dashboard_required(f):
    """Extra password gate for parent dashboard — child cannot walk in."""
    from functools import wraps
    @wraps(f)
    def d(*a, **k):
        if 'parent_email' not in session:
            return redirect(url_for('l2l_login'))
        if not session.get('dashboard_unlocked'):
            return redirect(url_for('l2l_dashboard_login'))
        return f(*a, **k)
    return d

def parent_required(f):
    from functools import wraps
    @wraps(f)
    def d(*a,**k):
        if 'parent_email' not in session: return redirect(url_for('l2l_login'))
        p = Parent.query.filter_by(email=session['parent_email']).first()
        if not p or not p.can_access(): return redirect(url_for('l2l_sub_required'))
        return f(*a,**k)
    return d

def child_required(f):
    from functools import wraps
    @wraps(f)
    def d(*a,**k):
        if 'child_id' not in session: return redirect(url_for('l2l_child_select'))
        return f(*a,**k)
    return d

# ── AUTH ─────────────────────────────────────────────────────────
@app.route('/login', methods=['GET','POST'])
def l2l_login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower()
        pw    = request.form.get('password','')
        p     = Parent.query.filter_by(email=email, is_active=True).first()
        if p and _verify_pw(pw, p.password_hash, p.salt):
            session['parent_email'] = email
            session['parent_name']  = p.name
            p.last_login = datetime.now(timezone.utc); db.session.commit()
            return redirect(url_for('l2l_child_select'))
        error = "Email or password not recognised."
    return render_template('l2l/login.html', error=error)

@app.route('/register', methods=['GET','POST'])
def l2l_register():
    error = None
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower()
        name  = request.form.get('name','').strip()
        pw    = request.form.get('password','')
        gdpr  = request.form.get('gdpr_consent') == 'on'
        if not gdpr: error = "You must agree to the privacy policy."
        elif len(pw) < 8: error = "Password must be at least 8 characters."
        elif Parent.query.filter_by(email=email).first(): error = "Account already exists."
        else:
            h,s = _hash_pw(pw); now = datetime.now(timezone.utc)
            p = Parent(email=email, name=name, password_hash=h, salt=s,
                       plan='trial', trial_started_at=now,
                       trial_ends_at=datetime(2026, 4, 15, 23, 59, 59, tzinfo=timezone.utc),
                       gdpr_consent=True, gdpr_consent_at=now)
            db.session.add(p); db.session.commit()
            session['parent_email'] = email; session['parent_name'] = name
            return redirect(url_for('l2l_add_child'))
    return render_template('l2l/register.html', error=error)

@app.route('/logout', methods=['GET','POST'])
def l2l_logout():
    session.pop('parent_email',None); session.pop('child_id',None)
    return redirect(url_for('l2l_login'))

@app.route('/subscription-required', methods=['GET','POST'])
def l2l_sub_required():
    p = Parent.query.filter_by(email=session.get('parent_email','')).first()
    return render_template('l2l/subscription_required.html', parent=p)

# ── CHILD SETUP ───────────────────────────────────────────────────
@app.route('/add-child', methods=['GET','POST'])
def l2l_add_child():
    if 'parent_email' not in session: return redirect(url_for('l2l_login'))
    error = None
    if request.method == 'POST':
        fn = request.form.get('first_name','').strip()
        yg = request.form.get('year_group','').strip()
        pi = request.form.get('primary_interest','').strip()
        si = request.form.get('secondary_interest','').strip()
        if not fn or yg not in ('junior','mid','senior'):
            error = "Please fill in all fields."
        else:
            c = Child(parent_email=session['parent_email'], first_name=fn,
                      year_group=yg, interests={'primary':pi or 'stories','secondary':si})
            db.session.add(c); db.session.commit()
            return redirect(url_for('l2l_child_select'))
    return render_template('l2l/add_child.html', error=error)

@app.route('/select-child', methods=['GET','POST'])
def l2l_child_select():
    if 'parent_email' not in session: return redirect(url_for('l2l_login'))
    children = Child.query.filter_by(parent_email=session['parent_email']).all()
    return render_template('l2l/child_select.html', children=children)

@app.route('/select-child/<int:child_id>', methods=['GET','POST'])
def l2l_select_child(child_id):
    if 'parent_email' not in session: return redirect(url_for('l2l_login'))
    child = Child.query.filter_by(id=child_id, parent_email=session['parent_email']).first_or_404()
    session['child_id'] = child.id; session['child_name'] = child.first_name
    if not child.preferred_login_time:
        return redirect(url_for('l2l_set_time'))
    if check_missed_login(child):
        yesterday = date.today() - timedelta(days=1)
        return redirect(url_for('l2l_absence', absent_date=yesterday.isoformat()))
    session['streak_awards']     = update_streak(child)
    session['login_time_status'] = check_login_time(child)
    return redirect(url_for('l2l_child_home'))

@app.route('/set-time', methods=['GET','POST'])
@child_required
def l2l_set_time():
    child = Child.query.get(session['child_id']); error = None
    if request.method == 'POST':
        try:
            from datetime import time as dtime
            parts = request.form.get('login_time','').split(':')
            child.preferred_login_time = dtime(int(parts[0]),int(parts[1]))
            db.session.commit()
            session['streak_awards']     = update_streak(child)
            session['login_time_status'] = 'on_time'
            session['first_time_setup']  = True
            return redirect(url_for('l2l_child_home'))
        except: error = "Please pick a valid time."
    return render_template('l2l/set_login_time.html', child=child, error=error)

@app.route('/absence/<absent_date>', methods=['GET','POST'])
@child_required
def l2l_absence(absent_date):
    child = Child.query.get(session['child_id'])
    if request.method == 'POST':
        reason = request.form.get('reason','').strip()
        try: d = date.fromisoformat(absent_date)
        except: d = date.today() - timedelta(days=1)
        assessment = 'honest_valid'
        if reason and 'didn' in reason.lower() and 'want' in reason.lower():
            assessment = 'showed_up_anyway'
        elif not reason: assessment = 'no_reason'
        dm = {'honest_valid':('honest_absence','Honest answer 💎'),
              'showed_up_anyway':('showed_up_anyway',"You came anyway 💎💎"),
              'no_reason':(None,"No worries. Let us get started.")}
        rk, msg = dm[assessment]; diamonds = 0
        if rk:
            tx = award_diamonds(child.id, rk)
            if tx: diamonds = tx['amount']
        rec = AbsenceRecord(child_id=child.id, absent_date=d, reason_given=reason,
                            assessment=assessment, diamonds_awarded=diamonds,
                            responded_at=datetime.now(timezone.utc))
        db.session.add(rec); db.session.commit()
        session['absence_result'] = {'message':msg,'diamonds_awarded':diamonds}
        session['streak_awards']     = update_streak(child)
        session['login_time_status'] = check_login_time(child)
        return redirect(url_for('l2l_child_home'))
    return render_template('l2l/explain_absence.html', child=child, absent_date=absent_date)

# ── CHILD HOME ────────────────────────────────────────────────────
@app.route('/home', methods=['GET','POST'])
@child_required
def l2l_child_home():
    child  = Child.query.get(session['child_id'])
    parent = Parent.query.filter_by(email=session.get('parent_email','')).first()
    if parent and not parent.can_access(): return redirect(url_for('l2l_sub_required'))
    streak_awards     = session.pop('streak_awards', [])
    absence_result    = session.pop('absence_result', None)
    login_time_status = session.pop('login_time_status', 'on_time')
    first_time_setup  = session.pop('first_time_setup', False)
    recent_txs = (DiamondTransaction.query.filter_by(child_id=child.id)
                  .order_by(DiamondTransaction.created_at.desc()).limit(5).all())
    goal = (DiamondGoal.query.filter_by(child_id=child.id, is_active=True)
            .order_by(DiamondGoal.created_at.desc()).first())
    ptime = child.preferred_login_time.strftime('%H:%M') if child.preferred_login_time else None
    return render_template('l2l/child_home.html', child=child,
                           streak_awards=streak_awards, absence_result=absence_result,
                           login_time_status=login_time_status, first_time_setup=first_time_setup,
                           preferred_time_display=ptime,
                           recent_diamonds=[t.to_dict() for t in recent_txs],
                           diamond_goal=goal)

@app.route('/start', methods=['GET','POST'])
@child_required
def l2l_start():
    import leo as leo_module
    child      = Child.query.get(session['child_id'])
    ls, is_new = get_or_create_ls(child)
    year_group = child.year_group or 'junior'
    interest   = (child.interests or {}).get('primary', 'default')

    # ── Decide what to teach — query DB for full picture ─────────
    subj, unit_id, teach_reason = _decide_what_to_teach(child, year_group)
    ls.session_type   = subj
    ls.leo_current_unit = unit_id

    unit = curriculum_module.get_topic_by_id(unit_id) if unit_id else None
    if unit:
        ls.unit_id   = unit['id']
        ls.unit_name = unit['topic']

    # Store the reason so Leo can mention it in returning/i_do phase
    if teach_reason:
        session['teach_reason'] = teach_reason

    # ── If returning child, skip rapport ─────────────────────────
    has_sessions = LearningSession.query.filter(
        LearningSession.child_id == child.id,
        LearningSession.session_id != ls.session_id
    ).count() > 0
    if has_sessions and not ls.leo_rapport_done:
        ls.leo_rapport_done = True
        ls.leo_phase        = 'returning'

    # ── Pre-generate question bank ───────────────────────────────
    if unit_id:
        leo_module.ensure_question_bank(
            unit_id=unit_id, subject=subj, year_group=year_group,
            interest=interest, gemini_client=gemini_client, model=GEMINI_MODEL,
        )

    session['ls_id'] = ls.session_id
    db.session.commit()
    return redirect(url_for('l2l_room'))


def _decide_what_to_teach(child, year_group):
    """
    Decide which sales skill track and topic to teach today.
    Uses sales_curriculum.py directly — no DB Curriculum table needed.
    """
    SALES_TRACKS = ['prospecting','discovery','presentation','objection_handling',
                    'closing','negotiation','account_management','sales_mindset']

    coverage  = ChildCoverage.query.filter_by(child_id=child.id).all()
    covered   = [c.unit_id for c in coverage]
    struggled = {c.unit_id: c.struggle_count for c in coverage if c.struggle_count > 0}
    total_sessions = LearningSession.query.filter_by(child_id=child.id).count()

    # Priority 1: Revisit struggled topic
    if struggled and total_sessions >= 3:
        recent_units = [s.unit_id for s in
                       LearningSession.query.filter_by(child_id=child.id)
                       .order_by(LearningSession.started_at.desc()).limit(2).all()]
        for unit_id in sorted(struggled, key=lambda x: -struggled[x]):
            if unit_id not in recent_units:
                topic = curriculum_module.get_topic_by_id(unit_id)
                if topic:
                    for track in SALES_TRACKS:
                        if unit_id in curriculum_module.get_track_topics(track):
                            return track, unit_id, f"Last time we looked at {topic['topic']}. Let us sharpen that up."

    # Priority 2: Continue current track
    last_session = (LearningSession.query.filter_by(child_id=child.id)
                    .order_by(LearningSession.started_at.desc()).first())
    current_track = last_session.session_type if last_session else 'prospecting'
    if current_track not in SALES_TRACKS:
        current_track = 'prospecting'

    next_topic = curriculum_module.get_next_topic(year_group, current_track, covered)
    if next_topic:
        return current_track, next_topic['id'], None

    # Priority 3: Move to next track with uncovered topics
    for track in SALES_TRACKS:
        next_topic = curriculum_module.get_next_topic(year_group, track, covered)
        if next_topic:
            return track, next_topic['id'], f"Let us move on to {track.replace('_',' ')} today."

    # All covered — restart from prospecting
    first = curriculum_module.get_next_topic(year_group, 'prospecting', [])
    if first:
        return 'prospecting', first['id'], "You have covered everything once. Let us go deeper."
    return 'prospecting', None, "all_covered"


# ================================================================
# ── LEARNING ROOM ────────────────────────────────────────────────
# ================================================================

@app.route('/room', methods=['GET','POST'])
@child_required
def l2l_room():
    child = Child.query.get(session['child_id'])
    ls    = LearningSession.query.filter_by(
        session_id=session.get('ls_id')).first()
    if not ls:
        return redirect(url_for('l2l_child_home'))
    return render_template('l2l/learning_room.html',
                           child=child,
                           learning_session=ls,
                           chat_history=ls.chat_log or [],
                           diamond_balance=child.diamond_balance)


# ================================================================
# ── CHAT ─────────────────────────────────────────────────────────
# ================================================================

@app.route('/chat', methods=['GET','POST'])
@child_required
def l2l_chat():
    import leo as leo_module
    from sqlalchemy.orm.attributes import flag_modified

    child = Child.query.get(session['child_id'])
    data  = request.get_json() or {}
    msg   = data.get('message', '').strip()

    # ── Robust session lookup ────────────────────────────────────
    ls = LearningSession.query.filter_by(
        session_id=session.get('ls_id')).first()
    if not ls:
        ls = (LearningSession.query
              .filter_by(child_id=child.id, status='in_progress')
              .order_by(LearningSession.started_at.desc()).first())
        if ls:
            session['ls_id'] = ls.session_id

    if not msg or not ls:
        return jsonify({'reply': 'I lost my place for a second. Please refresh!'}), 200

    diamond_events = []

    # ── Subject safety ───────────────────────────────────────────
    subject = ls.session_type if ls.session_type in {'prospecting','discovery','presentation','objection_handling','closing','negotiation','account_management','sales_mindset'} else 'prospecting'
    if ls.session_type != subject:
        ls.session_type = subject

    year_group = ls.year_group or child.year_group or 'junior'
    interest   = (child.interests or {}).get('primary', 'default')
    chat_log   = list(ls.chat_log or [])
    covered    = list(ChildCoverage.query.filter_by(child_id=child.id)
                      .with_entities(ChildCoverage.unit_id).all())
    covered    = [r[0] for r in covered]

    # ── Disrespect filter ────────────────────────────────────────
    rude = ['idiot','stupid','hate','shut up','dumb','useless']
    if any(w in msg.lower() for w in rude):
        tx = award_diamonds(child.id, 'disrespect_deduction', ls.session_id)
        if tx: diamond_events.append(tx)
        reply = "That wasn't kind. Let us get back on track."
        chat_log.append({'role':'agent', 'text':reply, 'ts':datetime.now(timezone.utc).isoformat()})
        ls.chat_log = chat_log
        flag_modified(ls, 'chat_log')
        db.session.commit()
        return jsonify({'reply':reply, 'diamond_events':diamond_events,
                        'diamond_balance':child.diamond_balance})

    # ── Subject switch — child asks Leo to teach something else ─────
    SUBJECT_WORDS = {
        'prospecting':        ['prospecting','cold call','outreach','leads','pipeline','icp','qualify'],
        'discovery':          ['discovery','needs','questions','spin','stakeholder'],
        'presentation':       ['presentation','demo','value prop','proposal','pitch'],
        'objection_handling': ['objection','objections','pushback','price','too expensive','competitor'],
        'closing':            ['closing','close','commitment','next step','sign off'],
        'negotiation':        ['negotiation','negotiate','terms','discount','anchor'],
        'account_management': ['account','qbr','upsell','expansion','churn','renewal'],
        'sales_mindset':      ['mindset','resilience','rejection','discipline','habits'],
    }
    msg_lower = msg.lower()
    for req_subj, keywords in SUBJECT_WORDS.items():
        if any(kw in msg_lower for kw in keywords) and req_subj != subject:
            # Child wants to switch — Leo switches immediately this turn
            ls.session_type = req_subj
            ls.leo_current_unit   = None
            ls.leo_phase          = 'i_do'
            ls.leo_msgs_in_phase  = 0
            ls.leo_we_do_attempts = 0
            ls.leo_question_idx   = 0
            subject = req_subj
            # Find first uncovered unit in requested subject
            new_topic = curriculum_module.get_next_topic(year_group, req_subj, covered)
            if new_topic:
                ls.leo_current_unit = new_topic['id']
                ls.unit_id   = new_topic['id']
                ls.unit_name = new_topic['topic']
                leo_module.ensure_question_bank(
                    new_topic['id'], req_subj, year_group,
                    interest, gemini_client, GEMINI_MODEL)
            # Also update teach_reason so Leo knows why this subject was chosen
            session['teach_reason'] = f"{child.first_name} asked to switch to {req_subj.replace('_',' ')}"
            break

    # ── Effort signals ───────────────────────────────────────────
    if '?' in msg and len(msg.strip()) > 5:
        ls.child_questions  = (ls.child_questions or 0) + 1
        ls.questions_asked  = (ls.questions_asked or 0) + 1
        tx = award_diamonds(child.id, 'question_asked', ls.session_id)
        if tx: diamond_events.append(tx)

    if any(kw in msg.lower() for kw in ['try again','start again','once more']):
        ls.restarts = (ls.restarts or 0) + 1
        tx = award_diamonds(child.id, 'restart_after_fail', ls.session_id)
        if tx: diamond_events.append(tx)

    # ── Get current phase ────────────────────────────────────────
    if ls.leo_phase == 'done':
        # Unit just completed — move to next unit's i_do
        covered_now = ls.leo_concepts_covered or []
        next_t = curriculum_module.get_next_topic(
            ls.year_group or 'junior', subject, covered_now)
        if next_t:
            ls.leo_current_unit   = next_t['id']
            ls.unit_id            = next_t['id']
            ls.unit_name          = next_t['topic']
            interest_now = (child.interests or {}).get('primary', 'default')
            leo_module.ensure_question_bank(
                next_t['id'], subject, ls.year_group or 'junior',
                interest_now, gemini_client, GEMINI_MODEL)
        ls.leo_phase          = 'i_do'
        ls.leo_msgs_in_phase  = 0
        ls.leo_we_do_attempts = 0
        ls.leo_question_idx   = 0

    phase = ls.leo_phase or 'rapport'

    # ── Get current topic from sales_curriculum ──────────────────
    topic = curriculum_module.get_topic_by_id(ls.leo_current_unit) if ls.leo_current_unit else None
    if not topic:
        next_t = curriculum_module.get_next_topic(year_group, subject, covered)
        if next_t:
            topic = next_t
            ls.leo_current_unit = topic['id']
            ls.unit_id   = topic['id']
            ls.unit_name = topic['topic']
            leo_module.ensure_question_bank(
                topic['id'], subject, year_group, interest,
                gemini_client, GEMINI_MODEL)

    if not topic:
        # Restart from first prospecting topic
        topic = curriculum_module.get_next_topic(year_group, 'prospecting', [])
        if topic:
            ls.leo_current_unit = topic['id']
            ls.unit_id   = topic['id']
            ls.unit_name = topic['topic']
            ls.session_type = 'prospecting'
            subject = 'prospecting'

    # ── Get question from bank (we_do and you_do phases) ─────────
    question_row = None
    if phase in ('we_do', 'you_do'):
        question_row = leo_module.get_next_question(
            ls.leo_current_unit, phase, ls.leo_question_idx or 0)

    # ── Get last 5-session context — passed into EVERY prompt so Leo knows the child's level ──
    last_ctx = leo_module.get_last_context(child.id)

    # ── Story mode — if child is clearly struggling, Leo takes a break ──
    story_mode = False
    if phase == 'we_do' and leo_module.detect_struggle(chat_log):
        story_mode = True

    # ── Build minimal prompt ──────────────────────────────────────
    ls.phase_reached = phase
    system_prompt = leo_module.build_prompt(child, topic, phase, question_row, last_ctx, story_mode)

    # ── Call AI with full history ─────────────────────────────────
    reply = call_ai_chat(system_prompt, chat_log, msg)
    if not reply:
        reply = f"Can you say that again {child.first_name}?"

    # ── Advance phase ─────────────────────────────────────────────
    ls.leo_msgs_in_phase = (ls.leo_msgs_in_phase or 0) + 1
    if phase == 'we_do':
        ls.leo_we_do_attempts = (ls.leo_we_do_attempts or 0) + 1
        ls.leo_question_idx   = (ls.leo_question_idx or 0) + 1

    if leo_module.should_advance(phase, ls.leo_msgs_in_phase, ls.leo_we_do_attempts or 0):
        new_phase = leo_module.next_phase(phase)
        ls.leo_phase         = new_phase
        ls.leo_msgs_in_phase = 0

        if phase == 'rapport':
            ls.leo_rapport_done = True
            # Detect and save child's interest from rapport conversation
            if not (child.interests or {}).get('primary'):
                for m in chat_log:
                    if m.get('role') == 'user':
                        detected = leo_module.detect_interest(m.get('text', ''))
                        if detected:
                            child.interests = {'primary': detected,
                                               'secondary': (child.interests or {}).get('secondary', '')}
                            db.session.add(child)
                            break

        if new_phase == 'you_do':
            ls.leo_question_idx = 0

        # ── Bonus Level: if you_do done but < 20 mins, run bonus before homework ──
        if new_phase == 'bonus' and (ls.active_minutes or 0) >= 20:
            # Enough time spent — skip bonus, go straight to homework
            new_phase             = 'homework'
            ls.leo_phase          = 'homework'
            ls.leo_msgs_in_phase  = 0

        # ── 30-min gate: homework only after 30 mins ──────────────
        # If bonus/you_do complete but not enough time, move to next unit
        if new_phase == 'homework' and (ls.active_minutes or 0) < 30:
            new_phase              = 'done'
            ls.leo_phase          = 'done'
            ls.leo_msgs_in_phase  = 0
            ls.leo_we_do_attempts = 0
            ls.leo_question_idx   = 0

        if new_phase == 'done':
            # ── Update ChildCoverage table ───────────────────────
            existing_cov = ChildCoverage.query.filter_by(
                child_id=child.id, unit_id=topic.unit_id).first()
            if existing_cov:
                existing_cov.times_practiced += 1
                existing_cov.last_practiced   = datetime.now(timezone.utc)
                existing_cov.mastery_level    = 'mastered' if existing_cov.times_practiced >= 2 else 'practiced'
            else:
                db.session.add(ChildCoverage(
                    child_id=child.id, unit_id=topic.unit_id,
                    subject=topic.subject, year_group=topic.year_group,
                    mastery_level='practiced',
                ))
            covered = [r[0] for r in
                       ChildCoverage.query.filter_by(child_id=child.id)
                       .with_entities(ChildCoverage.unit_id).all()]

            # ── Accuracy tracking ────────────────────────────────
            diff = topic.difficulty
            if diff == 1:
                ls.correct_easy   = (ls.correct_easy or 0) + 1
                ls.attempted_easy = (ls.attempted_easy or 0) + 1
            elif diff == 2:
                ls.correct_medium   = (ls.correct_medium or 0) + 1
                ls.attempted_medium = (ls.attempted_medium or 0) + 1
            else:
                ls.correct_hard   = (ls.correct_hard or 0) + 1
                ls.attempted_hard = (ls.attempted_hard or 0) + 1
            tx = award_diamonds(child.id, 'problem_solved', ls.session_id)
            if tx: diamond_events.append(tx)

            leo_module.write_session_summary(ls, child, gemini_client, GEMINI_MODEL)

            # ── Next unit from sales_curriculum ──────────────────
            covered_now = ls.leo_concepts_covered or []
            next_unit = curriculum_module.get_next_topic(year_group, subject, covered_now)
            if next_unit:
                ls.leo_current_unit   = next_unit['id']
                ls.leo_phase          = 'i_do'
                ls.leo_msgs_in_phase  = 0
                ls.leo_we_do_attempts = 0
                ls.leo_question_idx   = 0
                ls.unit_id            = next_unit['id']
                ls.unit_name          = next_unit['topic']
                leo_module.ensure_question_bank(
                    next_unit['id'], subject, year_group, interest,
                    gemini_client, GEMINI_MODEL)

    # ── Track struggle in ChildCoverage ──────────────────────────
    if phase == 'we_do' and ls.leo_we_do_attempts and ls.leo_we_do_attempts % 3 == 0:
        cov = ChildCoverage.query.filter_by(child_id=child.id, unit_id=topic.get('id','') if isinstance(topic,dict) else getattr(topic,'unit_id','')).first()
        if cov:
            cov.struggle_count += 1
        elif isinstance(topic,dict) and topic.get('id'):
            db.session.add(ChildCoverage(child_id=child.id,unit_id=topic.unit_id,
                subject=topic.subject,year_group=topic.year_group,struggle_count=1,mastery_level='learning'))

    # ── Track homework ────────────────────────────────────────────
    if phase == 'homework':
        ls.homework_set = topic['topic']

    # ── Save ──────────────────────────────────────────────────────
    ls.questions_by_leo = (ls.questions_by_leo or 0) + (1 if '?' in reply else 0)
    ls.last_saved_at    = datetime.now(timezone.utc)
    _save_chat(ls, msg, reply, chat_log)

    return jsonify({
        'reply':           reply,
        'diamond_events':  diamond_events,
        'diamond_balance': child.diamond_balance,
        'phase':           ls.leo_phase or 'rapport',
        'active_minutes':  ls.active_minutes or 0,
    })


def _save_chat(ls, user_msg, agent_reply, chat_log):
    from sqlalchemy.orm.attributes import flag_modified
    chat_log.append({'role':'user',  'text':user_msg,    'ts':datetime.now(timezone.utc).isoformat()})
    chat_log.append({'role':'agent', 'text':agent_reply, 'ts':datetime.now(timezone.utc).isoformat()})
    ls.chat_log = chat_log
    flag_modified(ls, 'chat_log')
    db.session.commit()


# ================================================================
# ── VOICE ────────────────────────────────────────────────────────
# ================================================================

@app.route('/voice-text', methods=['GET','POST'])
@child_required
def voice_text():
    import base64
    child     = Child.query.get(session['child_id'])
    data      = request.get_json(silent=True) or request.form or {}
    audio_b64 = data.get('audio', '')
    if not audio_b64:
        return jsonify({'error': 'No audio'}), 400

    # Transcribe via OpenAI Whisper (fastest available)
    transcript = None
    try:
        import requests as req_lib
        audio_bytes = base64.b64decode(audio_b64)
        if OPENAI_API_KEY:
            r = req_lib.post(
                'https://api.openai.com/v1/audio/transcriptions',
                headers={'Authorization': f'Bearer {OPENAI_API_KEY}'},
                files={'file': ('audio.webm', audio_bytes, 'audio/webm')},
                data={'model': 'whisper-1', 'language': 'en'},
                timeout=10,
            )
            if r.status_code == 200:
                transcript = r.json().get('text', '').strip()
            else:
                print(f'[WHISPER] {r.status_code} {r.text[:100]}')
        if not transcript and gemini_client:
            # Fallback to Gemini if no OpenAI key
            from google.genai import types as gtypes
            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[gtypes.Content(parts=[
                    gtypes.Part(inline_data=gtypes.Blob(
                        mime_type='audio/webm', data=audio_bytes)),
                    gtypes.Part(text='Transcribe exactly what is said. Return only the spoken words.'),
                ])],
                config=gtypes.GenerateContentConfig(max_output_tokens=540, temperature=0.0),
            )
            transcript = response.text.strip() if response.text else None
    except Exception as e:
        print(f'[TRANSCRIBE] {e}')

    if not transcript:
        return jsonify({'error': 'Could not understand. Try typing instead.'}), 200

    # Run through same chat logic directly
    import leo as leo_module
    from sqlalchemy.orm.attributes import flag_modified

    ls = LearningSession.query.filter_by(session_id=session.get('ls_id')).first()
    if not ls:
        ls = (LearningSession.query
              .filter_by(child_id=child.id, status='in_progress')
              .order_by(LearningSession.started_at.desc()).first())
        if ls:
            session['ls_id'] = ls.session_id
    if not ls:
        return jsonify({'transcript': transcript, 'error': 'No session. Please refresh.'}), 200

    diamond_events = []
    subject    = ls.session_type if ls.session_type in {'prospecting','discovery','presentation','objection_handling','closing','negotiation','account_management','sales_mindset'} else 'prospecting'
    year_group = ls.year_group or child.year_group or 'junior'
    interest   = (child.interests or {}).get('primary', 'default')
    chat_log   = list(ls.chat_log or [])
    covered    = ls.leo_concepts_covered or []

    rude = ['idiot','stupid','hate','shut up','dumb','useless']
    if any(w in transcript.lower() for w in rude):
        tx = award_diamonds(child.id, 'disrespect_deduction', ls.session_id)
        if tx: diamond_events.append(tx)
        reply = "That wasn't kind. Let us get back on track."
        _save_chat(ls, transcript, reply, chat_log)
        return jsonify({'transcript': transcript, 'reply': reply,
                        'diamond_events': diamond_events, 'diamond_balance': child.diamond_balance})

    if '?' in transcript and len(transcript.strip()) > 5:
        ls.child_questions = (ls.child_questions or 0) + 1
        ls.questions_asked = (ls.questions_asked or 0) + 1
        tx = award_diamonds(child.id, 'question_asked', ls.session_id)
        if tx: diamond_events.append(tx)

    if ls.leo_phase == 'done':
        ls.leo_phase = 'i_do'; ls.leo_msgs_in_phase = 0
        ls.leo_we_do_attempts = 0; ls.leo_question_idx = 0

    phase      = ls.leo_phase or 'rapport'
    topic      = curriculum_module.get_topic_by_id(ls.leo_current_unit) if ls.leo_current_unit else None
    if not topic:
        topic = curriculum_module.get_next_topic(year_group, subject, covered)
        if topic:
            ls.leo_current_unit = topic['id']
            ls.unit_id = topic['id']; ls.unit_name = topic['topic']
            leo_module.ensure_question_bank(topic['id'], subject, year_group,
                                            interest, gemini_client, GEMINI_MODEL)

    if not topic:
        # Restart from prospecting — never tell the user they are done
        topic = curriculum_module.get_next_topic(year_group, 'prospecting', [])
        if topic:
            ls.leo_current_unit = topic['id']
            ls.unit_id = topic['id']; ls.unit_name = topic['topic']
            ls.session_type = 'prospecting'
            subject = 'prospecting'

    question_row = None
    if phase in ('we_do', 'you_do'):
        question_row = leo_module.get_next_question(
            ls.leo_current_unit, phase, ls.leo_question_idx or 0)

    last_ctx = leo_module.get_last_context(child.id)  # always — Leo needs full history every turn
    ls.phase_reached = phase
    system_prompt = leo_module.build_prompt(child, topic, phase, question_row, last_ctx)
    reply = call_ai_chat(system_prompt, chat_log, transcript)
    if not reply:
        reply = f"Can you say that again {child.first_name}?"

    ls.leo_msgs_in_phase = (ls.leo_msgs_in_phase or 0) + 1
    if phase == 'we_do':
        ls.leo_we_do_attempts = (ls.leo_we_do_attempts or 0) + 1
        ls.leo_question_idx   = (ls.leo_question_idx or 0) + 1

    if leo_module.should_advance(phase, ls.leo_msgs_in_phase, ls.leo_we_do_attempts or 0):
        new_phase = leo_module.next_phase(phase)
        ls.leo_phase = new_phase; ls.leo_msgs_in_phase = 0
        if phase == 'rapport':
            ls.leo_rapport_done = True
            # Detect and save child's interest from rapport conversation
            if not (child.interests or {}).get('primary'):
                for m in chat_log:
                    if m.get('role') == 'user':
                        detected = leo_module.detect_interest(m.get('text', ''))
                        if detected:
                            child.interests = {'primary': detected,
                                               'secondary': (child.interests or {}).get('secondary', '')}
                            db.session.add(child)
                            break
        if new_phase == 'you_do':
            ls.leo_question_idx = 0
        # ── Bonus Level: if you_do done but < 20 mins, trigger bonus ──
        if new_phase == 'bonus' and (ls.active_minutes or 0) >= 20:
            new_phase = 'homework'
            ls.leo_phase = 'homework'; ls.leo_msgs_in_phase = 0
        # ── 30-min gate: homework only after 30 mins ──────────────
        if new_phase == 'homework' and (ls.active_minutes or 0) < 30:
            new_phase = 'done'
            ls.leo_phase = 'done'; ls.leo_msgs_in_phase = 0
            ls.leo_we_do_attempts = 0; ls.leo_question_idx = 0

        if new_phase == 'done':
            if topic['id'] not in covered:
                covered = list(covered) + [topic['id']]
                ls.leo_concepts_covered = covered
                flag_modified(ls, 'leo_concepts_covered')
                tx = award_diamonds(child.id, 'problem_solved', ls.session_id)
                if tx: diamond_events.append(tx)
            leo_module.write_session_summary(ls, child, gemini_client, GEMINI_MODEL)
            next_topic = curriculum_module.get_next_topic(year_group, subject, covered)
            if next_topic:
                ls.leo_current_unit = next_topic['id']
                ls.leo_phase = 'i_do'; ls.leo_msgs_in_phase = 0
                ls.leo_we_do_attempts = 0; ls.leo_question_idx = 0
                ls.unit_id = next_topic['id']; ls.unit_name = next_topic['topic']
                leo_module.ensure_question_bank(next_topic['id'], subject, year_group,
                                                interest, gemini_client, GEMINI_MODEL)

    ls.questions_by_leo = (ls.questions_by_leo or 0) + (1 if '?' in reply else 0)
    ls.last_saved_at = datetime.now(timezone.utc)
    _save_chat(ls, transcript, reply, chat_log)

    return jsonify({'transcript': transcript, 'reply': reply,
                    'diamond_events': diamond_events, 'diamond_balance': child.diamond_balance})


# ================================================================
# ── HEARTBEAT ────────────────────────────────────────────────────
# ================================================================



# ================================================================
# ── HOMEWORK PHOTO ───────────────────────────────────────────────
# Child uploads a photo of their written homework.
# Leo reviews it warmly — asks which question to start with.
# ================================================================

@app.route('/homework', methods=['GET','POST'])
@child_required
def l2l_homework():
    import base64
    from sqlalchemy.orm.attributes import flag_modified

    child     = Child.query.get(session['child_id'])
    data      = request.get_json() or {}
    img_b64   = data.get('image', '')
    if not img_b64:
        return jsonify({'error': 'No image'}), 400

    ls = LearningSession.query.filter_by(session_id=session.get('ls_id')).first()
    if not ls:
        ls = (LearningSession.query
              .filter_by(child_id=child.id, status='in_progress')
              .order_by(LearningSession.started_at.desc()).first())

    reply = f"Let me have a look at that {child.first_name}. Which question do you want to start with?"

    if gemini_client:
        try:
            from google.genai import types as gt
            name     = child.first_name
            interest = (child.interests or {}).get('primary', 'things')
            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[gt.Content(parts=[
                    gt.Part(inline_data=gt.Blob(
                        mime_type='image/jpeg',
                        data=base64.b64decode(img_b64)
                    )),
                    gt.Part(text=f"""This is {name}'s homework on paper.
Look at it warmly. Do NOT give answers.
Ask {name} which question they want to start with.
Say you will work through it together step by step.
Keep it to 2 warm sentences. Be encouraging."""),
                ])],
                config=gt.GenerateContentConfig(
                    max_output_tokens=540, temperature=0.3),
            )
            if response.text:
                reply = response.text.strip()
        except Exception as e:
            print(f"[HOMEWORK] {e}")

    if ls:
        chat_log = list(ls.chat_log or [])
        chat_log.append({'role':'user',  'text':'[Homework photo]', 'ts':datetime.now(timezone.utc).isoformat()})
        chat_log.append({'role':'agent', 'text':reply,              'ts':datetime.now(timezone.utc).isoformat()})
        ls.chat_log = chat_log
        flag_modified(ls, 'chat_log')
        db.session.commit()

    return jsonify({'reply': reply, 'diamond_balance': child.diamond_balance})

@app.route('/heartbeat', methods=['GET','POST'])
@child_required
def l2l_heartbeat():
    child = Child.query.get(session['child_id'])
    ls    = LearningSession.query.filter_by(
        session_id=session.get('ls_id')).first()
    if not ls:
        return jsonify({'ok': False})

    diamond_events    = []
    ls.active_minutes = (ls.active_minutes or 0) + 1

    if ls.active_minutes == 30:
        tx = award_diamonds(child.id, 'active_30_mins', ls.session_id)
        if tx: diamond_events.append(tx)

    today = date.today()
    snap  = DailyProgress.query.filter_by(child_id=child.id, date=today).first()
    if not snap:
        snap = DailyProgress(child_id=child.id, date=today)
        db.session.add(snap)
    snap.active_minutes  = ls.active_minutes
    snap.streak          = child.current_streak
    snap.diamonds_earned = child.diamond_balance

    import leo as leo_module
    proactive = []
    nudge = leo_module.get_proactive_nudge(child, ls, ls.active_minutes)
    if nudge:
        proactive.append({'text': nudge})
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(ls, 'behaviour_flags')

    ls.last_saved_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({
        'ok':               True,
        'active_minutes':   ls.active_minutes,
        'hit_30_min':       ls.active_minutes >= 30,
        'diamond_events':   diamond_events,
        'diamond_balance':  child.diamond_balance,
        'proactive_messages': proactive,
    })


@app.route('/parent/unlock', methods=['GET','POST'])
def l2l_dashboard_login():
    if 'parent_email' not in session:
        return redirect(url_for('l2l_login'))
    parent = Parent.query.filter_by(email=session['parent_email']).first()
    error  = None
    if request.method == 'POST':
        pw = request.form.get('dashboard_password','')
        if not parent.dashboard_password_hash:
            h, s = _hash_pw(pw)
            parent.dashboard_password_hash = h + ':' + s
            db.session.commit()
            session['dashboard_unlocked'] = True
            return redirect(url_for('l2l_parent_home'))
        stored = parent.dashboard_password_hash
        if ':' in stored:
            h_stored, salt = stored.rsplit(':', 1)
            h_check, _ = _hash_pw(pw, salt)
            if _hmac.compare_digest(h_check, h_stored):
                session['dashboard_unlocked'] = True
                return redirect(url_for('l2l_parent_home'))
        error = "Incorrect password."
    first_time = not parent.dashboard_password_hash
    return render_template('l2l/dashboard_login.html', error=error, first_time=first_time, parent=parent)

@app.route('/parent/lock', methods=['GET','POST'])
def l2l_dashboard_lock():
    session.pop('dashboard_unlocked', None)
    return redirect(url_for('l2l_login'))

# ── PARENT ────────────────────────────────────────────────────────
@app.route('/parent', methods=['GET','POST'])
@dashboard_required
def l2l_parent_home():
    parent   = Parent.query.filter_by(email=session['parent_email']).first()
    children = Child.query.filter_by(parent_email=parent.email).all()
    can_view = parent.can_view_dashboard()
    next_sun = None
    if not can_view:
        today = date.today(); days = (6-today.weekday())%7
        next_sun = today + timedelta(days=days or 7)
    goals = {}
    for c in children:
        g = (DiamondGoal.query.filter_by(child_id=c.id, is_active=True)
             .order_by(DiamondGoal.created_at.desc()).first())
        if g: goals[c.id] = g
    return render_template('l2l/parent_home.html', parent=parent, children=children,
                           can_view=can_view, next_sunday=next_sun, active_goals=goals)

@app.route('/parent/set-goal', methods=['GET','POST'])
@dashboard_required
def l2l_set_goal():
    parent   = Parent.query.filter_by(email=session['parent_email']).first()
    child_id = request.form.get('child_id', type=int)
    target   = request.form.get('target_diamonds', type=int)
    treat    = request.form.get('treat_description','').strip()
    if not child_id or not target or not treat: return redirect(url_for('l2l_parent_home'))
    child = Child.query.filter_by(id=child_id, parent_email=parent.email).first()
    if not child: return redirect(url_for('l2l_parent_home'))
    DiamondGoal.query.filter_by(child_id=child_id, is_active=True).update({'is_active':False})
    today  = date.today(); monday = today - timedelta(days=today.weekday())
    goal   = DiamondGoal(child_id=child_id, parent_email=parent.email,
                         target_diamonds=target, treat_description=treat,
                         week_start=monday, week_end=monday+timedelta(days=6),
                         diamonds_at_start=child.diamond_balance)
    db.session.add(goal); db.session.commit()
    return redirect(url_for('l2l_parent_home'))

@app.route('/parent/child/<int:child_id>', methods=['GET','POST'])
@dashboard_required
def l2l_child_detail(child_id):
    import json as _json
    parent = Parent.query.filter_by(email=session['parent_email']).first()
    child  = Child.query.filter_by(id=child_id, parent_email=parent.email).first_or_404()

    # All sessions for trend analysis
    all_sessions = (LearningSession.query.filter_by(child_id=child.id)
                    .order_by(LearningSession.started_at.asc()).all())
    week_ago     = datetime.now(timezone.utc) - timedelta(days=7)
    recent_sessions = [s for s in all_sessions if s.started_at and s.started_at >= week_ago]

    # Trend: attempts per question over time
    attempts_trend = []
    for s in all_sessions[-10:]:
        log = s.attempts_log or []
        if log:
            avg = sum(a.get('attempts',1) for a in log) / len(log)
            attempts_trend.append({'date': s.started_at.strftime('%d/%m') if s.started_at else '', 'avg': round(avg,1)})

    # Trend: child questions per session
    curiosity_trend = [{'date': s.started_at.strftime('%d/%m') if s.started_at else '',
                        'questions': s.child_questions or 0} for s in all_sessions[-10:]]

    # Learning plan — from sales_curriculum
    all_units = []
    for track in ['prospecting','discovery','presentation','objection_handling',
                  'closing','negotiation','account_management','sales_mindset']:
        for t in curriculum_module.get_curriculum(child.year_group or 'junior', track):
            all_units.append({'id': t['id'], 'subject': track, 'unit': t['topic'], 'difficulty': 'standard'})

    # Coverage — from ChildCoverage table (source of truth)
    coverage_rows    = ChildCoverage.query.filter_by(child_id=child.id).all()
    completed_unit_ids = {c.unit_id for c in coverage_rows}
    mastered_unit_ids  = {c.unit_id for c in coverage_rows if c.mastery_level == 'mastered'}
    struggled_unit_ids = {c.unit_id for c in coverage_rows if c.struggle_count > 0}

    # Per-subject breakdown
    subject_stats = {}
    for subj in ['maths','reading','coding']:
        total_in_subj  = sum(1 for u in all_units if u['subject'] == subj)
        done_in_subj   = sum(1 for u in all_units if u['subject'] == subj and u['id'] in completed_unit_ids)
        subject_stats[subj] = {'total': total_in_subj, 'done': done_in_subj,
                               'pct': int(done_in_subj/total_in_subj*100) if total_in_subj else 0}

    # Current unit
    current_unit_id = None
    for s in reversed(all_sessions):
        if s.leo_current_unit:
            current_unit_id = s.leo_current_unit
            break

    # On track calculation
    total_units     = len(all_units)
    completed_count = len(completed_unit_ids)
    weeks_in        = max(1, (date.today() - child.created_at.date()).days // 7) if child.created_at else 1
    expected_by_now = min(total_units, round(total_units / 40 * weeks_in))  # 40 week school year
    if completed_count >= expected_by_now:
        on_track = 'green'
    elif completed_count >= expected_by_now - 2:
        on_track = 'amber'
    else:
        on_track = 'red'

    # Audit trail per session
    audit = []
    for s in reversed(all_sessions[-20:]):
        audit.append({
            'date':           s.started_at.strftime('%a %d %b, %H:%M') if s.started_at else '',
            'subject':        s.session_type or 'maths',
            'unit_name':      s.unit_name or '',
            'phase_reached':  s.phase_reached or '',
            'active_minutes': s.active_minutes or 0,
            'questions_by_leo': s.questions_by_leo or 0,
            'child_questions':  s.child_questions or 0,
            'attempts_log':   s.attempts_log or [],
            'homework_set':   s.homework_set or '',
            'star_rating':    s.star_rating,
            'behaviour_flags':s.behaviour_flags or [],
            'diamonds':       s.diamonds_earned or 0,
        })

    daily = (DailyProgress.query.filter(DailyProgress.child_id==child.id)
             .order_by(DailyProgress.date.asc()).limit(14).all())
    recent_txs = (DiamondTransaction.query.filter_by(child_id=child.id)
                  .order_by(DiamondTransaction.created_at.desc()).limit(20).all())
    # Parent sees amount and date only — _diamond_safe defined at module level

    # Connect plan = transcript access
    can_see_transcript = parent.plan == 'connect'

    fb_done = request.args.get('feedback') == 'done'
    return render_template('l2l/parent_child_detail.html',
                           child=child,
                           parent=parent,
                           recent_sessions=recent_sessions,
                           audit=audit,
                           all_units=all_units,
                           completed_unit_ids=completed_unit_ids,
                           mastered_unit_ids=mastered_unit_ids,
                           struggled_unit_ids=struggled_unit_ids,
                           subject_stats=subject_stats,
                           current_unit_id=current_unit_id,
                           completed_count=completed_count,
                           total_units=total_units,
                           expected_by_now=expected_by_now,
                           on_track=on_track,
                           attempts_trend=_json.dumps(attempts_trend),
                           curiosity_trend=_json.dumps(curiosity_trend),
                           daily_data=_json.dumps([d.to_dict() for d in daily]),
                           recent_diamonds=[t.to_dict() for t in recent_txs],
                           can_see_transcript=can_see_transcript,
                           total_active_mins=sum(s.active_minutes or 0 for s in recent_sessions),
                           total_questions_asked=sum(s.questions_asked or 0 for s in recent_sessions),
                           total_restarts=sum(s.restarts or 0 for s in recent_sessions),
                           diamonds_this_week=sum(s.diamonds_earned or 0 for s in recent_sessions),
                           total_correct_easy=sum(s.correct_easy or 0 for s in recent_sessions),
                           total_correct_medium=sum(s.correct_medium or 0 for s in recent_sessions),
                           total_correct_hard=sum(s.correct_hard or 0 for s in recent_sessions),
                           total_attempted_easy=sum(s.attempted_easy or 0 for s in recent_sessions),
                           total_attempted_medium=sum(s.attempted_medium or 0 for s in recent_sessions),
                           total_attempted_hard=sum(s.attempted_hard or 0 for s in recent_sessions),
                           feedback_submitted=fb_done)

@app.route('/parent/feedback', methods=['GET','POST'])
@dashboard_required
def l2l_feedback():
    parent = Parent.query.filter_by(email=session['parent_email']).first()
    # Grant 3 months free from today as beta promise
    from datetime import date
    three_months = datetime.now(timezone.utc) + timedelta(days=92)
    if parent.plan == 'trial':
        parent.plan = 'connect'
    if not parent.subscription_end or parent.subscription_end < three_months:
        parent.subscription_end = three_months
        parent.subscription_start = datetime.now(timezone.utc)
    db.session.commit()
    fb = BetaFeedback(parent_email=parent.email,
                      child_name=request.form.get('child_name',''),
                      rating=request.form.get('rating',type=int),
                      what_worked=request.form.get('what_worked','').strip(),
                      what_didnt=request.form.get('what_didnt','').strip(),
                      would_pay=request.form.get('would_pay',''),
                      other_comments=request.form.get('other_comments','').strip())
    db.session.add(fb); db.session.commit()
    cid = request.form.get('child_id','0')
    return redirect(url_for('l2l_child_detail', child_id=cid) + '?feedback=done')


# ── LOGS — last 50 for debugging ─────────────────────────────────

@app.route('/admin/login', methods=['GET','POST'])
def l2l_admin_login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email','').strip()
        pw    = request.form.get('password','')
        admin = Admin.query.filter_by(email=email).first()
        if admin and _verify_pw(pw, admin.password_hash, admin.salt):
            session['is_admin'] = True
            admin.last_login = datetime.now(timezone.utc)
            db.session.commit()
            return redirect(url_for('l2l_admin_dashboard'))  # ← goes to HTML dashboard
        error = "Wrong email or password."
    return render_template('l2l/admin_login.html', error=error)

@app.route('/admin')
def l2l_admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('l2l_admin_login'))
    parents     = Parent.query.order_by(Parent.created_at.desc()).all()
    child_count = Child.query.count()
    return render_template('l2l/admin.html', parents=parents, child_count=child_count)

@app.route('/admin/logs', methods=['GET','POST'])
def l2l_logs():
    if not session.get('is_admin'):
        return jsonify({'error': 'Admin only'}), 403
    from models import LearningSession, DiamondTransaction
    sessions = (LearningSession.query
                .order_by(LearningSession.started_at.desc())
                .limit(50).all())
    logs = []
    for s in sessions:
        child = Child.query.get(s.child_id)
        logs.append({
            'session_id':    s.session_id,
            'child':         child.first_name if child else '?',
            'year_group':    s.year_group,
            'subject':       s.session_type,
            'started_at':    s.started_at.isoformat() if s.started_at else '',
            'active_minutes':s.active_minutes,
            'status':        s.status,
            'questions_asked':s.questions_asked,
            'restarts':      s.restarts,
            'correct_easy':  s.correct_easy,
            'correct_medium':s.correct_medium,
            'correct_hard':  s.correct_hard,
            'diamonds_earned':s.diamonds_earned,
            'phase':         (s.agent_state or {}).get('agents',{}).get('leo',{}).get('state',{}).get('phase','?'),
            'rapport_done':  (s.agent_state or {}).get('agents',{}).get('leo',{}).get('state',{}).get('rapport_done', False),
            'concepts_covered': (s.agent_state or {}).get('agents',{}).get('leo',{}).get('state',{}).get('concepts_covered', []),
            'last_messages': (s.chat_log or [])[-6:],
        })
    return jsonify({'sessions': logs, 'count': len(logs)})


# ── AUTO ADMIN ON STARTUP ────────────────────────────────────────
def ensure_admin():
    email = os.environ.get('ADMIN_EMAIL','')
    pw    = os.environ.get('ADMIN_PASSWORD','')
    if not email or not pw:
        return
    try:
        if not Admin.query.filter_by(email=email).first():
            h, s = _hash_pw(pw)
            admin = Admin(email=email, name='Admin', password_hash=h, salt=s)
            db.session.add(admin)
            db.session.commit()
            print(f"[ADMIN] Created: {email}")
    except Exception as e:
        print(f"[ADMIN] {e}")
        db.session.rollback()

with app.app_context():
    ensure_admin()


# ── MISSING SHORT ROUTES ─────────────────────────────────────────
@app.route('/admin/logout', methods=['GET','POST'])
def admin_logout_redirect():
    session.pop('is_admin', None)
    return redirect(url_for('l2l_login'))

@app.route('/delete-account', methods=['GET','POST'])
def delete_account():
    if 'parent_email' not in session:
        return redirect(url_for('l2l_login'))
    parent = Parent.query.filter_by(email=session['parent_email']).first()
    if parent:
        parent.data_deletion_requested = True
        parent.is_active = False
        db.session.commit()
    session.clear()
    return render_template('l2l/deletion_confirmed.html')

# ── TTS — OpenAI tts-1-hd (premium voices) ──────────────────────

@app.route('/api/tts', methods=['POST'])
def api_tts():
    """
    OpenAI TTS — tts-1-hd.
    Max:      onyx  (deep authoritative male)
    Prospect: nova  (natural female)
    Falls back 503 so frontend uses browser speech.
    """
    import requests as req_lib
    data     = request.get_json() or {}
    text     = data.get('text', '').strip()[:400]
    voice_id = data.get('voice', 'onyx')
    if not text:
        return jsonify({'error': 'No text'}), 400
    if not OPENAI_API_KEY:
        return jsonify({'error': 'OPENAI_API_KEY not set'}), 503
    try:
        r = req_lib.post(
            'https://api.openai.com/v1/audio/speech',
            headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type':  'application/json',
            },
            json={
                'model': 'tts-1-hd',
                'input': text,
                'voice': voice_id,
                'response_format': 'mp3',
                'speed': 0.95,
            },
            timeout=15,
        )
        if r.status_code != 200:
            print(f'[TTS] OpenAI error: {r.status_code} {r.text[:200]}')
            return jsonify({'error': 'TTS failed'}), 503
        from flask import Response
        return Response(r.content, status=200, mimetype='audio/mpeg',
                        headers={'Cache-Control': 'no-cache'})
    except Exception as e:
        print(f'[TTS] {e}')
        return jsonify({'error': str(e)}), 503






# ── PRACTICE CALL — Gemini plays the prospect ────────────────────

@app.route('/practice', methods=['GET'])
@child_required
def practice_page():
    child = Child.query.get(session['child_id'])
    return render_template('l2l/practice.html', child=child)



@child_required
def api_practice():
    child    = Child.query.get(session['child_id'])
    data     = request.get_json() or {}
    mode     = data.get('mode', 'prospect')
    history  = data.get('history', [])
    scenario = data.get('scenario', '')
    industry = (child.interests or {}).get('primary', 'general')
    level    = child.year_group or 'junior'

    if mode == 'review':
        transcript = '\n'.join(
            f"{'Rep' if m['role'] == 'rep' else 'Prospect'}: {m['text']}"
            for m in history
        )
        system = (
            f"You are Max, a blunt sales coach debriefing a practice call.\n"
            f"Rep level: {level}. Sector: {industry.replace('_',' ')}. Scenario: {scenario}\n\n"
            f"Write EXACTLY this structure, no extra words:\n"
            f"WHAT WORKED: [one sentence — specific, not vague]\n"
            f"BIGGEST MISS: [one sentence — the single thing that would have lost the deal]\n"
            f"THE FIX: [one concrete technique with an example phrase they could have used]\n"
            f"SCORE: [X/10 — one sentence why]\n\n"
            f"Max 120 words. No intro. Start with WHAT WORKED:"
        )
        reply = call_ai(system, transcript, max_tokens=540, temperature=0.3)
        return jsonify({'reply': reply or 'Good effort. Let us debrief what happened.'})

    # Gemini plays the prospect
    personas = {
        'tech_saas':          'a skeptical VP of Engineering at a 150-person SaaS company',
        'pharma':             'a busy GP with 8 minutes between patients',
        'financial_services': 'a cautious self-employed accountant who already has a financial adviser',
        'construction':       'a hard-nosed commercial director reviewing three competing bids',
        'recruitment':        'a hiring manager who has been burned by agencies before',
        'general':            'a realistic B2B decision maker who is politely skeptical',
    }
    persona = personas.get(industry, personas['general'])

    last_rep = history[-1]['text'] if history else ''
    prior = '\n'.join(
        f"{'Salesperson' if m['role'] == 'rep' else 'Prospect'}: {m['text']}"
        for m in history[:-1]
    ) if len(history) > 1 else ''

    is_opening = len(history) <= 1

    system = (
        f"You are {persona}. A salesperson called you.\n"
        f"Scenario: {scenario}\n\n"
        f"RULES — zero tolerance:\n"
        f"- Output ONLY spoken words. No labels, no formatting, no punctuation beyond commas and periods.\n"
        f"- NEVER use square brackets. NEVER write [Name] [Company] [Product] or any placeholder.\n"
        f"- NEVER use round brackets or stage directions.\n"
        f"- NEVER use asterisks.\n"
        f"- Do not introduce yourself by name. You are anonymous.\n"
        f"- Max 15 words per reply.\n"
        f"- Be blunt and skeptical. You get calls like this every day.\n"
        f"{'- Opening line only: say you are busy and ask what this is about.' if is_opening else ''}\n\n"
        f"{'Prior:' + chr(10) + prior if prior else ''}"
    )

    user_msg = f"Salesperson said: {last_rep}" if last_rep else "The salesperson just called."
    reply = call_ai(system, user_msg, max_tokens=540, temperature=0.7)

    # Strip any remaining brackets/placeholders
    import re
    if reply:
        reply = re.sub(r'\[[^\]]*\]', '', reply)
        reply = re.sub(r'\([^)]*\)', '', reply)
        reply = re.sub(r'\*[^*]*\*', '', reply)
        reply = re.sub(r'\s+', ' ', reply).strip().strip('"').strip()

    return jsonify({'reply': reply or "I'm busy. What do you want?"})



# ── LANDING + SHORT REDIRECTS ────────────────────────────────────
@app.route('/', methods=['GET','POST'])
def index():
    return render_template('l2l/landing.html')

@app.route('/pricing')
def pricing():
    return render_template('l2l/pricing.html')

@app.route('/privacy')
def privacy():
    return render_template('l2l/privacy.html')