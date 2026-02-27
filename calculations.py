def calculate_pf(basic):
    WAGE_CEILING = 15000
    EMPLOYEE_RATE = 0.12
    EMPLOYER_RATE = 0.12
    EPS_RATE = 0.0833

    contribution_base = min(basic, WAGE_CEILING)

    employee_pf = round(contribution_base * EMPLOYEE_RATE, 2)
    employer_pf_total = round(contribution_base * EMPLOYER_RATE, 2)
    eps_contribution = round(contribution_base * EPS_RATE, 2)
    epf_from_employer = round(employer_pf_total - eps_contribution, 2)

    return {
        "contribution_base": contribution_base,
        "employee_pf": employee_pf,
        "employer_pf_total": employer_pf_total,
        "eps_contribution": eps_contribution,
        "epf_from_employer": epf_from_employer
    }


def calculate_esi(gross):
    ESI_THRESHOLD = 21000
    EMPLOYEE_RATE = 0.0075
    EMPLOYER_RATE = 0.0325

    if gross > ESI_THRESHOLD:
        return {
            "eligible": False,
            "employee_esi": 0,
            "employer_esi": 0
        }

    employee_esi = round(gross * EMPLOYEE_RATE, 2)
    employer_esi = round(gross * EMPLOYER_RATE, 2)

    return {
        "eligible": True,
        "employee_esi": employee_esi,
        "employer_esi": employer_esi
    }


def calculate_pt(state, gross):
    state = state.upper()

    if state == "KA":
        if gross <= 15000:
            pt = 0
        elif gross <= 20000:
            pt = 150
        else:
            pt = 200

        return {
            "state": "KA",
            "pt_amount": pt
        }

    if state == "MH":
        if gross <= 7500:
            pt = 0
        elif gross <= 10000:
            pt = 175
        else:
            pt = 200

        return {
            "state": "MH",
            "pt_amount": pt
        }

    return {
        "state": state,
        "pt_amount": None,
        "note": "PT slab not implemented for this state"
    }


def calculate_bonus(gross):
    BONUS_ELIGIBILITY_LIMIT = 21000
    BONUS_CALC_CEILING = 7000
    MIN_RATE = 0.0833
    MAX_RATE = 0.20

    if gross > BONUS_ELIGIBILITY_LIMIT:
        return {
            "eligible": False,
            "reason": "Salary exceeds eligibility limit"
        }

    calculation_base = min(gross, BONUS_CALC_CEILING)

    min_bonus = round(calculation_base * MIN_RATE, 2)
    max_bonus = round(calculation_base * MAX_RATE, 2)

    return {
        "eligible": True,
        "calculation_base": calculation_base,
        "minimum_bonus": min_bonus,
        "maximum_bonus": max_bonus
    }


def calculate_gratuity(last_drawn_salary, years_of_service):
    if years_of_service < 5:
        return {
            "eligible": False,
            "reason": "Less than 5 years of continuous service"
        }

    gratuity = round((last_drawn_salary * 15 * years_of_service) / 26, 2)

    return {
        "eligible": True,
        "gratuity_amount": gratuity
    }