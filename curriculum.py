"""
love2learn — UK National Curriculum
=====================================
Year 2 to Year 6. Maths, Reading, Coding Logic.

Each topic has:
- The actual UK National Curriculum objective
- How Leo explains it (plain English, no jargon)
- Teaching script — what Leo says to introduce the concept
- Interest-based examples (football, minecraft, animals, space, dinosaurs, art)
- Check questions — natural questions Leo weaves in after teaching
- Common mistakes — what to watch for

Leo picks the interest template that matches what the child told him.
Leo teaches FIRST. Checks SECOND. Never quizzes cold.
"""


# ================================================================
# INTEREST TEMPLATE PICKER
# ================================================================

INTERESTS = ['football', 'minecraft', 'animals', 'space', 'dinosaurs',
             'art', 'music', 'pokemon', 'cars', 'cooking', 'lego', 'default']

def get_example(templates, interest):
    """Pick the best matching interest template."""
    if not interest:
        return templates.get('default', list(templates.values())[0])

    interest_lower = interest.lower().strip()

    # Direct match
    for key in templates:
        if key in interest_lower or interest_lower in key:
            return templates[key]

    # Partial match
    for key in templates:
        words = interest_lower.split()
        if any(w in key for w in words):
            return templates[key]

    return templates.get('default', list(templates.values())[0])


def get_curriculum(year_group, subject):
    """Get all topics for a year group and subject."""
    data = {
        'maths': MATHS_CURRICULUM,
        'reading': READING_CURRICULUM,
        'coding': CODING_CURRICULUM,
    }
    subject_data = data.get(subject, MATHS_CURRICULUM)
    return subject_data.get(year_group, [])


def get_next_topic(year_group, subject, covered_ids):
    """Get the next topic Leo should teach, skipping already covered ones."""
    topics = get_curriculum(year_group, subject)
    for topic in topics:
        if topic['id'] not in covered_ids:
            return topic
    # All covered — loop back to start or return first
    return topics[0] if topics else None


def build_teaching_message(topic, interest):
    """Build Leo's teaching message for a topic using the child's interest."""
    example = get_example(topic['examples'], interest)
    intro = topic['leo_intro']
    return f"{intro}\n\n{example}"


def build_check_message(topic, interest):
    """Build Leo's natural check question after teaching."""
    checks = topic.get('check_questions', [])
    if not checks:
        return None
    check_templates = checks[0] if isinstance(checks[0], dict) else {'default': checks[0]}
    if isinstance(check_templates, str):
        return check_templates
    return get_example(check_templates, interest)


# ================================================================
# MATHS CURRICULUM — UK National Curriculum Year 2-6
# ================================================================

MATHS_CURRICULUM = {

    # ================================================================
    # YEAR 2
    # ================================================================
    "year_2": [
        {
            "id": "y2_add_2digit",
            "topic": "Adding two-digit numbers",
            "nc_objective": "Add and subtract numbers using concrete objects and mentally, including two two-digit numbers.",
            "leo_intro": "Adding means putting two amounts together to find the total. The trick is to add the tens first, then the ones.",
            "examples": {
                "football": "So say Salah scored 23 goals in one season and 14 in the next. To add them: first the tens — 20 and 10 makes 30. Then the ones — 3 and 4 makes 7. So altogether that's 37 goals.",
                "minecraft": "Imagine you mined 23 diamonds on Monday and 14 on Tuesday. Tens first: 20 and 10 is 30. Ones: 3 and 4 is 7. Total is 37 diamonds in your chest.",
                "animals": "A zoo has 23 monkeys and 14 penguins. Tens: 20 plus 10 is 30. Ones: 3 plus 4 is 7. So 37 animals altogether.",
                "space": "A rocket travels 23 miles in the first minute and 14 miles in the second. Tens: 20 plus 10 is 30. Ones: 3 plus 4 is 7. That's 37 miles total.",
                "dinosaurs": "A T-Rex ate 23 animals on Monday and 14 on Tuesday. Tens: 20 plus 10 is 30. Ones: 3 plus 4 is 7. So 37 animals in two days.",
                "default": "Let's say you had 23 stickers and you got 14 more. Tens first: 20 plus 10 is 30. Ones: 3 plus 4 is 7. So you have 37 stickers altogether.",
            },
            "check_questions": {
                "football": "So if Mane scored 31 goals and then 25 more the next season — how do you think we'd start working that out?",
                "minecraft": "If you had 42 diamonds and found 35 more in a cave — what would you add first, the tens or the ones?",
                "animals": "A farm has 35 sheep and 24 cows. How many animals is that altogether?",
                "default": "Try this one — 32 plus 25. Start with the tens. What do you get?",
            },
            "common_mistakes": [
                "Adding ones before tens — remind them tens first",
                "Forgetting to carry — not needed at this level, keep it simple",
            ],
        },
        {
            "id": "y2_subtract_2digit",
            "topic": "Subtracting two-digit numbers",
            "nc_objective": "Subtract numbers using concrete objects and mentally, including two two-digit numbers.",
            "leo_intro": "Subtracting means taking one amount away from another. We find out what's left. Again — tens first, then ones.",
            "examples": {
                "football": "Say a team had 45 points and lost 12 points worth of games. Tens: 40 take away 10 is 30. Ones: 5 take away 2 is 3. So they have 33 points left.",
                "minecraft": "You had 56 arrows and used 23 of them fighting zombies. Tens: 50 minus 20 is 30. Ones: 6 minus 3 is 3. So you have 33 arrows left.",
                "animals": "There were 48 birds on a wire and 25 flew away. Tens: 40 minus 20 is 20. Ones: 8 minus 5 is 3. So 23 birds are still there.",
                "space": "A spaceship had 67 fuel cells and used 34 to reach the moon. Tens: 60 minus 30 is 30. Ones: 7 minus 4 is 3. So 33 fuel cells left.",
                "dinosaurs": "A herd of 58 dinosaurs walked away, and 34 stayed behind. How many walked away? Tens: 50 minus 30 is 20. Ones: 8 minus 4 is 4. So 24 walked away.",
                "default": "You had 47 sweets and gave 23 to your friends. Tens: 40 minus 20 is 20. Ones: 7 minus 3 is 4. So you have 24 sweets left.",
            },
            "check_questions": {
                "football": "A team had 65 points and dropped 32 of them. How many do they have now? Start with the tens.",
                "minecraft": "You had 78 wood blocks and used 45 building your house. How many do you have left?",
                "default": "Try this — 59 minus 36. Tens first. What do you get?",
            },
            "common_mistakes": [
                "Subtracting the larger from the smaller in the ones column",
                "Forgetting to subtract tens separately",
            ],
        },
        {
            "id": "y2_times2",
            "topic": "2 times table",
            "nc_objective": "Recall and use multiplication and division facts for the 2 multiplication table.",
            "leo_intro": "The 2 times table means counting in pairs. Everything times 2 is just doubled — two of something. It's the same as adding the number to itself.",
            "examples": {
                "football": "In football, every player has 2 boots. So 1 player has 2 boots, 2 players have 4 boots, 3 players have 6 boots. We're just counting pairs of boots. 3 times 2 is 6.",
                "minecraft": "Every house in Minecraft needs 2 doors. One house — 2 doors. Two houses — 4 doors. Three houses — 6 doors. That's the 2 times table right there.",
                "animals": "Every bird has 2 wings. 1 bird has 2 wings. 2 birds have 4 wings. 3 birds have 6 wings. Count the wings — that's your 2 times table.",
                "space": "Each astronaut needs 2 gloves. 1 astronaut — 2 gloves. 2 astronauts — 4 gloves. 3 astronauts — 6 gloves. See the pattern?",
                "dinosaurs": "Every Diplodocus has 2 horns. 1 Diplodocus — 2 horns. 2 Diplodocuses — 4 horns. 3 — 6 horns. That's the 2 times table.",
                "default": "Think about pairs of socks. 1 pair is 2 socks. 2 pairs is 4 socks. 3 pairs is 6 socks. That's counting in twos — the 2 times table.",
            },
            "check_questions": {
                "football": "There are 4 players on the pitch. How many boots is that altogether?",
                "minecraft": "You're building 5 houses. Each needs 2 doors. How many doors do you need?",
                "animals": "6 birds are sitting on a branch. How many wings is that in total?",
                "default": "What is 7 times 2? Think of 7 pairs of something.",
            },
            "common_mistakes": [
                "Confusing 2 times table with adding 2 to the number",
            ],
        },
        {
            "id": "y2_times5",
            "topic": "5 times table",
            "nc_objective": "Recall and use multiplication and division facts for the 5 multiplication table.",
            "leo_intro": "The 5 times table is counting in fives. The answers always end in 0 or 5. That's the trick — if the answer doesn't end in 0 or 5, something has gone wrong.",
            "examples": {
                "football": "A football team scores 5 points every time they win. After 1 win — 5 points. 2 wins — 10 points. 3 wins — 15 points. Always ends in 0 or 5.",
                "minecraft": "Each chest holds 5 diamonds. 1 chest — 5 diamonds. 2 chests — 10. 3 chests — 15. Count in fives as you open each chest.",
                "animals": "A starfish has 5 arms. 1 starfish — 5 arms. 2 starfish — 10 arms. 3 starfish — 15 arms.",
                "space": "A space mission lasts 5 days. After 1 mission — 5 days. 2 missions — 10 days. 3 missions — 15 days in space.",
                "dinosaurs": "A Velociraptor has 5 claws on each foot. 1 Velociraptor — 5 claws. 2 — 10 claws. 3 — 15 claws.",
                "default": "Think of a hand. Each hand has 5 fingers. 1 hand — 5. 2 hands — 10. 3 hands — 15. That's the 5 times table.",
            },
            "check_questions": {
                "football": "A team wins 6 games and gets 5 points each time. How many points is that?",
                "minecraft": "You have 7 chests each with 5 diamonds. How many diamonds in total?",
                "default": "What's 8 times 5? Remember — the answer ends in 0 or 5.",
            },
            "common_mistakes": [
                "Answer not ending in 0 or 5 — use this as a self-check rule",
            ],
        },
        {
            "id": "y2_times10",
            "topic": "10 times table",
            "nc_objective": "Recall and use multiplication and division facts for the 10 multiplication table.",
            "leo_intro": "The 10 times table is the easiest one. You just put a zero on the end of any number. 3 times 10 is 30. 7 times 10 is 70. That's it.",
            "examples": {
                "football": "A goal is worth 10 points. 1 goal — 10 points. 2 goals — 20. 3 goals — 30. Just put a zero on the end of how many goals.",
                "minecraft": "You collect 10 blocks every minute. After 1 minute — 10 blocks. After 2 — 20. After 3 — 30. Zero on the end every time.",
                "animals": "A centipede has 10 legs per segment. 1 segment — 10 legs. 2 segments — 20. 3 segments — 30.",
                "space": "A rocket goes 10 miles every second. After 1 second — 10 miles. 2 seconds — 20. 3 seconds — 30.",
                "dinosaurs": "A Brachiosaurus eats 10 trees a day. After 1 day — 10 trees. 2 days — 20. 3 days — 30.",
                "default": "Think of 10p coins. 1 coin — 10p. 2 coins — 20p. 3 coins — 30p. Always put a zero on the end.",
            },
            "check_questions": {
                "football": "If a player scores 6 goals and each is worth 10 points, how many points altogether?",
                "minecraft": "You mine for 9 minutes and collect 10 blocks a minute. How many blocks?",
                "default": "What is 4 times 10? And 8 times 10? What do you notice about the answers?",
            },
            "common_mistakes": [
                "Adding 10 instead of multiplying — remind them it's groups of 10",
            ],
        },
        {
            "id": "y2_fractions_half",
            "topic": "Halves and quarters",
            "nc_objective": "Recognise, find, name and write fractions 1/3, 1/4, 2/4 and 3/4 of a length, shape, set of objects or quantity.",
            "leo_intro": "A half means splitting something equally into 2 parts and taking one. A quarter means splitting into 4 equal parts and taking one. The key word is EQUAL — both halves have to be the same size.",
            "examples": {
                "football": "A football match is 90 minutes long. Half time is at 45 minutes — that's exactly half. If we split the 90 minutes into 4 quarters, each quarter is 22 and a half minutes. That's why they talk about quarters in American football.",
                "minecraft": "You have 8 diamonds and want to share them equally between 2 friends. Half of 8 is 4 — each friend gets 4. If you split between 4 friends, a quarter of 8 is 2 — each gets 2.",
                "animals": "A pizza for 2 cats — cut it in half, each cat gets the same amount. A pizza for 4 dogs — cut it into quarters, each dog gets one quarter.",
                "space": "A space station has 12 rooms. Half the rooms are sleeping quarters — that's 6. A quarter of the rooms are labs — that's 3.",
                "dinosaurs": "A dinosaur has 12 eggs. Half of them hatch — that's 6. A quarter of them are red — that's 3.",
                "default": "You have 10 sweets. Half means sharing equally between 2 people — that's 5 each. A quarter means sharing between 4 people — that's 2 and a half each... hmm, doesn't work perfectly. Let's try with 12 sweets instead.",
            },
            "check_questions": {
                "football": "A pitch is 100 metres long. What's half of that? And if we split it into quarters, how long is each quarter?",
                "minecraft": "You have 16 gold ingots. What's half? What's a quarter?",
                "default": "What is half of 20? And what is a quarter of 20?",
            },
            "common_mistakes": [
                "Unequal splitting — stress that half means exactly equal",
                "Confusing half with quarter",
            ],
        },
    ],

    # ================================================================
    # YEAR 3
    # ================================================================
    "year_3": [
        {
            "id": "y3_times3",
            "topic": "3 times table",
            "nc_objective": "Recall and use multiplication and division facts for the 3 multiplication table.",
            "leo_intro": "The 3 times table is counting in threes. A good trick is to add 3 each time. 3, 6, 9, 12, 15. Also useful: the digits of the answer always add up to a multiple of 3. So 12 — 1 plus 2 is 3. That's a way to check yourself.",
            "examples": {
                "football": "A team gets 3 points for every win. After 1 win — 3 points. 2 wins — 6. 3 wins — 9. 4 wins — 12. That's the Premier League points system right there.",
                "minecraft": "You need 3 logs to make a plank set. 1 craft — 3 logs. 2 crafts — 6 logs. 3 crafts — 9 logs. 4 crafts — 12 logs.",
                "animals": "A clover leaf has 3 leaves. 1 clover — 3 leaves. 2 clovers — 6 leaves. 3 clovers — 9 leaves.",
                "space": "Each rocket has 3 engines. 1 rocket — 3 engines. 2 rockets — 6. 3 rockets — 9.",
                "dinosaurs": "A Triceratops has 3 horns. 1 Triceratops — 3 horns. 2 — 6 horns. 3 — 9 horns.",
                "default": "A triangle has 3 sides. 1 triangle — 3 sides. 2 triangles — 6 sides. 3 triangles — 9 sides.",
            },
            "check_questions": {
                "football": "A team has won 7 games. How many points have they got? Remember — 3 points per win.",
                "minecraft": "You want to make 8 plank sets. Each needs 3 logs. How many logs altogether?",
                "default": "What is 9 times 3? And 11 times 3?",
            },
            "common_mistakes": [
                "Mixing up 3s and 6s — the 3 times table is exactly half the 6 times table",
            ],
        },
        {
            "id": "y3_times4",
            "topic": "4 times table",
            "nc_objective": "Recall and use multiplication and division facts for the 4 multiplication table.",
            "leo_intro": "The 4 times table is double the 2 times table. So if you know 6 times 2 is 12, then 6 times 4 is just double that — 24. Double it twice and you've got it.",
            "examples": {
                "football": "A car park at the stadium has rows of 4 spaces. 1 row — 4 spaces. 2 rows — 8. 3 rows — 12. 4 rows — 16.",
                "minecraft": "You need 4 planks to make a crafting table. 1 table — 4 planks. 2 tables — 8. 3 tables — 12.",
                "animals": "A dog has 4 legs. 1 dog — 4 legs. 2 dogs — 8. 3 dogs — 12. 4 dogs — 16.",
                "space": "A space probe has 4 solar panels. 1 probe — 4 panels. 2 probes — 8. 3 probes — 12.",
                "dinosaurs": "Most dinosaurs had 4 limbs. 1 dinosaur — 4 limbs. 2 — 8. 3 — 12.",
                "default": "A table has 4 legs. 1 table — 4 legs. 2 tables — 8. 3 tables — 12.",
            },
            "check_questions": {
                "football": "There are 6 rows of car park spaces, each row has 4 spaces. How many spaces altogether?",
                "minecraft": "You need 7 crafting tables. Each needs 4 planks. How many planks?",
                "default": "What is 8 times 4? Remember — it's double 8 times 2.",
            },
            "common_mistakes": [
                "Confusing 4 times table with adding 4 repeatedly — work on the concept of groups",
            ],
        },
        {
            "id": "y3_times8",
            "topic": "8 times table",
            "nc_objective": "Recall and use multiplication and division facts for the 8 multiplication table.",
            "leo_intro": "The 8 times table is double the 4 times table. So 6 times 4 is 24, meaning 6 times 8 is 48. Always even numbers. And all answers are even — another handy check.",
            "examples": {
                "football": "An octopus — if it played football it'd have 8 legs to kick with. 1 octopus — 8 legs. 2 octopuses — 16. 3 — 24. 4 — 32.",
                "minecraft": "A spider in Minecraft has 8 legs. 1 spider — 8 legs. 2 spiders — 16. 3 spiders — 24.",
                "animals": "A spider has 8 legs. 1 spider — 8 legs. 2 spiders — 16. 3 — 24. 4 — 32.",
                "space": "A space station module has 8 solar cells. 1 module — 8 cells. 2 modules — 16. 3 — 24.",
                "dinosaurs": "Imagine a dinosaur with 8 spines on its back. 1 dinosaur — 8 spines. 2 — 16. 3 — 24.",
                "default": "A box holds 8 crayons. 1 box — 8 crayons. 2 boxes — 16. 3 boxes — 24. 4 boxes — 32.",
            },
            "check_questions": {
                "football": "5 octopuses are watching the match. How many legs altogether?",
                "minecraft": "You encounter 6 spiders in a cave. How many legs is that?",
                "default": "What is 7 times 8? Remember — double 7 times 4.",
            },
            "common_mistakes": [
                "Forgetting that 8 times table answers are always even",
            ],
        },
        {
            "id": "y3_fractions",
            "topic": "Fractions — thirds and eighths",
            "nc_objective": "Count up and down in tenths; recognise that tenths arise from dividing an object into 10 equal parts.",
            "leo_intro": "A fraction is just dividing something into equal parts. The bottom number tells you how many equal parts there are. The top number tells you how many of those parts you have. So 3 over 8 means you split something into 8 equal parts and took 3 of them.",
            "examples": {
                "football": "A football match has 90 minutes. One third of the match is 30 minutes — that's when the game really starts warming up. Two thirds is 60 minutes — the time when managers start making substitutions.",
                "minecraft": "You have a bar of 8 gold ingots. One eighth is 1 ingot. Three eighths is 3 ingots. Four eighths is exactly half — which is 4 ingots.",
                "animals": "A litter of 8 kittens. One eighth of them is 1 kitten. Three eighths is 3 kittens. If you had 6 eighths, that's 6 out of 8 — or three quarters.",
                "space": "A mission lasts 9 months. One third of it is 3 months — that's the launch phase. Two thirds is 6 months — the travel phase.",
                "dinosaurs": "A dinosaur skeleton has 12 main bones in its leg. One third of those bones is 4. Two thirds is 8.",
                "default": "You have a chocolate bar with 8 pieces. One eighth is 1 piece. Three eighths is 3 pieces. Half is four eighths — that's 4 pieces.",
            },
            "check_questions": {
                "football": "If you've watched two thirds of a 90 minute match, how long have you been watching?",
                "minecraft": "You have a stack of 12 blocks. What is one third of 12? What is two thirds?",
                "default": "I have 16 grapes. What is one eighth of 16? What is three eighths?",
            },
            "common_mistakes": [
                "Confusing numerator and denominator",
                "Not ensuring equal parts when dividing",
            ],
        },
        {
            "id": "y3_time",
            "topic": "Telling the time and time intervals",
            "nc_objective": "Tell and write the time from an analogue clock, including using Roman numerals from I to XII, and 12-hour and 24-hour clocks.",
            "leo_intro": "Time works in groups of 60 — 60 seconds in a minute, 60 minutes in an hour. The short hand shows the hour. The long hand shows the minutes. When the long hand points to 12, it's exactly on the hour. When it points to 6, it's half past.",
            "examples": {
                "football": "A football match kicks off at 3 o'clock — the short hand points to 3, long hand to 12. Half time is 45 minutes later — the long hand has gone almost all the way round. The final whistle at 90 minutes means the long hand has gone round once and a half.",
                "minecraft": "In Minecraft a day lasts 20 real minutes. If it's daytime for 10 minutes, that's half the day. Monsters come out at night — which starts 10 minutes in. So 10 minutes is half of 20.",
                "animals": "A vet appointment is at quarter past 2 — that means 2:15. The cat needs medicine every 6 hours — so if it has it at 8am, next dose is at 2pm, then 8pm.",
                "space": "A rocket launches at 14:30 — that's half past 2 in the afternoon in 24-hour time. It lands 6 hours later at 20:30 — that's half past 8 in the evening.",
                "dinosaurs": "Scientists think T-Rex was most active from about 6am to 6pm — a 12 hour window. Half of that is 6 hours. A quarter of that is 3 hours.",
                "default": "School starts at 9 o'clock. Lunch is at half past 12. That's 3 and a half hours of morning lessons. Home time is at 3 o'clock — 6 hours after school started.",
            },
            "check_questions": {
                "football": "A match starts at quarter past 3. It lasts 90 minutes. What time does it finish?",
                "minecraft": "If it's 10:45 now, what time will it be in 30 minutes?",
                "default": "School finishes at 3:30. You walk home for 20 minutes. What time do you get home?",
            },
            "common_mistakes": [
                "Confusing the hour and minute hands",
                "Forgetting that half past means 30 minutes",
            ],
        },
    ],

    # ================================================================
    # YEAR 4
    # ================================================================
    "year_4": [
        {
            "id": "y4_times6",
            "topic": "6 times table",
            "nc_objective": "Recall multiplication and division facts for multiplication tables up to 12x12.",
            "leo_intro": "The 6 times table is double the 3 times table. So 7 times 3 is 21, meaning 7 times 6 is 42. All the answers are even numbers. And here's a cool pattern — for the first 10: the ones digit goes 6, 2, 8, 4, 0 and repeats.",
            "examples": {
                "football": "Each side of a hexagonal football panel has 6 sides — wait, that's the shape. Let's try: a football league has 6 points for two wins. 1 double win — 6 points. 2 — 12. 3 — 18. 4 — 24.",
                "minecraft": "A honeycomb in Minecraft is hexagonal — 6 sides. 1 honeycomb — 6 sides. 2 honeycombs — 12. 3 — 18.",
                "animals": "An insect has 6 legs. 1 insect — 6 legs. 2 insects — 12. 3 — 18. 4 — 24. 5 — 30.",
                "space": "A space station has 6 docking ports. 1 station — 6 ports. 2 stations — 12. 3 — 18.",
                "dinosaurs": "Imagine a Stegosaurus has 6 back plates per section. 1 section — 6. 2 sections — 12. 3 sections — 18.",
                "default": "An egg box holds 6 eggs. 1 box — 6 eggs. 2 boxes — 12. 3 boxes — 18. 4 boxes — 24.",
            },
            "check_questions": {
                "football": "7 insects are watching a match. How many legs are there in the insect section?",
                "animals": "There are 9 insects in a jar. How many legs altogether?",
                "default": "What is 8 times 6? Remember — double 8 times 3.",
            },
            "common_mistakes": [
                "Mixing up 6 and 9 times tables in the middle range",
            ],
        },
        {
            "id": "y4_times7",
            "topic": "7 times table",
            "nc_objective": "Recall multiplication and division facts for multiplication tables up to 12x12.",
            "leo_intro": "The 7 times table is tricky — it doesn't have easy patterns like 5s or 10s. The best way is to learn the ones that trip people up: 7 times 7 is 49, 7 times 8 is 56, 7 times 9 is 63. Those three cause the most problems.",
            "examples": {
                "football": "There are 7 days in a week. A footballer trains every day. After 1 week — 7 sessions. 2 weeks — 14. 3 weeks — 21. 4 weeks — 28. That's how they get so good.",
                "minecraft": "A week in real life is 7 days. In Minecraft you play 7 minutes per day. 1 week — 49 minutes. That's 7 times 7.",
                "animals": "A rainbow has 7 colours — just like how 7 different animals visited a watering hole each day. 1 day — 7 visits. 7 days — 49 visits.",
                "space": "A space mission brief lasts 7 minutes. 1 brief — 7 minutes. 7 briefs — 49 minutes.",
                "dinosaurs": "A scientist studies 7 dinosaur bones a day. In 7 days — 49 bones. In 8 days — 56 bones.",
                "default": "A week has 7 days. 1 week — 7 days. 2 weeks — 14. 7 weeks — 49 days. 8 weeks — 56 days.",
            },
            "check_questions": {
                "football": "A footballer trains 7 days a week for 6 weeks. How many training sessions is that?",
                "default": "What is 7 times 8? This is the one that trips most people up — 56.",
            },
            "common_mistakes": [
                "7x7=49 and 7x8=56 are the most commonly confused — drill these specifically",
            ],
        },
        {
            "id": "y4_decimals",
            "topic": "Decimals — tenths and hundredths",
            "nc_objective": "Recognise and write decimal equivalents of any number of tenths or hundredths.",
            "leo_intro": "A decimal point separates whole numbers from parts of a number. The first digit after the point is tenths — how many tenths you have. The second digit is hundredths. So 3.7 means 3 whole and 7 tenths. Like 3 pounds and 70 pence.",
            "examples": {
                "football": "Football stats use decimals all the time. A player averages 0.7 goals per game — that's 7 tenths of a goal. Their pass accuracy might be 87.5 percent — 87 whole percent and 5 tenths more.",
                "minecraft": "In some Minecraft mods, items have durability shown as decimals. A sword at 3.7 durability has 3 whole points and 7 tenths more before it breaks.",
                "animals": "A cheetah runs at 112.7 kilometres per hour. That's 112 whole kilometres per hour and 7 tenths more.",
                "space": "A satellite orbits at 7.6 kilometres per second. 7 whole kilometres and 6 tenths of a kilometre every second.",
                "dinosaurs": "A fossil is dated at 66.5 million years old. 66 whole million years and 5 tenths of a million years more.",
                "default": "A bottle holds 1.5 litres. That's 1 whole litre and 5 tenths — which is half a litre. So 1 and a half litres.",
            },
            "check_questions": {
                "football": "A player's average goals per game is 0.8. What does the 8 represent — is it 8 whole goals or something else?",
                "default": "Which is bigger — 3.7 or 3.4? How do you know?",
            },
            "common_mistakes": [
                "Thinking 3.7 is smaller than 3.4 because 7 is 'after the point'",
                "Not understanding that 0.5 is a half",
            ],
        },
        {
            "id": "y4_area_perimeter",
            "topic": "Area and perimeter",
            "nc_objective": "Measure and calculate the perimeter of a rectilinear figure in centimetres and metres; find the area of rectilinear shapes by counting squares.",
            "leo_intro": "Perimeter is the distance all the way around the outside of a shape — like walking around the edge of a football pitch. Area is how much space is inside — like how much grass is on the pitch. Perimeter is measured in cm or m. Area is measured in squares — cm squared or m squared.",
            "examples": {
                "football": "A 5-a-side football pitch is 30 metres long and 20 metres wide. The perimeter — all the way around — is 30 plus 20 plus 30 plus 20 which is 100 metres. The area is length times width — 30 times 20 is 600 square metres of grass.",
                "minecraft": "You want to build a wall around your base. Your base is 10 blocks long and 8 blocks wide. The perimeter is 10 plus 8 plus 10 plus 8 — that's 36 blocks of wall. The area inside is 10 times 8 — 80 square blocks of space.",
                "animals": "A tiger's territory is a rectangle 4km long and 3km wide. Its perimeter — how far it walks to patrol the edge — is 4 plus 3 plus 4 plus 3 which is 14km. The area of its territory is 4 times 3 which is 12 square kilometres.",
                "space": "A landing pad for a spacecraft is 15m long and 12m wide. To put a fence around it: 15 plus 12 plus 15 plus 12 is 54 metres of fence. The area — how much surface the pad covers — is 15 times 12 which is 180 square metres.",
                "dinosaurs": "A dinosaur enclosure is 50m long and 30m wide. The fence around it — the perimeter — is 50 plus 30 plus 50 plus 30 which is 160 metres. The area inside is 50 times 30 which is 1500 square metres.",
                "default": "A garden is 8m long and 5m wide. To put a fence around it: 8 plus 5 plus 8 plus 5 is 26 metres of fence — that's the perimeter. To find out how much grass seed you need — the area — it's 8 times 5 which is 40 square metres.",
            },
            "check_questions": {
                "football": "A training pitch is 25 metres long and 15 metres wide. What is the perimeter? And what is the area?",
                "minecraft": "Your Minecraft farm is 12 blocks by 9 blocks. How many fence blocks do you need for the perimeter? What is the area?",
                "default": "A room is 6m long and 4m wide. What is the perimeter? What is the area?",
            },
            "common_mistakes": [
                "Confusing perimeter (adding sides) with area (multiplying length by width)",
                "Forgetting to add all 4 sides for perimeter",
            ],
        },
    ],

    # ================================================================
    # YEAR 5
    # ================================================================
    "year_5": [
        {
            "id": "y5_percentages",
            "topic": "Percentages",
            "nc_objective": "Recognise the per cent symbol and understand that per cent relates to number of parts per hundred.",
            "leo_intro": "Per cent means out of 100. So 50 percent means 50 out of every 100 — which is exactly half. 25 percent is a quarter. 10 percent is easy — just divide by 10. Once you know 10 percent you can work out most others.",
            "examples": {
                "football": "A goalkeeper saves 75 percent of shots. Out of every 100 shots — 75 are saved. A player completes 80 percent of his passes — 80 out of every 100 reach a teammate. Transfer fees are sometimes 10 percent agents fee — so a 100 million deal means 10 million to the agent.",
                "minecraft": "Your armour has 60 percent durability left. That means 60 out of 100 durability points remain. A crafting success rate of 85 percent means 85 out of 100 crafts succeed.",
                "animals": "70 percent of the Earth is covered in water. That's 70 out of every 100 parts. Only 30 percent is land. Of all species on Earth, scientists think 99 percent have gone extinct.",
                "space": "A rocket uses 90 percent of its fuel just to get off the ground. Only 10 percent is left for the actual journey. A mission has a 95 percent success rate — meaning 95 out of 100 similar missions succeeded.",
                "dinosaurs": "Scientists believe 75 percent of all species went extinct when the asteroid hit. That's 75 out of every 100 species — gone. Only 25 percent survived.",
                "default": "If a shop has 20 percent off, and something costs £100, you save £20. If it costs £50, you save £10 — because 10 percent of 50 is 5, and 20 percent is double that.",
            },
            "check_questions": {
                "football": "A goalkeeper faces 200 shots in a season and saves 75 percent of them. How many does he save?",
                "default": "What is 10 percent of 80? What is 20 percent of 80? And 50 percent?",
            },
            "common_mistakes": [
                "Thinking percent is the same as the actual number — 75% of 200 is not 75",
                "Forgetting that 10% means divide by 10",
            ],
        },
        {
            "id": "y5_negative_numbers",
            "topic": "Negative numbers",
            "nc_objective": "Interpret negative numbers in context, count forwards and backwards with positive and negative whole numbers through zero.",
            "leo_intro": "Negative numbers are below zero. Think of a thermometer — below freezing is negative. Or an underground car park — floor minus 1 is below ground level. They go in the opposite direction from positive numbers.",
            "examples": {
                "football": "A team's goal difference can be negative. If they've scored 5 goals but let in 8, their goal difference is minus 3. That's written as negative 3, or -3. They need to score 4 more than they concede just to get back to zero.",
                "minecraft": "In Minecraft, the deepest caves are at Y level minus 59 — that's 59 blocks below sea level. Diamonds spawn at around minus 58. So negative Y coordinates mean underground.",
                "animals": "The temperature at the Arctic is often minus 40 degrees. That's 40 degrees below freezing. Polar bears can survive it — we really can't.",
                "space": "In outer space, the temperature is minus 270 degrees Celsius. That's almost as cold as it gets — called absolute zero. Only 3 degrees off the coldest possible temperature.",
                "dinosaurs": "When the asteroid hit, temperatures dropped to minus 20 in some places due to debris blocking the sun. That's 20 degrees below freezing — even tropical dinosaurs faced freezing conditions.",
                "default": "In winter, the temperature might be minus 5 degrees. If it warms up by 8 degrees, what's the temperature now? Starting at -5 and going up 8: -5, -4, -3, -2, -1, 0, 1, 2, 3. It's now 3 degrees.",
            },
            "check_questions": {
                "football": "A team has a goal difference of minus 4. They then win 3 games scoring 2 goals in each and letting in 0. What is their new goal difference?",
                "default": "The temperature is minus 8 degrees. It warms up by 11 degrees. What is the temperature now?",
            },
            "common_mistakes": [
                "Thinking -8 is bigger than -3 because 8 is bigger than 3",
                "Getting confused about direction when adding or subtracting from negatives",
            ],
        },
    ],

    # ================================================================
    # YEAR 6
    # ================================================================
    "year_6": [
        {
            "id": "y6_ratio",
            "topic": "Ratio and proportion",
            "nc_objective": "Solve problems involving the relative sizes of two quantities where missing values can be found by using integer multiplication and division facts.",
            "leo_intro": "Ratio compares two amounts. 2 to 1 means for every 2 of one thing, there is 1 of another. Ratios are written with a colon — 2:1. To scale up a ratio, you multiply both sides by the same number.",
            "examples": {
                "football": "A coach says the ratio of defenders to attackers is 4 to 2 — written as 4:2. That simplifies to 2:1 — for every 2 defenders there's 1 attacker. If you have 8 defenders, how many attackers? Keep the ratio: 8:4 — so 4 attackers.",
                "minecraft": "A recipe needs iron and gold in a ratio of 3:1. For every 3 iron, 1 gold. If you have 12 iron, you need 4 gold. If you have 9 iron, you need 3 gold.",
                "animals": "In a wildlife park the ratio of lions to zebras is 1:6. For every 1 lion there are 6 zebras. If there are 4 lions, there are 24 zebras.",
                "space": "Rocket fuel needs oxygen and hydrogen in a ratio of 1:2. For every 1 part oxygen, 2 parts hydrogen. If you use 50kg of oxygen, you need 100kg of hydrogen.",
                "dinosaurs": "In a fossil bed, for every 1 T-Rex fossil there are 5 smaller dinosaur fossils — a ratio of 1:5. If you find 3 T-Rex fossils, how many smaller ones would you expect?",
                "default": "Orange squash is mixed with water in a ratio of 1:4. For every 1 part squash, 4 parts water. To make 5 cups, you need 1 cup of squash and 4 cups of water. To make 10 cups?",
            },
            "check_questions": {
                "football": "A team wins and loses games in a ratio of 3:1. If they played 20 games, how many did they win?",
                "default": "Cement is made with sand and gravel in a ratio of 2:3. If you use 10 bags of sand, how many bags of gravel do you need?",
            },
            "common_mistakes": [
                "Not applying the same multiplier to both sides",
                "Confusing ratio with fraction",
            ],
        },
        {
            "id": "y6_algebra",
            "topic": "Simple algebra",
            "nc_objective": "Use simple formulae; generate and describe linear number sequences; express missing number problems algebraically.",
            "leo_intro": "Algebra uses letters to stand for numbers we don't know yet. It's like a mystery number. If I say n plus 5 equals 12, n is the mystery number. To find it, we do the opposite — 12 minus 5 is 7. So n is 7.",
            "examples": {
                "football": "A player scores g goals per game. After 10 games he has scored 10 times g goals total. If he scored 30 goals in 10 games, then 10g equals 30, so g equals 3 goals per game.",
                "minecraft": "You earn x diamonds each level. After 8 levels you have 40 diamonds. So 8x equals 40. Divide both sides by 8: x equals 5. You earn 5 diamonds per level.",
                "animals": "A dog gains w kg per month. After 6 months it weighs 12kg more than when it started. So 6w equals 12. Divide by 6: w equals 2. It gains 2kg per month.",
                "space": "A rocket travels d km per second. In 5 seconds it travels 35km. So 5d equals 35. Divide by 5: d equals 7. The rocket travels 7km per second.",
                "dinosaurs": "A T-Rex eats m animals per day. In 7 days it eats 21 animals. So 7m equals 21. Divide by 7: m equals 3. It eats 3 animals per day.",
                "default": "A bag of sweets costs p pence. You buy 6 bags and spend 90p. So 6p equals 90. Divide by 6: p equals 15. Each bag costs 15p.",
            },
            "check_questions": {
                "football": "A player earns g pounds per goal. In a season he scores 20 goals and earns 60 pounds in bonuses. Write this as an equation and find g.",
                "default": "If 4n equals 28, what is n? Show your working.",
            },
            "common_mistakes": [
                "Trying to guess the number rather than using inverse operations",
                "Forgetting that whatever you do to one side you must do to the other",
            ],
        },
    ],
}


# ================================================================
# READING CURRICULUM — UK National Curriculum Year 2-6
# ================================================================

READING_CURRICULUM = {

    "year_2": [
        {
            "id": "y2_read_sequence",
            "topic": "Story sequence and order",
            "nc_objective": "Discuss the sequence of events in books and how items of information are related.",
            "leo_intro": "Stories have a beginning, a middle, and an end — just like a football match. Something happens first, then something happens because of that, and then the story comes to a conclusion. When we understand the order things happen in, we understand the story.",
            "examples": {
                "football": "Think about a match. It has a beginning — the teams line up and kick off. A middle — the action, the goals, the tension. And an end — the final whistle. If I told you 'they celebrated winning' before 'they played the match', that wouldn't make sense. The sequence matters.",
                "minecraft": "In Minecraft your day has a sequence too. You wake up, you mine, you build, night falls, monsters come, you survive or you don't. Each part happens because of the part before.",
                "animals": "A caterpillar's story has a clear sequence — egg, caterpillar, cocoon, butterfly. Mix those up and the story doesn't work. That's what sequence means in reading.",
                "default": "Every story has an order. First this, then that, then the ending. Good readers spot what happens, then what happens next, then why it ends the way it does.",
            },
            "check_questions": {
                "football": "In a football match story — the team train all week, then they play, then they win the trophy. Which part is the beginning, which is the middle, which is the end?",
                "default": "I'm going to describe three events from a story. Can you put them in the right order?",
            },
            "common_mistakes": [
                "Focusing only on the ending without understanding what led to it",
                "Missing cause and effect — this happened BECAUSE of that",
            ],
        },
        {
            "id": "y2_read_characters",
            "topic": "Understanding characters",
            "nc_objective": "Discuss and clarify the meanings of words, linking new meanings to known vocabulary.",
            "leo_intro": "Characters in stories have feelings, just like real people. Good readers try to understand why a character feels the way they do — and the clues are always in the text. We look for words that tell us how someone is feeling.",
            "examples": {
                "football": "If a story says 'the goalkeeper punched the air and shouted YES after the save' — how is he feeling? Excited, proud, relieved. We know because of what he does and says. That's how we read characters.",
                "minecraft": "If a character in a story 'sat in the corner, wouldn't speak, and stared at the floor' — how are they feeling? Sad, upset, maybe embarrassed. The author didn't say 'he was sad' but we know from the clues.",
                "animals": "If a story says 'the dog whimpered, tucked its tail between its legs, and backed away slowly' — how is the dog feeling? Scared. We can tell from the body language described in the words.",
                "default": "Authors don't always say 'she was angry'. They might say 'her face went red, she slammed the door and didn't speak all evening'. We have to be detectives and read the clues.",
            },
            "check_questions": {
                "football": "A story says: 'the striker walked slowly off the pitch, head down, ignoring his teammates'. How is he feeling, and how do you know?",
                "default": "If a character 'clapped her hands, jumped up and down, and couldn't stop smiling' — what is she feeling? What clues told you that?",
            },
            "common_mistakes": [
                "Just saying 'happy' or 'sad' without using evidence from the text",
            ],
        },
    ],

    "year_3": [
        {
            "id": "y3_inference",
            "topic": "Inference — reading between the lines",
            "nc_objective": "Draw inferences such as inferring characters' feelings, thoughts and motives from their actions.",
            "leo_intro": "Inference means figuring out something the author hasn't directly told you. Authors leave clues and trust you to work it out. It's like being a detective — the answer is always there, you just have to find it.",
            "examples": {
                "football": "If a match report says 'the home fans went quiet after the 89th minute goal' — it doesn't say they were devastated. But we can infer they were. The clue is them going quiet so late in the game. That's inference.",
                "minecraft": "If a story says 'the player had been underground for days. When they finally surfaced they shielded their eyes' — we can infer it was bright outside after so long in the dark. The author didn't say it — we worked it out.",
                "animals": "If a text says 'the rabbit froze, its ears pointed straight up, its nose twitching rapidly' — we can infer it sensed danger. We're inferring from what its body is doing.",
                "space": "A space story says 'the astronaut checked the fuel gauge three times before takeoff'. We can infer she was nervous or being extremely careful. Nothing said 'she was nervous'.",
                "default": "A character 'checked the clock every five minutes, kept looking at the door, and couldn't sit still'. We can infer they are waiting for something important or someone they really want to see.",
            },
            "check_questions": {
                "football": "A football story says 'the manager sat alone in the dressing room long after everyone had left'. What can you infer about how he's feeling, and what clues support that?",
                "default": "A story says 'Maya put the birthday card away quickly when she heard footsteps on the stairs'. What can we infer and how do we know?",
            },
            "common_mistakes": [
                "Making inferences not supported by the text — always need textual evidence",
                "Confusing what we're told directly with what we have to work out",
            ],
        },
    ],

    "year_4": [
        {
            "id": "y4_summarise",
            "topic": "Summarising and main idea",
            "nc_objective": "Identify main ideas drawn from more than one paragraph and summarise these.",
            "leo_intro": "Summarising means picking out the most important information and saying it in fewer words. Not every detail matters. A good summary gets the key point across quickly — like a match report headline rather than the full article.",
            "examples": {
                "football": "A 500-word match report might tell you every tackle and every chance. But the summary is: 'Liverpool won 2-1 in the 90th minute thanks to a Salah penalty'. That's the main idea. Everything else is detail.",
                "minecraft": "Imagine a long tutorial about building a house. The summary is: gather wood, build walls, add a roof, put in a door. That's the core of it. All the other steps are detail to support those main points.",
                "animals": "A long article about migration might describe individual animals, weather patterns, exact dates. The main idea is: some animals travel thousands of miles each year to find food and warmer weather.",
                "default": "When you summarise, ask yourself: what is this mainly about? If I had to explain it to someone in 2 sentences, what would I say? That forces you to find the main idea.",
            },
            "check_questions": {
                "football": "I'm going to describe a football match in detail. You tell me the main idea in one sentence.",
                "default": "Read this paragraph and tell me the main point in your own words.",
            },
            "common_mistakes": [
                "Including too much detail in a summary",
                "Missing the actual main point and focusing on interesting details instead",
            ],
        },
    ],

    "year_5": [
        {
            "id": "y5_language_effects",
            "topic": "Language choices and their effects",
            "nc_objective": "Discuss and evaluate how authors use language, including figurative language, considering the impact on the reader.",
            "leo_intro": "Authors choose every word on purpose. They think about the effect it will have on you as a reader. A word like 'stormed' tells you so much more than 'walked'. Metaphors, similes, and powerful verbs are all tools authors use to make you feel something.",
            "examples": {
                "football": "A match report could say 'he ran fast'. Instead it says 'he blazed past the defender like a thunderbolt'. The word 'blazed' and the simile 'like a thunderbolt' make you feel the speed. That's deliberate language choice.",
                "minecraft": "A story says 'the cave was dark'. Or it could say 'the cave swallowed them whole, its darkness pressing in from all sides'. The second version makes you feel trapped. Same information, completely different effect.",
                "animals": "A nature documentary might say 'the cheetah ran towards the deer'. Or it might say 'the cheetah launched itself like a missile, the ground a blur beneath it'. Which one makes your heart beat faster?",
                "default": "The word 'whispered' tells you it was quiet and possibly secretive. The word 'hissed' tells you it was quiet but angry. Authors pick between words like these on purpose to make you feel a certain way.",
            },
            "check_questions": {
                "football": "Which is more powerful: 'the crowd was loud' or 'the crowd roared like a storm breaking'? What is the effect of each?",
                "default": "Why might an author choose the word 'crumbled' instead of 'fell' to describe someone sitting down?",
            },
            "common_mistakes": [
                "Spotting the technique (simile, metaphor) without explaining the EFFECT on the reader",
                "Just saying 'it makes it more interesting' — need to be specific about the effect",
            ],
        },
    ],

    "year_6": [
        {
            "id": "y6_complex_inference",
            "topic": "Complex inference and deduction",
            "nc_objective": "Make comparisons within and across books; distinguish between statements of fact and opinion.",
            "leo_intro": "At Year 6 level, inference gets more complex. You're reading between the lines AND explaining exactly which words or phrases support your idea. Every inference needs evidence. It's the difference between a good reader and a great one.",
            "examples": {
                "football": "A tactical analysis says 'the manager selected five defensive players and kept a deep defensive line'. We can infer from this that he was prioritising not conceding over scoring. The evidence is 'five defensive players' and 'deep defensive line'.",
                "minecraft": "A story says 'the player had spent weeks fortifying the base — triple walls, traps at every entrance, hidden chests for valuables. And still, every morning, she checked the perimeter before doing anything else'. We can infer she had been attacked badly before. The evidence is the extreme level of preparation.",
                "animals": "A wildlife text says 'the pack has been seen near human settlements three times this month, always at dusk when bins are being emptied'. We can infer their natural food supply is failing. The evidence is the pattern of timing and location.",
                "default": "A letter says 'I have thought very carefully before writing this'. We can infer the writer is being cautious about what they say and expects it to matter. The word 'carefully' and 'before writing' are our evidence.",
            },
            "check_questions": {
                "football": "A text says 'the captain avoided eye contact with the manager after the match and was first out of the stadium'. What can we infer and what is the evidence?",
                "default": "What is the difference between a fact and an opinion? Give me an example of each.",
            },
            "common_mistakes": [
                "Making an inference without citing the specific evidence",
                "Treating opinion as fact in texts",
            ],
        },
    ],
}


# ================================================================
# CODING LOGIC CURRICULUM — UK National Curriculum Computing Year 2-6
# ================================================================

CODING_CURRICULUM = {

    "year_2": [
        {
            "id": "y2_algorithms",
            "topic": "Algorithms — step by step instructions",
            "nc_objective": "Understand what algorithms are; how they are implemented as programs on digital devices.",
            "leo_intro": "An algorithm is just a set of step-by-step instructions to do something. You follow algorithms every day — getting ready for school, making toast, playing a game. The key thing is that every step has to be in the right order and clear enough that anyone could follow it.",
            "examples": {
                "football": "How does a footballer take a penalty? That's an algorithm. Step 1: place the ball on the spot. Step 2: take a run-up. Step 3: decide where to aim. Step 4: kick the ball. Step 5: follow through. If you mix up those steps — say you kick before placing — it doesn't work.",
                "minecraft": "How do you mine diamonds in Minecraft? That's an algorithm. Step 1: craft a pickaxe. Step 2: dig down to level 11. Step 3: mine horizontally. Step 4: look for diamond ore. Step 5: mine it. Step 6: collect the diamonds. Order matters.",
                "animals": "How does a spider build a web? That's nature's algorithm. It always follows the same steps in the same order. Start at the centre, add spokes outward, then spiral inward. If it changed the order, the web wouldn't hold.",
                "space": "A rocket launch is an algorithm. T-minus 10, check systems. T-minus 5, start engines. T-zero, release clamps. T-plus 1, full thrust. Every step in order, every time.",
                "default": "Making a sandwich is an algorithm. Step 1: get two slices of bread. Step 2: spread butter. Step 3: add filling. Step 4: put the slices together. Step 5: cut in half. Change the order and you get a mess.",
            },
            "check_questions": {
                "football": "Write me an algorithm for getting ready to play football. What are the steps? Does the order matter?",
                "default": "If I wrote an algorithm for making toast but put 'put bread in toaster' AFTER 'press the button' — what would go wrong?",
            },
            "common_mistakes": [
                "Steps that are too vague — 'do the thing' is not a clear instruction",
                "Missing steps that seem obvious but a computer wouldn't assume",
            ],
        },
        {
            "id": "y2_sequences",
            "topic": "Sequences and precise instructions",
            "nc_objective": "Create and debug simple programs; use logical reasoning to predict the behaviour of simple programs.",
            "leo_intro": "A sequence is instructions that happen one after another in order. Computers follow sequences exactly — they don't assume anything. If you leave out a step or get the order wrong, the computer does the wrong thing. Precision matters.",
            "examples": {
                "football": "Imagine programming a robot footballer. You tell it: move forward, stop, kick. If you say 'kick' before 'move forward' the robot kicks air. Computers are literal — they do exactly what you say, nothing more.",
                "minecraft": "If you program a Minecraft bot: dig down 10 blocks, turn right, dig 5 blocks. If you miss 'turn right' it just keeps digging down forever. The sequence has to be exact.",
                "animals": "A bee follows a sequence to make honey. Collect nectar — fly back to hive — pass it to a worker bee — wait for it to dry — seal with wax. Miss one step and there's no honey.",
                "default": "A sequence in coding is like a recipe. Miss 'add eggs' from a cake recipe and the cake won't hold together. Computers are the same — they need every step.",
            },
            "check_questions": {
                "football": "I've written instructions for a robot: 'kick the ball, run to the ball, pick up the ball'. What's wrong with this sequence?",
                "default": "Can you spot the mistake in this sequence: 'put on shoes, put on socks, tie laces'?",
            },
            "common_mistakes": [
                "Assuming the computer will use common sense — it won't",
                "Steps in wrong order",
            ],
        },
    ],

    "year_3": [
        {
            "id": "y3_conditionals",
            "topic": "Conditionals — if and else",
            "nc_objective": "Use sequence, selection, and repetition in programs; work with variables and various forms of input and output.",
            "leo_intro": "A conditional is an IF statement. IF something is true, do this. ELSE do something different. Computers make decisions using conditionals all the time. Games are full of them — IF the player has enough lives, continue. ELSE game over.",
            "examples": {
                "football": "In a match: IF the ball goes over the goal line AND into the net — goal is given. ELSE the game continues. IF it's full time AND the score is level — extra time. ELSE the winner is declared. Football runs on conditionals.",
                "minecraft": "In Minecraft: IF it gets dark — monsters spawn. ELSE it stays safe. IF you touch lava — you die. ELSE you keep playing. IF you have 3 diamonds AND a crafting table — you can make a sword. ELSE you can't.",
                "animals": "Animal behaviour is full of conditionals. IF a rabbit sees a fox — RUN. ELSE graze normally. IF the bear is hungry AND there are fish in the river — fish. ELSE keep walking.",
                "space": "A spacecraft: IF fuel is above 20 percent — continue mission. ELSE abort and return. IF oxygen levels drop below safe level — emergency protocol starts. These are the actual rules programmed into spacecraft.",
                "default": "A traffic light: IF the light is green — go. ELSE if the light is amber — slow down. ELSE if the light is red — stop. That's a conditional with multiple options.",
            },
            "check_questions": {
                "football": "Write an IF/ELSE statement for what happens IF a player commits a foul inside the penalty area.",
                "minecraft": "Can you write a conditional for what happens in Minecraft IF it starts raining?",
                "default": "Create an IF/ELSE for what you do IF it is raining when you wake up.",
            },
            "common_mistakes": [
                "Forgetting the ELSE — what happens when the condition is NOT true",
                "Conditions that overlap or are impossible to satisfy",
            ],
        },
        {
            "id": "y3_loops",
            "topic": "Loops — repeating instructions",
            "nc_objective": "Use repetition in programs.",
            "leo_intro": "A loop is when you repeat the same instructions multiple times without writing them out over and over. Instead of writing 'kick ball' 50 times, you write 'repeat 50 times: kick ball'. Loops make code shorter and smarter.",
            "examples": {
                "football": "A training drill: repeat 20 times — sprint to the cone, touch it, sprint back. Instead of writing those instructions 20 times, we use a loop. REPEAT 20 TIMES: sprint to cone, touch cone, sprint back.",
                "minecraft": "Mining a tunnel: REPEAT until wall reached — mine 1 block forward. You don't know exactly how many blocks until you hit the end. The loop keeps going until the condition is met.",
                "animals": "A woodpecker REPEATS — peck tree, check for insects, peck again — until it finds food. That's a loop. It keeps repeating the same action until something changes.",
                "space": "A satellite: REPEAT every 90 minutes — transmit data back to Earth, receive new instructions, adjust orbit slightly. That loop runs for years.",
                "default": "Washing your hair: REPEAT TWICE — apply shampoo, massage, rinse. The bottle says 'repeat' — that's a loop.",
            },
            "check_questions": {
                "football": "A player does free kick practice. They kick 10 times, rest, kick 10 times, rest, kick 10 times. Write this as a loop.",
                "default": "What's the difference between a loop that runs 5 times and a loop that runs UNTIL something happens?",
            },
            "common_mistakes": [
                "Infinite loops — forgetting to tell the loop when to stop",
                "Off-by-one errors — loop runs one too many or too few times",
            ],
        },
        {
            "id": "y3_debugging",
            "topic": "Debugging — finding and fixing errors",
            "nc_objective": "Use logical reasoning to detect and correct errors in algorithms and programs.",
            "leo_intro": "Debugging means finding what's wrong in a program and fixing it. Every programmer does it — even the best ones in the world. The skill is being systematic: test, find the error, understand why, fix it, test again.",
            "examples": {
                "football": "A VAR review is debugging. The referee thought it was a goal — but we test it (look at the footage), find the error (the player was offside), understand why (their foot was past the last defender), fix it (disallow the goal), check again (confirmed).",
                "minecraft": "Your Minecraft farm isn't working. You test it — no crops growing. Find the error — no water near the soil. Understand why — crops need water within 4 blocks. Fix it — add water channel. Test — crops grow.",
                "animals": "A scientist's experiment isn't working. They test it, look for what's wrong, try to understand why it failed, make a change, and test again. That's the scientific method — which is basically debugging.",
                "default": "Your alarm didn't go off. You test it — press the button, nothing happens. Find the error — it's set to PM not AM. Understand why — you accidentally changed it. Fix — set it correctly. Test — alarm goes off.",
            },
            "check_questions": {
                "football": "Here's a broken algorithm for a penalty: 'kick ball, place ball on spot, take run-up'. What's the bug? How would you fix it?",
                "default": "A loop says REPEAT 3 TIMES: print 'hello'. But the word 'hello' appears 4 times. What's the bug?",
            },
            "common_mistakes": [
                "Changing multiple things at once — you can't tell which fix worked",
                "Not testing after each fix",
            ],
        },
    ],

    "year_4": [
        {
            "id": "y4_variables",
            "topic": "Variables — boxes that hold values",
            "nc_objective": "Use variables in programs.",
            "leo_intro": "A variable is like a labelled box. You put a value in the box, give it a name, and you can use that name throughout your program. The value can change — that's why it's called a variable. Score is a variable. Lives is a variable. Name is a variable.",
            "examples": {
                "football": "In a football game program: score = 0. Every time a goal is scored: score = score + 1. The box called 'score' updates. At any point you can check the box to see the current score. That's a variable.",
                "minecraft": "In Minecraft your inventory is full of variables. diamonds = 0. Every time you mine one: diamonds = diamonds + 1. Your health is a variable: health = 20. Every hit: health = health - 2.",
                "animals": "A wildlife tracking program: number_of_lions = 47. Each month they count again and update the variable. It might go up or down. The label 'number_of_lions' stays the same — but the value inside changes.",
                "space": "A rocket program: fuel = 100. Every second the engine runs: fuel = fuel - 1. When fuel = 0: engines stop. The variable tracks the changing value throughout the mission.",
                "default": "A game has lives = 3. Each time you die: lives = lives - 1. When lives = 0: game over. The variable 'lives' starts at 3 and decreases. The name 'lives' stays the same, the number inside it changes.",
            },
            "check_questions": {
                "football": "A game starts with score = 0. Three goals are scored. Write out how the variable changes each time.",
                "default": "Why is a variable called a 'variable'? What makes it different from a fixed number?",
            },
            "common_mistakes": [
                "Confusing the variable name with the value stored in it",
                "Forgetting that score = score + 1 means 'take the current value, add 1, store it back'",
            ],
        },
    ],

    "year_5": [
        {
            "id": "y5_decomposition",
            "topic": "Decomposition — breaking problems down",
            "nc_objective": "Understand several key algorithms that reflect computational thinking.",
            "leo_intro": "Decomposition means breaking a big, complicated problem into smaller, manageable pieces. Instead of trying to solve everything at once, you deal with one bit at a time. All large programs are built this way — piece by piece.",
            "examples": {
                "football": "Building a football management video game is huge. But break it down: player stats, match engine, transfer system, training, finances, fans. Then break each one down further. Player stats: name, position, speed, passing, shooting. Each small piece is manageable.",
                "minecraft": "Building a survival base seems overwhelming. Break it down: shelter first, then food source, then storage, then lighting, then defences, then expansion. Each part is its own project. Tackle them one at a time.",
                "animals": "How does a nature documentary get made? Break it down: research the animal, find a location, set up cameras, film, edit, add narration, release. Each stage is its own task. Decompose the big problem.",
                "space": "A moon landing: break into launch phase, transit phase, lunar orbit, landing, surface operations, return. Engineers work on each phase separately. Then they combine them.",
                "default": "Planning a party: venue, food, invitations, decorations, entertainment, timing. That's decomposition. You don't try to do everything at once — you solve each part separately then put it all together.",
            },
            "check_questions": {
                "football": "I want to build a website that shows live Premier League scores. Decompose that into its main parts.",
                "default": "What is the difference between decomposition and just making a to-do list?",
            },
            "common_mistakes": [
                "Breaking things down too much — some things should stay together",
                "Forgetting that the pieces eventually need to connect back together",
            ],
        },
    ],

    "year_6": [
        {
            "id": "y6_boolean_logic",
            "topic": "Boolean logic — AND, OR, NOT",
            "nc_objective": "Understand how instructions are stored and executed within a computer system; understand how data is represented.",
            "leo_intro": "Boolean logic uses AND, OR, and NOT to combine conditions. AND means both conditions must be true. OR means at least one must be true. NOT flips the result. Everything in computing runs on these three operations.",
            "examples": {
                "football": "A goal counts IF the ball crosses the line AND the player was onside AND no foul was committed. All three must be true — that's AND logic. A penalty is given IF there was a foul inside the box OR the goalkeeper handled it outside the box. Either one is enough — that's OR.",
                "minecraft": "You can enter the Nether IF you have a flint AND steel AND obsidian frame. All three needed — AND logic. You die IF you fall into lava OR a creeper explodes next to you OR you run out of health. Any one of those kills you — OR logic.",
                "animals": "A cat will come inside IF it is cold OR raining OR dark. Any one of those conditions is enough — OR. A chameleon changes colour IF it is stressed AND on a surface AND the temperature is right — it needs all three conditions — AND.",
                "space": "A spacecraft aborts IF fuel is low OR systems fail OR mission control says abort. Any one is enough — OR. A spacewalk happens IF weather is stable AND oxygen systems are working AND crew are physically ready — all three needed — AND.",
                "default": "You can buy a game IF you have enough money AND your parents say yes AND the shop has stock. All three — AND logic. You can get to school IF you take the bus OR your parents drive you OR you walk. Any one works — OR logic.",
            },
            "check_questions": {
                "football": "Offside: a player is offside IF they are nearer the goal than the ball AND nearer the goal than the second-to-last defender. Is this AND or OR logic? And what happens if only ONE of those conditions is true?",
                "default": "Create an AND statement and an OR statement about something you do every day. Explain the difference.",
            },
            "common_mistakes": [
                "Confusing AND with OR — AND is stricter (both must be true), OR is more permissive (either works)",
                "Forgetting that NOT flips the result entirely",
            ],
        },
    ],
}


# ================================================================
# DIFFICULTY LEVELS — used for parent accuracy tracking
# ================================================================

TOPIC_DIFFICULTY = {
    # Year 2 = 1 (green/easy)
    "y2_add_2digit": 1, "y2_subtract_2digit": 1, "y2_times2": 1,
    "y2_times5": 1, "y2_times10": 1, "y2_fractions_half": 1,
    "y2_read_sequence": 1, "y2_read_characters": 1,
    "y2_algorithms": 1, "y2_sequences": 1,

    # Year 3 = 2 (yellow/medium)
    "y3_times3": 2, "y3_times4": 2, "y3_times8": 2,
    "y3_fractions": 2, "y3_time": 2,
    "y3_inference": 2,
    "y3_conditionals": 2, "y3_loops": 2, "y3_debugging": 2,

    # Year 4 = 2 (yellow/medium)
    "y4_times6": 2, "y4_times7": 2, "y4_decimals": 2, "y4_area_perimeter": 2,
    "y4_summarise": 2,
    "y4_variables": 2,

    # Year 5 = 3 (violet/hard)
    "y5_percentages": 3, "y5_negative_numbers": 3,
    "y5_language_effects": 3,
    "y5_decomposition": 3,

    # Year 6 = 3 (violet/hard)
    "y6_ratio": 3, "y6_algebra": 3,
    "y6_complex_inference": 3,
    "y6_boolean_logic": 3,
}


def get_topic_difficulty(topic_id):
    """Return 1=easy/green, 2=medium/yellow, 3=hard/violet."""
    return TOPIC_DIFFICULTY.get(topic_id, 1)


def get_curriculum_with_difficulty(year_group, subject):
    """Same as get_curriculum but each topic includes difficulty_level."""
    topics = get_curriculum(year_group, subject)
    for t in topics:
        t['difficulty_level'] = get_topic_difficulty(t['id'])
    return topics
