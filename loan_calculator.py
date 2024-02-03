from datetime import datetime, timedelta

def convert_interest_rate_to_frequency(interest_rate, frequency):
    if frequency == 'monthly':
        return interest_rate / 12
    elif frequency == 'fortnightly':
        return interest_rate / 365 * 14
    elif frequency == 'weekly':
        return interest_rate / 365 * 7
    else:
        raise ValueError('Invalid frequency')

def calculate_pmt(interest_rate, periods, present_value, type=0):
    pmt = (present_value * interest_rate) / (1 - (1 + interest_rate) ** -periods)
    if type == 1:
        pmt = pmt / (1 + interest_rate)
    return round(pmt, 2)

def set_new_date(date, offset, frequency):
    if frequency == 'monthly':
        year_offset = offset // 12
        month_offset = offset % 12
        new_year = date.year + year_offset
        new_month = date.month + month_offset
        if new_month > 12:
            new_year += 1
            new_month -= 12
        return date.replace(year=new_year, month=new_month)
    elif frequency == 'fortnightly':
        return date + timedelta(days = offset * 14)
    elif frequency == 'weekly':
        return date + timedelta(days = offset * 7)
    else:
        raise ValueError('Invalid frequency')

def adjust_repayment_amount(original_schedule, first_repayment_date, daily_interest_rate, number_of_repayments, present_value):
    last_date = first_repayment_date
    original_schedule.pop(0)

    sum_of_products = 0
    for entry in original_schedule:
        parsed_date = datetime.strptime(entry['date'], '%d/%m/%Y')
        diff_days = (parsed_date - last_date).days
        sum_of_products += diff_days * entry['interest']
        last_date = parsed_date

    sum_of_interests = sum(entry['interest'] for entry in original_schedule)
    days_per_entry = sum_of_products / sum_of_interests

    adjusted_interest_rate = daily_interest_rate * days_per_entry
    adjusted_repayment = calculate_pmt(adjusted_interest_rate, number_of_repayments, present_value, 1)

    return adjusted_repayment

def calculate_expected_repayment_schedule(loan_amount, repayment_frequency, number_of_repayments, interest_rate, establishment_date, first_repayment_date, repayment_amount = 'undefined'):
    parsed_establishment_date = datetime.strptime(establishment_date, '%d/%m/%Y')
    parsed_first_repayment_date = datetime.strptime(first_repayment_date, '%d/%m/%Y')
    converted_interest_rate = convert_interest_rate_to_frequency(interest_rate, repayment_frequency)
    daily_interest_rate = interest_rate / 365
    present_value = loan_amount
    present_value += (parsed_first_repayment_date - parsed_establishment_date).days * daily_interest_rate * present_value
    if repayment_amount == 'undefined':
        repayment = calculate_pmt(converted_interest_rate, number_of_repayments, present_value, 1)
    else:
        repayment = repayment_amount
    repayment_schedule = []
    prev_balance = abs(loan_amount)
    prev_date = parsed_establishment_date

    for i in range(number_of_repayments):
        new_date = set_new_date(parsed_first_repayment_date, i, repayment_frequency)
        diff_days = (new_date - prev_date).days
        new_interest = diff_days * daily_interest_rate * prev_balance
        new_principal = abs(repayment) - new_interest

        if i == number_of_repayments - 1:
            last_repayment = prev_balance + new_interest
            last_principal = last_repayment - new_interest
            repayment_obj = {
                'id': i + 1,
                'date': new_date.strftime('%d/%m/%Y'),
                'opening_balance': prev_balance,
                'repayment': round(last_repayment, 2),
                'interest': round(new_interest, 2),
                'principal': round(last_principal, 2),
                'closing_balance': round(prev_balance - last_principal, 2)
            }
        else:
            repayment_obj = {
                'id': i + 1,
                'date': new_date.strftime('%d/%m/%Y'),
                'opening_balance': prev_balance,
                'repayment': abs(repayment),
                'interest': round(new_interest, 2),
                'principal': round(new_principal, 2),
                'closing_balance': round(prev_balance - new_principal, 2)
            }
        repayment_schedule.append(repayment_obj)
        prev_balance = round(prev_balance - new_principal, 2)
        prev_date = new_date
    
    if repayment_frequency == 'monthly' and repayment_amount == 'undefined':
        adjusted_repayment = adjust_repayment_amount(repayment_schedule, parsed_first_repayment_date, daily_interest_rate, number_of_repayments, present_value)
        repayment_schedule = calculate_expected_repayment_schedule(loan_amount, repayment_frequency, number_of_repayments, interest_rate, establishment_date, first_repayment_date, adjusted_repayment)['expected_repayment_schedule']

    return {
        'repayment_amount': round(repayment, 2),
        'expected_repayment_schedule': repayment_schedule
    }