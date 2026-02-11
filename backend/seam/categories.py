"""SEAM dysfunction categories – the six diagnostic domains.

Based on Henri Savall's Socio-Economic Approach to Management (SEAM).
Each category maps to a family of hidden costs and well-known managerial
dysfunctions documented in the SEAM intervention-research literature.

Each category includes: key, English name, Arabic name, detailed description,
and a comprehensive set of thematic tags that commonly surface during
diagnostic interviews.
"""

SEAM_CATEGORIES = [
    {
        "key": "strategic_implementation",
        "name_en": "Strategic Implementation",
        "name_ar": "التنفيذ الاستراتيجي",
        "description_en": (
            "Dysfunctions in translating organizational strategy into actionable "
            "plans and results. Includes: unclear or shifting strategic priorities, "
            "vision–execution gaps, delayed project implementation, reactive "
            "(firefighting) management instead of proactive planning, lack of KPIs "
            "or performance metrics, misalignment between stated goals and daily "
            "activities, frequent project failures, absence of medium-to-long-term "
            "planning, and disconnect between leadership decisions and front-line "
            "reality."
        ),
        "description_ar": (
            "اختلالات في ترجمة استراتيجية المنظمة إلى خطط عمل ونتائج ملموسة. "
            "تشمل: أولويات استراتيجية غير واضحة أو متغيرة، فجوات بين الرؤية والتنفيذ، "
            "تأخر تنفيذ المشاريع، إدارة ردود الأفعال بدل التخطيط الاستباقي، "
            "غياب مؤشرات الأداء، عدم تطابق الأهداف المعلنة مع الأنشطة اليومية، "
            "فشل متكرر للمشاريع، وانفصال قرارات القيادة عن واقع الميدان."
        ),
        "example_tags": [
            "unclear_priorities", "vision_misalignment", "strategy_execution_gap",
            "lack_of_direction", "short_term_focus", "goal_ambiguity",
            "reactive_management", "no_kpis", "project_failure",
            "delayed_implementation", "leadership_disconnect",
        ],
    },
    {
        "key": "working_conditions",
        "name_en": "Working Conditions",
        "name_ar": "ظروف العمل",
        "description_en": (
            "Dysfunctions in the physical and psychological work environment. "
            "Includes: inadequate or defective tools and equipment, unsafe or "
            "unhealthy premises, excessive physical or cognitive workload, "
            "ergonomic issues, suppression of creative capacity, toxic workplace "
            "culture, psychological safety deficits (fear of speaking up), "
            "lack of recognition, burnout risk, poor work-life balance, "
            "noise or environmental nuisances, and insufficient resources "
            "allocated to front-line operations."
        ),
        "description_ar": (
            "اختلالات في بيئة العمل المادية والنفسية. تشمل: أدوات ومعدات "
            "غير كافية أو معطلة، مباني غير آمنة أو غير صحية، عبء عمل مادي "
            "أو ذهني مفرط، مشاكل بيئة العمل المريحة، كبت القدرة الإبداعية، "
            "ثقافة عمل سامة، ضعف الأمان النفسي، غياب التقدير، "
            "خطر الإرهاق المهني، وضعف التوازن بين العمل والحياة."
        ),
        "example_tags": [
            "workload_imbalance", "poor_tools", "unsafe_environment",
            "inadequate_facilities", "stress", "burnout_risk",
            "suppressed_creativity", "toxic_culture", "low_psychological_safety",
            "no_recognition", "poor_work_life_balance", "noise_nuisance",
            "defective_equipment", "resource_shortage",
        ],
    },
    {
        "key": "work_organization",
        "name_en": "Work Organization",
        "name_ar": "تنظيم العمل",
        "description_en": (
            "Dysfunctions in organizational structure, role design, and process "
            "efficiency. Includes: role ambiguity and overlapping responsibilities, "
            "task duplication, unclear authority chains, excessive hierarchy and "
            "bureaucracy, decision paralysis (decisions stuck at higher levels), "
            "role creep (responsibilities expanding without formal mandate), "
            "lack of organizational flexibility, unoptimized task allocation, "
            "process inefficiency, absence of documented procedures, and "
            "silos between teams or departments."
        ),
        "description_ar": (
            "اختلالات في الهيكل التنظيمي وتصميم الأدوار وكفاءة العمليات. "
            "تشمل: غموض الأدوار وتداخل المسؤوليات، تكرار المهام، "
            "سلاسل سلطة غير واضحة، تدرج هرمي مفرط وبيروقراطية، "
            "شلل في اتخاذ القرار، توسع المسؤوليات دون تفويض رسمي، "
            "غياب المرونة التنظيمية، وعدم كفاءة العمليات."
        ),
        "example_tags": [
            "role_ambiguity", "process_inefficiency", "excessive_bureaucracy",
            "unclear_authority", "task_duplication", "decision_bottleneck",
            "decision_paralysis", "role_creep", "organizational_rigidity",
            "no_documented_procedures", "excessive_hierarchy", "departmental_silos",
        ],
    },
    {
        "key": "time_management",
        "name_en": "Time Management",
        "name_ar": "إدارة الوقت",
        "description_en": (
            "Dysfunctions in time utilization at individual and organizational "
            "levels. Includes: excessive or unproductive meetings, constant "
            "interruptions during focused work, missed deadlines, encroachment "
            "on personal/family time, firefighting culture (urgent always over "
            "important), inability to prioritize strategic over operational tasks, "
            "poor scheduling and calendar management, time wasted on redundant "
            "reporting and administrative tasks, absence of time-planning tools, "
            "and multitasking overload."
        ),
        "description_ar": (
            "اختلالات في استخدام الوقت على المستوى الفردي والتنظيمي. "
            "تشمل: اجتماعات مفرطة أو غير منتجة، انقطاعات مستمرة أثناء العمل، "
            "مواعيد نهائية فائتة، تعدي على الوقت الشخصي والعائلي، "
            "ثقافة إطفاء الحرائق، عدم القدرة على تحديد أولويات المهام "
            "الاستراتيجية، وإهدار الوقت في تقارير إدارية متكررة."
        ),
        "example_tags": [
            "excessive_meetings", "constant_interruptions", "missed_deadlines",
            "poor_scheduling", "time_waste", "firefighting_culture",
            "work_life_encroachment", "multitasking_overload",
            "redundant_reporting", "no_time_planning", "urgent_over_important",
        ],
    },
    {
        "key": "communication_coordination_cooperation",
        "name_en": "Communication, Coordination & Cooperation (3Cs)",
        "name_ar": "التواصل والتنسيق والتعاون (3Cs)",
        "description_en": (
            "Dysfunctions in information flow, coordination mechanisms, and "
            "teamwork quality. Includes: information silos (critical information "
            "not reaching the right people), top-down-only communication with no "
            "upward feedback, poor interdepartmental coordination, cross-functional "
            "friction, conflict avoidance (issues swept under the rug), "
            "zero or ineffective feedback loops, lack of regular team meetings, "
            "rumor culture replacing formal communication, absence of "
            "collaboration platforms, weak manager–employee dialogue, and "
            "breakdown of trust between hierarchical levels."
        ),
        "description_ar": (
            "اختلالات في تدفق المعلومات وآليات التنسيق وجودة العمل الجماعي. "
            "تشمل: جزر معلوماتية معزولة، تواصل من أعلى لأسفل فقط دون تغذية راجعة، "
            "ضعف التنسيق بين الأقسام، احتكاك بين الوظائف المختلفة، "
            "تجنب النزاعات، غياب حلقات التغذية الراجعة الفعالة، "
            "ثقافة الشائعات بدل التواصل الرسمي، وانهيار الثقة بين المستويات الإدارية."
        ),
        "example_tags": [
            "information_silos", "poor_interdepartmental_coordination",
            "lack_of_feedback", "conflict", "weak_teamwork",
            "communication_breakdown", "coordination_gaps",
            "top_down_communication", "conflict_avoidance", "rumor_culture",
            "cross_functional_friction", "no_upward_feedback", "trust_deficit",
        ],
    },
    {
        "key": "integrated_training",
        "name_en": "Integrated Training",
        "name_ar": "التدريب المتكامل",
        "description_en": (
            "Dysfunctions in employee skill development and organizational "
            "learning. Includes: denial of training and learning opportunities, "
            "inadequate or non-existent onboarding for new employees, "
            "no continuous learning culture, knowledge loss when employees "
            "leave or change roles (no succession planning), training–practice "
            "disconnect (training content not applied on the job), irrelevant "
            "or superficial training programs, insufficient investment in "
            "employee development, competency gaps in critical areas, "
            "lack of mentoring or coaching, and failure to adapt training "
            "to evolving technology and market demands."
        ),
        "description_ar": (
            "اختلالات في تطوير مهارات الموظفين والتعلم التنظيمي. "
            "تشمل: حرمان من فرص التدريب والتعلم، تأهيل غير كافٍ للموظفين الجدد، "
            "غياب ثقافة التعلم المستمر، فقدان المعرفة عند مغادرة الموظفين "
            "أو تغيير أدوارهم (لا تخطيط للخلافة)، انفصال التدريب عن الممارسة، "
            "برامج تدريب سطحية أو غير ذات صلة، فجوات في الكفاءات الحرجة، "
            "وعدم تكييف التدريب مع التطورات التكنولوجية."
        ),
        "example_tags": [
            "skill_gaps", "inadequate_onboarding", "no_continuous_learning",
            "knowledge_loss", "irrelevant_training", "training_discontinuity",
            "no_succession_planning", "training_practice_disconnect",
            "no_mentoring", "underinvestment_in_development",
            "competency_gaps", "technology_skills_gap",
        ],
    },
]

# Quick lookup helpers
CATEGORY_KEYS = [c["key"] for c in SEAM_CATEGORIES]
CATEGORY_NAMES_EN = {c["key"]: c["name_en"] for c in SEAM_CATEGORIES}
CATEGORY_NAMES_AR = {c["key"]: c["name_ar"] for c in SEAM_CATEGORIES}

ALL_TAGS = []
for cat in SEAM_CATEGORIES:
    ALL_TAGS.extend(cat["example_tags"])
