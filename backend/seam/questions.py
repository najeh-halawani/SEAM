"""Bilingual diagnostic question bank aligned with the six SEAM dysfunction categories.

Each category contains:
- opening questions (used to introduce the topic)
- probing questions (used as follow-ups to deepen responses)
- closing questions (used to wrap up the category)

All questions are provided in English and Arabic.
Probing questions are expanded to enable deeper, role-adapted interviews.
"""

QUESTION_BANK = {
    # ───────────────────── 1. Strategic Implementation ─────────────────────
    "strategic_implementation": {
        "opening": [
            {
                "en": "Do you have a clear idea of what the company's top priorities are right now, and what your team is supposed to focus on?",
                "ar": "هل لديك فكرة واضحة عن ماهية الأولويات القصوى للشركة حالياً، وما يفترض بفريقك التركيز عليه؟"
            },
            {
                "en": "Do you feel that your daily work actually contributes to the company's big goals, or does it feel disconnected?",
                "ar": "هل تشعر أن عملك اليومي يساهم فعلاً في تحقيق أهداف الشركة الكبرى، أم تشعر أنه منفصل عنها؟"
            },
        ],
        "probing": [
            {
                "en": "Can you give a specific example of when strategic priorities were unclear or changed unexpectedly?",
                "ar": "هل يمكنك إعطاء مثال محدد عندما كانت الأولويات الاستراتيجية غير واضحة أو تغيرت بشكل غير متوقع؟"
            },
            {
                "en": "How does this lack of clarity affect your day-to-day work?",
                "ar": "كيف يؤثر عدم الوضوح هذا على عملك اليومي؟"
            },
            {
                "en": "What do you think could be done differently to improve strategic alignment?",
                "ar": "ما الذي تعتقد أنه يمكن القيام به بشكل مختلف لتحسين التوافق الاستراتيجي؟"
            },
            {
                "en": "Have you experienced situations where a project or initiative was launched and then abandoned? What happened?",
                "ar": "هل مررت بمواقف تم فيها إطلاق مشروع أو مبادرة ثم التخلي عنها؟ ماذا حدث؟"
            },
            {
                "en": "Do you feel that management decisions reflect a long-term plan, or do things feel more reactive?",
                "ar": "هل تشعر أن قرارات الإدارة تعكس خطة طويلة المدى، أم أن الأمور تبدو أكثر ردود أفعال آنية؟"
            },
            {
                "en": "How are performance goals or KPIs communicated in your area? Do they feel meaningful to your work?",
                "ar": "كيف يتم إيصال أهداف الأداء أو مؤشراته في مجال عملك؟ هل تشعر أنها ذات معنى لعملك؟"
            },
            {
                "en": "When strategic confusion happens, how much time would you say gets wasted — per week — on rework, waiting for directions, or doing things that end up being scrapped?",
                "ar": "عندما يحدث ارتباك استراتيجي، كم من الوقت تعتقد أنه يضيع أسبوعياً على إعادة العمل أو انتظار التوجيهات أو القيام بأشياء ينتهي بها الأمر بالإلغاء؟"
            },
            {
                "en": "Have you seen people leave the organization — or think about leaving — because of unclear direction or broken promises? How common is that?",
                "ar": "هل رأيت أشخاصاً يغادرون المنظمة — أو يفكرون في المغادرة — بسبب عدم وضوح الاتجاه أو الوعود المكسورة؟ ما مدى شيوع ذلك؟"
            },
        ],
        "closing": [
            {
                "en": "Is there anything else you would like to share about the organization's strategic direction?",
                "ar": "هل هناك أي شيء آخر تود مشاركته حول التوجه الاستراتيجي للمنظمة؟"
            },
        ],
    },

    # ───────────────────── 2. Working Conditions ──────────────────────────
    "working_conditions": {
        "opening": [
            {
                "en": "How would you describe your current working conditions — both the physical environment and the general atmosphere?",
                "ar": "كيف تصف ظروف عملك الحالية — سواء البيئة المادية أو الأجواء العامة؟"
            },
            {
                "en": "Do you feel you have the tools and resources you need to do your job effectively?",
                "ar": "هل تشعر أن لديك الأدوات والموارد التي تحتاجها للقيام بعملك بفعالية؟"
            },
        ],
        "probing": [
            {
                "en": "Can you describe a situation where working conditions made it difficult to perform your tasks?",
                "ar": "هل يمكنك وصف موقف حيث جعلت ظروف العمل من الصعب أداء مهامك؟"
            },
            {
                "en": "How do you feel your workload compares to what is reasonable?",
                "ar": "كيف تشعر أن حجم عملك يقارن بما هو معقول؟"
            },
            {
                "en": "What aspects of your working conditions would you most like to see improved?",
                "ar": "ما هي جوانب ظروف عملك التي تود أكثر أن ترى تحسناً فيها؟"
            },
            {
                "en": "Do you feel psychologically safe to express concerns or disagree with a decision at work?",
                "ar": "هل تشعر بالأمان النفسي للتعبير عن مخاوفك أو الاعتراض على قرار في العمل؟"
            },
            {
                "en": "Has there been a time when the lack of proper equipment or resources affected the quality of your output?",
                "ar": "هل كان هناك وقت أثر فيه نقص المعدات أو الموارد المناسبة على جودة عملك؟"
            },
            {
                "en": "How do you feel about the recognition and appreciation you receive for your work?",
                "ar": "كيف تشعر تجاه التقدير الذي تتلقاه على عملك؟"
            },
            {
                "en": "When tools break down or resources are missing, how often does that happen — and roughly how much time do you lose each time working around it?",
                "ar": "عندما تتعطل الأدوات أو تنقص الموارد، كم مرة يحدث ذلك — وتقريباً كم من الوقت تخسره في كل مرة بسبب الحلول البديلة؟"
            },
            {
                "en": "Have poor working conditions ever led to sick days, stress leave, or people calling in absent more often? What patterns have you noticed?",
                "ar": "هل أدت ظروف العمل السيئة إلى أيام مرضية أو إجازات إجهاد أو غياب الناس بشكل أكثر؟ ما الأنماط التي لاحظتها؟"
            },
            {
                "en": "If there's one thing about your working conditions that frustrates you the most, what is it?",
                "ar": "إذا كان هناك شيء واحد في ظروف عملك يحبطك أكثر من غيره، فما هو؟"
            },
        ],
        "closing": [
            {
                "en": "Is there anything else you'd like to mention about your working environment?",
                "ar": "هل هناك أي شيء آخر تود ذكره عن بيئة عملك؟"
            },
        ],
    },

    # ───────────────────── 3. Work Organization ───────────────────────────
    "work_organization": {
        "opening": [
            {
                "en": "How clear is your role within the organization, and do you feel the boundaries of your responsibilities are well-defined?",
                "ar": "ما مدى وضوح دورك داخل المنظمة، وهل تشعر أن حدود مسؤولياتك محددة بشكل جيد؟"
            },
            {
                "en": "How would you describe the way work processes are organized in your department?",
                "ar": "كيف تصف الطريقة التي تنظم بها عمليات العمل في قسمك؟"
            },
        ],
        "probing": [
            {
                "en": "Can you give an example of a situation where unclear responsibilities caused problems?",
                "ar": "هل يمكنك إعطاء مثال على موقف حيث تسببت المسؤوليات غير الواضحة في مشاكل؟"
            },
            {
                "en": "Do you encounter situations where decisions get delayed because of unclear authority?",
                "ar": "هل تواجه مواقف تتأخر فيها القرارات بسبب عدم وضوح السلطة؟"
            },
            {
                "en": "What changes in how work is organized would make the biggest difference for you?",
                "ar": "ما التغييرات في كيفية تنظيم العمل التي ستحدث أكبر فرق بالنسبة لك؟"
            },
            {
                "en": "Have you noticed tasks being duplicated — two people or teams doing essentially the same thing?",
                "ar": "هل لاحظت تكرار المهام — شخصان أو فريقان يقومان بالشيء نفسه أساساً؟"
            },
            {
                "en": "Do you feel there is too much bureaucracy or too many approval steps for routine decisions?",
                "ar": "هل تشعر أن هناك بيروقراطية مفرطة أو خطوات موافقة كثيرة للقرارات الروتينية؟"
            },
            {
                "en": "Has your role expanded beyond what you were originally hired or assigned to do? How does that affect you?",
                "ar": "هل توسع دورك إلى ما هو أبعد مما تم تعيينك للقيام به أصلاً؟ كيف يؤثر ذلك عليك؟"
            },
            {
                "en": "When work is disorganized or tasks fall through the cracks, how often does someone have to redo the work? Roughly how much time does that cost per week?",
                "ar": "عندما يكون العمل غير منظم أو تسقط المهام بين الشقوق، كم مرة يتعين على شخص ما إعادة العمل؟ تقريباً كم من الوقت يكلف ذلك أسبوعياً؟"
            },
            {
                "en": "Are there problems in your area that everyone knows about but nobody talks about openly? What's holding people back from raising them?",
                "ar": "هل هناك مشاكل في مجالك يعرفها الجميع لكن لا أحد يتحدث عنها علناً؟ ما الذي يمنع الناس من إثارتها؟"
            },
        ],
        "closing": [
            {
                "en": "Is there anything else about how work is structured or organized that you would like to share?",
                "ar": "هل هناك أي شيء آخر حول كيفية هيكلة أو تنظيم العمل تود مشاركته؟"
            },
        ],
    },

    # ───────────────────── 4. Time Management ─────────────────────────────
    "time_management": {
        "opening": [
            {
                "en": "How do you feel about the way your time is used during a typical workday?",
                "ar": "كيف تشعر حيال الطريقة التي يُستخدم بها وقتك خلال يوم عمل نموذجي؟"
            },
            {
                "en": "Do you feel you have enough time to complete your important tasks without constant pressure?",
                "ar": "هل تشعر أن لديك وقتاً كافياً لإنجاز مهامك المهمة دون ضغط مستمر؟"
            },
        ],
        "probing": [
            {
                "en": "What takes up most of your time during the day, and do you think that's the best use of your time?",
                "ar": "ما الذي يستغرق معظم وقتك خلال اليوم، وهل تعتقد أن ذلك هو أفضل استخدام لوقتك؟"
            },
            {
                "en": "How often are you interrupted during tasks that require your full attention?",
                "ar": "كم مرة تُقاطع أثناء المهام التي تتطلب انتباهك الكامل؟"
            },
            {
                "en": "Can you describe a recent situation where time pressure led to a problem or reduced quality?",
                "ar": "هل يمكنك وصف موقف حديث حيث أدى ضغط الوقت إلى مشكلة أو تقليل الجودة؟"
            },
            {
                "en": "Do you feel that meetings are a good use of your time, or are there too many that don't produce results?",
                "ar": "هل تشعر أن الاجتماعات هي استخدام جيد لوقتك، أم أن هناك الكثير منها لا يحقق نتائج؟"
            },
            {
                "en": "Does your work often encroach on your personal or family time? How does that make you feel?",
                "ar": "هل يتعدى عملك غالباً على وقتك الشخصي أو العائلي؟ كيف يشعرك ذلك؟"
            },
            {
                "en": "Would you say your daily work is mostly planned and proactive, or mostly responding to urgent issues?",
                "ar": "هل تقول أن عملك اليومي مخطط ومبادر في الغالب، أم أنه استجابة للمشاكل العاجلة في الغالب؟"
            },
            {
                "en": "If you had to estimate, how many hours per week do you spend on things that feel like wasted time — unnecessary meetings, redoing work, waiting on approvals, chasing information?",
                "ar": "إذا كان عليك التقدير، كم ساعة في الأسبوع تقضيها على أشياء تشعر أنها وقت ضائع — اجتماعات غير ضرورية، إعادة العمل، انتظار الموافقات، البحث عن معلومات؟"
            },
            {
                "en": "What's the biggest time-killer in your work that you wish someone would fix?",
                "ar": "ما هو أكبر مضيع للوقت في عملك وتتمنى لو أن شخصاً ما يصلحه؟"
            },
        ],
        "closing": [
            {
                "en": "Is there anything else you'd like to share about how time is managed in your area?",
                "ar": "هل هناك أي شيء آخر تود مشاركته حول كيفية إدارة الوقت في مجالك؟"
            },
        ],
    },

    # ──────────── 5. Communication, Coordination & Cooperation ────────────
    "communication_coordination_cooperation": {
        "opening": [
            {
                "en": "How would you describe the quality of communication within your team and across departments?",
                "ar": "كيف تصف جودة التواصل داخل فريقك وعبر الأقسام؟"
            },
            {
                "en": "Do you feel that information reaches you in a timely and useful manner?",
                "ar": "هل تشعر أن المعلومات تصل إليك في الوقت المناسب وبطريقة مفيدة؟"
            },
        ],
        "probing": [
            {
                "en": "Can you share an example where poor communication or coordination caused a problem?",
                "ar": "هل يمكنك مشاركة مثال حيث تسبب ضعف التواصل أو التنسيق في مشكلة؟"
            },
            {
                "en": "How well do different departments or teams cooperate when they need to work together?",
                "ar": "ما مدى تعاون الأقسام أو الفرق المختلفة عندما يحتاجون للعمل معاً؟"
            },
            {
                "en": "Do you receive regular feedback on your work? From whom?",
                "ar": "هل تتلقى تغذية راجعة منتظمة على عملك؟ ممن؟"
            },
            {
                "en": "Do you feel comfortable raising concerns or disagreements with your manager or peers? Why or why not?",
                "ar": "هل تشعر بالراحة في طرح المخاوف أو الخلافات مع مديرك أو زملائك؟ لماذا أو لماذا لا؟"
            },
            {
                "en": "Is communication mostly top-down, or do employees have channels to share ideas upward?",
                "ar": "هل التواصل في الغالب من أعلى لأسفل، أم أن للموظفين قنوات لمشاركة الأفكار صعوداً؟"
            },
            {
                "en": "When conflicts arise between colleagues or teams, how are they usually handled?",
                "ar": "عندما تنشأ خلافات بين الزملاء أو الفرق، كيف يتم التعامل معها عادةً؟"
            },
            {
                "en": "When communication breaks down, what's the typical consequence — delays, mistakes, duplicated work? How often would you say this happens?",
                "ar": "عندما ينهار التواصل، ما النتيجة النموذجية — تأخيرات، أخطاء، عمل مكرر؟ كم مرة تقول إن هذا يحدث؟"
            },
            {
                "en": "Is there something about how things work here that you've been wanting to say but haven't had the chance to?",
                "ar": "هل هناك شيء حول كيفية سير الأمور هنا كنت تريد قوله لكن لم تتح لك الفرصة؟"
            },
        ],
        "closing": [
            {
                "en": "Is there anything else you'd like to add about communication, coordination, or teamwork?",
                "ar": "هل هناك أي شيء آخر تود إضافته حول التواصل أو التنسيق أو العمل الجماعي؟"
            },
        ],
    },

    # ───────────────────── 6. Integrated Training ─────────────────────────
    "integrated_training": {
        "opening": [
            {
                "en": "How would you describe the training and development opportunities available to you?",
                "ar": "كيف تصف فرص التدريب والتطوير المتاحة لك؟"
            },
            {
                "en": "Do you feel adequately prepared and supported to handle your current responsibilities?",
                "ar": "هل تشعر أنك مستعد ومدعوم بشكل كافٍ للتعامل مع مسؤولياتك الحالية؟"
            },
        ],
        "probing": [
            {
                "en": "Can you describe a situation where a lack of training or skills affected your performance or your team's performance?",
                "ar": "هل يمكنك وصف موقف حيث أثر نقص التدريب أو المهارات على أدائك أو أداء فريقك؟"
            },
            {
                "en": "How is knowledge transferred when someone leaves or changes roles?",
                "ar": "كيف يتم نقل المعرفة عندما يغادر شخص ما أو يغير دوره؟"
            },
            {
                "en": "What type of training would be most valuable to you right now?",
                "ar": "ما نوع التدريب الذي سيكون أكثر قيمة لك الآن؟"
            },
            {
                "en": "When you receive training, do you feel you can actually apply what you learned in your daily work?",
                "ar": "عندما تتلقى تدريباً، هل تشعر أنك تستطيع فعلاً تطبيق ما تعلمته في عملك اليومي؟"
            },
            {
                "en": "Is there a mentoring or coaching culture here? Do experienced colleagues help newer ones grow?",
                "ar": "هل هناك ثقافة توجيه وإرشاد هنا؟ هل يساعد الزملاء ذوو الخبرة الأحدث عهداً على النمو؟"
            },
            {
                "en": "If a key person in your team were to leave tomorrow, what knowledge or skills would be lost?",
                "ar": "إذا كان شخص رئيسي في فريقك سيغادر غداً، ما هي المعرفة أو المهارات التي ستفقد؟"
            },
            {
                "en": "Have you seen mistakes or quality problems happen because someone wasn't properly trained? How often does that come up?",
                "ar": "هل رأيت أخطاء أو مشاكل جودة تحدث لأن شخصاً ما لم يتم تدريبه بشكل صحيح؟ كم مرة يظهر ذلك؟"
            },
            {
                "en": "What's the one skill or knowledge gap in your team that, if fixed, would make the biggest difference?",
                "ar": "ما هي الفجوة في المهارة أو المعرفة في فريقك التي، إذا تم سدها، ستحدث أكبر فرق؟"
            },
        ],
        "closing": [
            {
                "en": "Is there anything else you'd like to share about training, learning, or professional development?",
                "ar": "هل هناك أي شيء آخر تود مشاركته حول التدريب أو التعلم أو التطوير المهني؟"
            },
        ],
    },
}

# Interview flow order
CATEGORY_ORDER = [
    "strategic_implementation",
    "working_conditions",
    "work_organization",
    "time_management",
    "communication_coordination_cooperation",
    "integrated_training",
]
