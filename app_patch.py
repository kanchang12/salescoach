"""
app_patch.py — Changes to apply to app.py for the Sales Coach version
======================================================================
This is NOT a standalone file. It documents the exact additions
you need to make to your existing app.py.

Apply these changes in order.
"""


# ══════════════════════════════════════════════════════════════════
# 1. ENV VARS — add to top of app.py (after GEMINI_MODEL line)
# ══════════════════════════════════════════════════════════════════

"""
ELEVENLABS_API_KEY  = os.environ.get('ELEVENLABS_API_KEY', '')
ELEVENLABS_VOICE_ID = os.environ.get('ELEVENLABS_VOICE_ID', 'pNInz6obpgDQGcFmaJgB')  # Adam — change in EL dashboard
ELEVENLABS_AGENT_ID = os.environ.get('ELEVENLABS_AGENT_ID', '')  # your Conversational AI agent ID
"""


# ══════════════════════════════════════════════════════════════════
# 2. IMPORT CHANGE — swap curriculum import in app.py
# ══════════════════════════════════════════════════════════════════

"""
Replace:
    import curriculum as cur

With:
    import sales_curriculum as cur
"""

# Note: leo.py already imports 'sales_curriculum as cur' internally.
# But if app.py itself calls cur.get_curriculum() or cur.get_next_topic(),
# you need this change there too.


# ══════════════════════════════════════════════════════════════════
# 3. UPDATE l2l_room() ROUTE — pass elevenlabs_agent_id to template
# ══════════════════════════════════════════════════════════════════

"""
Replace your l2l_room() return statement:

    return render_template('l2l/learning_room.html',
                           child=child,
                           learning_session=ls,
                           chat_history=ls.chat_log or [],
                           diamond_balance=child.diamond_balance)

With:

    return render_template('l2l/learning_room.html',
                           child=child,
                           learning_session=ls,
                           chat_history=ls.chat_log or [],
                           diamond_balance=child.diamond_balance,
                           elevenlabs_agent_id=ELEVENLABS_AGENT_ID)
"""


# ══════════════════════════════════════════════════════════════════
# 4. NEW ROUTE — /api/tts  (add anywhere in app.py before the if __name__ block)
# ══════════════════════════════════════════════════════════════════

"""
@app.route('/api/tts', methods=['POST'])
def api_tts():
    \"\"\"
    Proxy to ElevenLabs TTS API.
    Receives: { "text": "..." }
    Returns:  audio/mpeg stream
    \"\"\"
    import requests as req_lib

    data = request.get_json() or {}
    text = data.get('text', '').strip()

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    if not ELEVENLABS_API_KEY:
        return jsonify({'error': 'ElevenLabs API key not configured'}), 503

    # Truncate to 500 chars — TTS for conversational replies only
    text = text[:500]

    try:
        el_res = req_lib.post(
            f'https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}',
            headers={
                'xi-api-key':   ELEVENLABS_API_KEY,
                'Content-Type': 'application/json',
            },
            json={
                'text':       text,
                'model_id':   'eleven_turbo_v2_5',  # Lowest latency
                'voice_settings': {
                    'stability':        0.55,
                    'similarity_boost': 0.75,
                    'style':            0.0,
                    'use_speaker_boost': True,
                },
            },
            timeout=15,
        )

        if el_res.status_code != 200:
            print(f'[TTS] ElevenLabs error: {el_res.status_code} {el_res.text[:200]}')
            return jsonify({'error': 'TTS service error'}), 502

        from flask import Response
        return Response(
            el_res.content,
            status=200,
            mimetype='audio/mpeg',
            headers={
                'Cache-Control': 'no-cache',
                'Content-Length': str(len(el_res.content)),
            }
        )

    except Exception as e:
        print(f'[TTS] Exception: {e}')
        return jsonify({'error': 'TTS request failed'}), 500
"""


# ══════════════════════════════════════════════════════════════════
# 5. ADD TO requirements.txt
# ══════════════════════════════════════════════════════════════════

"""
Add this line to requirements.txt:
    requests>=2.31.0

(likely already there — check before adding)
"""


# ══════════════════════════════════════════════════════════════════
# 6. ENV VARS TO SET IN GOOGLE CLOUD RUN / .env
# ══════════════════════════════════════════════════════════════════

"""
ELEVENLABS_API_KEY   = sk_...           (from elevenlabs.io → API Keys)
ELEVENLABS_VOICE_ID  = pNInz6obpgDQGcFmaJgB   (Adam — or pick from your EL voice library)
ELEVENLABS_AGENT_ID  = agent_...       (from elevenlabs.io → Conversational AI → your agent)

Popular voice IDs for a sales coach persona:
  Adam:    pNInz6obpgDQGcFmaJgB   — deep, authoritative
  Josh:    TxGEqnHWrfWFTfGW9XjX   — energetic
  Antoni:  ErXwobaYiN019PkySvjV   — well-rounded
  Liam:    TX3LPaxmHKxFdv7VOFE1   — calm, professional
"""


# ══════════════════════════════════════════════════════════════════
# 7. ELEVENLABS AGENT SETUP INSTRUCTIONS
# ══════════════════════════════════════════════════════════════════

"""
In the ElevenLabs dashboard (elevenlabs.io):

1. Go to "Conversational AI" → "Create Agent"

2. Agent Name: Max — TrueSkills Sales Coach

3. System Prompt (paste this):
   ----------------------------------------
   You are Max, a high-performance sales coach.
   You are coaching {{learner_name}}, a sales professional.
   Your job is to run realistic sales roleplay scenarios and give direct,
   actionable coaching feedback.

   You are direct, warm, and precise. Not a corporate trainer.
   You roleplay both the coach and the customer/prospect in practice scenarios.
   You give one clear coaching point at a time.
   When the rep does something well, you name exactly what worked.
   When they miss something, you call it out — no vague praise.

   Keep responses conversational and under 80 words.
   ----------------------------------------

4. Voice: pick from your preferred voice (Adam recommended for authority)

5. Dynamic Variables: enable "learner_name"

6. Copy the Agent ID and set ELEVENLABS_AGENT_ID in your Cloud Run env vars.
"""
