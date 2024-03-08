class RequestPrioritizer():
    """
    Prioritizes requests
    """

    CATEGORIES_PRIORITIES = {
        "Emergency": 1,
        "Pain/Discomfort":  2,
        "Medical Needs": 3,
        "Bathroom Needs": 4,
        "Temperature-Related Needs": 5,
        "Food": 6,
        "Thirsty": 7,
        "Shower": 8,
        "Entertainment Related Needs": 9,
        "Questions/General Information": 10,
        "Other - Non-Medical": 11,
        "Uncategorizable": 12
    }

    RISK_FACTORS = set([
        'Transferred From ICU', 
        'Heart Patient', 
        'COPD Patient', 
        'Reanimated',
        'Heart Patient',
        'Confused/Disoriented',
        'Paraplegia',
        'Neurologic Problem',
        'Pneumonia',
        'High Fall Risk',
        'High Age',
        'Diabetic',
        'Tracheotomy',
        'Gastric Bleeding Within 48 Hours'
    ])

    @classmethod
    def calculate_priority(cls, condition, request_category):
        category_priority = cls.CATEGORIES_PRIORITIES.get(request_category, 13)
        if condition in cls.RISK_FACTORS:
            return category_priority * 0.6
        return category_priority