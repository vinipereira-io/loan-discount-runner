from loan_calculator import calculate_expected_repayment_schedule
from datetime import datetime, timedelta
from dateutil.parser import parse
from tabulate import tabulate

print('------------------------------------------------\nWelcome to DiscountRunner!\n------------------------------------------------')
print('This program helps you simulate the impact of interest rate discounts in your loan.\nFollow the instructions to calculate your own scenarios:')

loan_amount = input('How much are you borrowing? (in AUD; min 3000; max 50000) ')
loan_amount = float(loan_amount)
if loan_amount < 3000 or loan_amount > 50000:
    raise ValueError('Loan amount is out of acceptable range, it needs to be between 3,000 and 50,000')

""" repayment_frequency = input('How often do you want to make payments on your loan? (monthly, fortnightly or weekly) ').lower()
if repayment_frequency not in ['monthly', 'fortnightly', 'weekly']:
    raise ValueError('Invalid frequency') """ 
repayment_frequency = 'monthly' # Currently supporting monthly frequency only


term_in_months = input('How long do you need to repay the loan? (in months; min 12; max 72) ')
term_in_months = int(term_in_months)
if term_in_months < 12 or term_in_months > 72:
    raise ValueError('Invalid term, it needs to be between 12 and 72 months')

if repayment_frequency == 'monthly':
    number_of_repayments = term_in_months
elif repayment_frequency == 'fortnightly':
    number_of_repayments = int(term_in_months * (26 / 12))
elif repayment_frequency == 'weekly':
    number_of_repayments = int(term_in_months * (52 / 12))

interest_rate = input('What interest rate are being charged per year? (min 25%; max 50%) ').strip('%')
interest_rate = float(interest_rate.strip('%')) / 100
if interest_rate < 0.25 or interest_rate > 0.5:
    raise ValueError('Interest rate is out of acceptable range, it needs to be between 25 and 50% ')

establishment_date = input('When was this loan funded? (dd/mm/yyyy) ')
establishment_date = datetime.strptime(establishment_date, '%d/%m/%Y')

first_repayment_date = input('When do you want your first repayment to be? (max 30 days after establishment date; dd/mm/yyyy) ')
first_repayment_date = datetime.strptime(first_repayment_date, '%d/%m/%Y')

if (first_repayment_date - establishment_date).days > 30:
    raise ValueError('First repayment date can\'t be after 30 days of funding')

establishment_date = establishment_date.strftime('%d/%m/%Y')
first_repayment_date = first_repayment_date.strftime('%d/%m/%Y')

print('Calculating your repayment scenario...')

loan_scenario = calculate_expected_repayment_schedule(loan_amount, repayment_frequency, number_of_repayments, interest_rate, establishment_date, first_repayment_date)
loan_expected_schedule = loan_scenario['expected_repayment_schedule']
loan_total_repayment = sum(entry['repayment'] for entry in loan_expected_schedule)
loan_total_interest = sum(entry['interest'] for entry in loan_expected_schedule)

print('Your repayment amount is: $' + str(loan_scenario['repayment_amount']) + '\n' + 
      'At the end of your loan you\'ll have paid $' + str(loan_total_repayment) + '\n' +
      'From that amount $' + str(loan_total_interest) + ' is interest.')

repayment_schedule = loan_scenario['expected_repayment_schedule']

if input('Do you want to see your full expected repayment schedule? (y/n) ').lower() == 'y':
    headers = [x.capitalize().replace('_', ' ') for x in repayment_schedule[0].keys()]
    rows = [y.values() for y in repayment_schedule]

    print(tabulate(rows, headers, numalign = 'left', stralign = 'left', tablefmt = 'fancy_grid'))

print('OK, now let\'s simulate your discounts...')
discount_input = input('Enter all your discounts in the format "month # : discount in %" separated by comma (e.g. 2 : 0.50%, 5 : 0.25%...) ')
discount_input = discount_input.replace(' ', '').split(',')

discount_list = []
for entry in discount_input:
    discount_dict = {}
    month, discount = entry.split(':')
    month = int(month.strip())
    discount = float(discount.strip().rstrip('%')) / 100
    discount_dict['month'] = month
    discount_dict['discount'] = discount
    discount_list.append(discount_dict)

current_repayment_schedule = repayment_schedule
current_interest_rate = interest_rate
for discount in discount_list:
    schedule_before_discount = list(filter(lambda entry: entry['id'] <= discount['month'], current_repayment_schedule))

    reference_entry = current_repayment_schedule[discount['month'] - 1]
    current_balance = reference_entry['closing_balance']
    remaining_repayments = len(current_repayment_schedule) - reference_entry['id']
    current_interest_rate -= discount['discount']
    effective_date = reference_entry['date']
    next_repayment_date = current_repayment_schedule[discount['month']]['date']

    discount_scenario = calculate_expected_repayment_schedule(current_balance, repayment_frequency, remaining_repayments, current_interest_rate, effective_date, next_repayment_date)
    schedule_after_discount = discount_scenario['expected_repayment_schedule']

    current_repayment_schedule = schedule_before_discount + schedule_after_discount
    new_id = 0
    for entry in current_repayment_schedule:
        new_id += 1
        entry['id'] = new_id

discount_impact = round(loan_total_repayment - sum(entry['repayment'] for entry in current_repayment_schedule),2)

print('You will save a total amount of $' + str(discount_impact) + ' with interest discounts.')

if input('Do you want to see your updated repayment schedule? (y/n) ').lower() == 'y':
    headers = [x.capitalize().replace('_', ' ') for x in current_repayment_schedule[0].keys()]
    rows = [y.values() for y in current_repayment_schedule]

    print(tabulate(rows, headers, numalign = 'left', stralign = 'left', tablefmt = 'fancy_grid'))