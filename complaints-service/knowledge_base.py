"""
Uzbekistan Environmental Violations Knowledge Base
Based on current legislation and БРВ = 412,000 сумов (August 2025)
"""

# Base calculation unit (БРВ) in UZS
BRV = 412_000

# Informant reward percentage
INFORMANT_REWARD_PERCENT = 15

# Violation types with fines
VIOLATIONS = {
    "air_pollution_construction": {
        "name_ru": "Загрязнение воздуха на стройплощадке",
        "name_uz": "Qurilish maydonchasida havoni ifloslantirish",
        "name_en": "Air pollution at construction site",
        "description_ru": "Несоблюдение требований по охране атмосферного воздуха, выбросы пыли и песка",
        "fine_min": BRV * 10,  # 4,120,000
        "fine_max": BRV * 10,
        "fine_repeat": BRV * 50,  # 18,750,000 при повторном
        "keywords": ["стройка", "пыль", "строительство", "песок", "цемент", "construction", "dust", "qurilish"]
    },
    "burning_waste": {
        "name_ru": "Сжигание растительных остатков",
        "name_uz": "O'simlik qoldiqlarini yoqish",
        "name_en": "Burning vegetation/waste",
        "description_ru": "Сжигание стерни, сухих листьев, веток или других растительных остатков",
        "fine_min": BRV * 3,   # 1,236,000
        "fine_max": BRV * 5,   # 2,060,000
        "keywords": ["сжигание", "дым", "огонь", "костёр", "мусор горит", "burning", "smoke", "fire", "yonayotgan"]
    },
    "illegal_dumping": {
        "name_ru": "Выброс мусора в неустановленных местах",
        "name_uz": "Belgilanmagan joylarga chiqindilar tashlash",
        "name_en": "Illegal waste dumping",
        "description_ru": "Выброс твердых бытовых и строительных отходов в неустановленных местах",
        "fine_min": BRV * 1,   # 412,000
        "fine_max": BRV * 3,   # 1,236,000
        "keywords": ["мусор", "свалка", "отходы", "выброс", "garbage", "dump", "waste", "chiqindi", "axlat"]
    },
    "water_pollution": {
        "name_ru": "Загрязнение водных ресурсов",
        "name_uz": "Suv resurslarini ifloslantirish",
        "name_en": "Water pollution",
        "description_ru": "Загрязнение или отравление водных ресурсов",
        "fine_min": BRV * 3,   # 1,236,000
        "fine_max": BRV * 5,   # 2,060,000
        "keywords": ["вода", "река", "канал", "слив", "water", "river", "suv", "daryo"]
    },
    "illegal_tree_cutting": {
        "name_ru": "Незаконная вырубка деревьев",
        "name_uz": "Daraxtlarni noqonuniy kesish",
        "name_en": "Illegal tree cutting",
        "description_ru": "Незаконная вырубка, обрезка, повреждение или уничтожение деревьев",
        "fine_min": BRV * 25,  # 10,300,000
        "fine_max": BRV * 50,  # 20,600,000
        "keywords": ["вырубка", "дерево", "пила", "рубка", "tree", "cutting", "daraxt", "kesish"]
    },
    "environmental_restoration_failure": {
        "name_ru": "Непринятие мер по восстановлению среды",
        "name_uz": "Atrof-muhitni tiklash bo'yicha choralar ko'rmaslik",
        "name_en": "Failure to restore environment",
        "description_ru": "Непринятие мер по восстановлению природной среды и ликвидации последствий",
        "fine_min": BRV * 1,   # 412,000
        "fine_max": BRV * 3,   # 1,236,000
        "keywords": ["восстановление", "ликвидация", "ущерб", "restoration", "damage"]
    },
    "vehicle_emissions": {
        "name_ru": "Превышение выбросов транспортом",
        "name_uz": "Transport tomonidan chiqindilarning oshishi",
        "name_en": "Vehicle emissions violation",
        "description_ru": "Эксплуатация транспортного средства с превышением норм выбросов",
        "fine_min": BRV * 2,   # 824,000
        "fine_max": BRV * 5,   # 2,060,000
        "keywords": ["выхлоп", "дым машины", "автомобиль", "exhaust", "vehicle", "avtomobil", "tutun"]
    },
    "industrial_emissions": {
        "name_ru": "Промышленные выбросы",
        "name_uz": "Sanoat chiqindilari",
        "name_en": "Industrial emissions",
        "description_ru": "Превышение нормативов выбросов загрязняющих веществ предприятием",
        "fine_min": BRV * 10,  # 4,120,000
        "fine_max": BRV * 50,  # 20,600,000
        "keywords": ["завод", "фабрика", "труба", "промышленность", "factory", "industrial", "zavod", "fabrika"]
    }
}


def calculate_reward(fine_amount: int) -> int:
    """Calculate informant reward (15% of fine)"""
    return int(fine_amount * INFORMANT_REWARD_PERCENT / 100)


def get_violation_info(violation_type: str) -> dict:
    """Get detailed info about a violation type"""
    if violation_type not in VIOLATIONS:
        return None
    
    violation = VIOLATIONS[violation_type]
    return {
        "type": violation_type,
        "name": violation["name_ru"],
        "description": violation["description_ru"],
        "fine_range": {
            "min": violation["fine_min"],
            "max": violation["fine_max"],
            "min_formatted": f"{violation['fine_min']:,}".replace(",", " ") + " сум",
            "max_formatted": f"{violation['fine_max']:,}".replace(",", " ") + " сум"
        },
        "reward_range": {
            "min": calculate_reward(violation["fine_min"]),
            "max": calculate_reward(violation["fine_max"]),
            "min_formatted": f"{calculate_reward(violation['fine_min']):,}".replace(",", " ") + " сум",
            "max_formatted": f"{calculate_reward(violation['fine_max']):,}".replace(",", " ") + " сум"
        }
    }


def get_all_violations_summary() -> str:
    """Get formatted summary of all violations for AI context"""
    summary = "БАЗА ДАННЫХ ШТРАФОВ ЗА ЭКОЛОГИЧЕСКИЕ НАРУШЕНИЯ В УЗБЕКИСТАНЕ\n"
    summary += "=" * 60 + "\n\n"
    summary += f"Базовая расчётная величина (БРВ): {BRV:,} сумов\n"
    summary += f"Вознаграждение информатору: {INFORMANT_REWARD_PERCENT}% от суммы штрафа\n\n"
    
    for key, v in VIOLATIONS.items():
        reward_min = calculate_reward(v["fine_min"])
        reward_max = calculate_reward(v["fine_max"])
        
        summary += f"▸ {v['name_ru']}\n"
        summary += f"  Штраф: {v['fine_min']:,} - {v['fine_max']:,} сум\n"
        summary += f"  Вознаграждение: {reward_min:,} - {reward_max:,} сум\n"
        summary += f"  Описание: {v['description_ru']}\n\n"
    
    return summary
