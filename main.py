from loan_calculator import calculate_expected_repayment_schedule
from datetime import datetime
from tabulate import tabulate
import os
import time

# Clear the terminal screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

class Loan:
    def __init__(self, amount, interest_rate, repayment_frequency, number_of_repayments, establishment_date, first_repayment_date):
        self.amount = amount
        self.interest_rate = interest_rate
        self.initial_interest_rate = interest_rate
        self.repayment_frequency = repayment_frequency
        self.number_of_repayments = number_of_repayments
        self.establishment_date = establishment_date
        self.first_repayment_date = first_repayment_date

        initial_scenario = calculate_expected_repayment_schedule(self.amount, self.repayment_frequency, self.number_of_repayments, self.interest_rate, self.establishment_date, self.first_repayment_date)
        
        self.repayment_amount = initial_scenario['repayment_amount']
        self.repayment_schedule = initial_scenario['expected_repayment_schedule']
        self.initial_repayment_schedule = initial_scenario['expected_repayment_schedule']
        self.repayment_total = sum(entry['repayment'] for entry in self.repayment_schedule)
        self.initial_repayment_total = sum(entry['repayment'] for entry in self.repayment_schedule)
        self.interest_total = sum(entry['interest'] for entry in self.repayment_schedule)
        self.initial_interest_total = sum(entry['interest'] for entry in self.repayment_schedule)

    def __repr__(self):
        repayment_formatted = '${:,.2f}'.format(self.repayment_amount)
        total_formatted = '${:,.2f}'.format(self.repayment_total)
        interest_formatted = '${:,.2f}'.format(self.interest_total)
        return 'Your repayment amount is: {}\nAt the end of your loan you\'ll have paid {}\nFrom which {} is interest.'.format(repayment_formatted, total_formatted, interest_formatted)

    def print_repayment_schedule(self, schedule):
        headers = [x.capitalize().replace('_', ' ') for x in schedule[0].keys()]
        formatted_rows = []

        for row in schedule:
            formatted_row = []
            for val in row.values():
                if isinstance(val, float):
                    formatted_val = '${:,.2f}'.format(val)
                else:
                    formatted_val = val
                formatted_row.append(formatted_val)
            formatted_rows.append(formatted_row)

        print(tabulate(formatted_rows, headers, numalign = 'left', stralign = 'left', tablefmt = 'fancy_grid'))
        print()
        input('Press Enter to continue...')
        clear_screen()

    def calculate_discount_impact(self, discount_list):
        current_repayment_schedule = self.repayment_schedule
        current_interest_rate = self.interest_rate
        for discount in discount_list:
            schedule_before_discount = list(filter(lambda entry: entry['id'] <= discount['month'], current_repayment_schedule))

            reference_entry = current_repayment_schedule[discount['month'] - 1]
            current_balance = reference_entry['closing_balance']
            remaining_repayments = len(current_repayment_schedule) - reference_entry['id']
            current_interest_rate -= discount['discount']
            effective_date = reference_entry['date']
            next_repayment_date = current_repayment_schedule[discount['month']]['date']

            discount_scenario = calculate_expected_repayment_schedule(current_balance, self.repayment_frequency, remaining_repayments, current_interest_rate, effective_date, next_repayment_date)
            schedule_after_discount = discount_scenario['expected_repayment_schedule']

            current_repayment_schedule = schedule_before_discount + schedule_after_discount
            new_id = 0
            for entry in current_repayment_schedule:
                new_id += 1
                entry['id'] = new_id
        self.interest_rate = current_interest_rate
        self.repayment_schedule = current_repayment_schedule
        self.repayment_total = sum(entry['repayment'] for entry in current_repayment_schedule)
        self.interest_total = sum(entry['interest'] for entry in current_repayment_schedule)
        discount_impact = round(self.initial_repayment_total - self.repayment_total,2)
        return discount_impact

clear_screen()
while True:
    ## Program starts
    print('--------------------------\nWelcome to DiscountRunner!\n--------------------------')
    print()
    print('This program helps you simulate the impact of interest rate discounts in your loan.\nFollow the instructions to calculate your own scenarios.')
    print()
    input('Press Enter to continue...')
    clear_screen()

    ## Loan variables input

    loan_amount = input('Q: How much are you looking to borrow? (in AUD; minimum $3,000; maximum $50,000)\nA: ')
    loan_amount = float(loan_amount.replace(',',''))
    if loan_amount < 3000 or loan_amount > 50000:
        raise ValueError('Loan amount is out of acceptable range, it needs to be between 3,000 and 50,000')
    clear_screen()

    repayment_frequency = 'monthly' # Currently supporting monthly frequency only

    term_in_months = input('Q: How long do you need to repay the loan? (in months; minimum 12; maximum 72)\nA: ')
    term_in_months = int(term_in_months)
    if term_in_months < 12 or term_in_months > 72:
        raise ValueError('Invalid term, it needs to be between 12 and 72 months')
    clear_screen()

    number_of_repayments = term_in_months # Currently supporting monthly frequency only

    interest_rate = input('Q: What is the annual interest rate? (minimum 25%; maximum 50%)\nA: ').strip('%')
    interest_rate = float(interest_rate.strip('%')) / 100
    if interest_rate < 0.25 or interest_rate > 0.5:
        raise ValueError('Interest rate is out of acceptable range, it needs to be between 25 and 50% ')
    clear_screen()

    establishment_date = input('Q: When was this loan funded? (please provide the date in the format dd/mm/yyyy)\nA: ')
    establishment_date = datetime.strptime(establishment_date, '%d/%m/%Y')
    clear_screen()

    first_repayment_date = input('Q: When do you want your first repayment to be? (up to 30 days after funding; dd/mm/yyyy)\nA: ')
    first_repayment_date = datetime.strptime(first_repayment_date, '%d/%m/%Y')
    if (first_repayment_date - establishment_date).days > 30:
        raise ValueError('First repayment date can\'t be after 30 days of funding')
    clear_screen()

    establishment_date = establishment_date.strftime('%d/%m/%Y')
    first_repayment_date = first_repayment_date.strftime('%d/%m/%Y')

    ## Loan creation

    print('Calculating your scenario...')
    time.sleep(2)
    loan = Loan(loan_amount, interest_rate, repayment_frequency, number_of_repayments, establishment_date, first_repayment_date)
    clear_screen()

    print(loan)
    print()
    if input('Q: Would you like to see your full expected repayment schedule? (y/n)\nA: ').lower() == 'y':
        clear_screen()
        loan.print_repayment_schedule(loan.initial_repayment_schedule)
    clear_screen()

    ## Discounts input
    
    print('OK, now let\'s simulate your discounts...')
    discount_list = []
    print()
    while True:
        discount_input = input('Q: Enter a discount in the format "month: discount%" (e.g. 2: 0.50%)\nA: ')
        discount_input = discount_input.replace(' ', '').split(':')
        month = int(discount_input[0].strip())
        discount = float(discount_input[1].strip().rstrip('%')) / 100
        discount_dict = {}
        discount_dict['month'] = month
        discount_dict['discount'] = discount
        discount_list.append(discount_dict)
        clear_screen()
        if input('Q: Would you like to add another discount? (y/n)\nA: ').lower() == 'n':
            clear_screen()
            break
        clear_screen()

    print('Recalculating your scenario...')
    time.sleep(2)

    discount_impact = loan.calculate_discount_impact(discount_list)
    clear_screen()

    print('You will save a total amount of ' + '${:,.2f}'.format(discount_impact) + ' with interest discounts.')
    print()
    if input('Q: Would you like to see your updated repayment schedule? (y/n)\nA: ').lower() == 'y':
        clear_screen()
        loan.print_repayment_schedule(loan.repayment_schedule)
    clear_screen()

    if input('Q: Would you like to simulate another loan? (y/n)\nA: ').lower() != 'y':
        clear_screen()
        print('Thank you for using DiscountRunner!')
        print()
        print('Created by Vini Pereira')
        print('github.com/vinipereira-io')
        break ## Program stops
    clear_screen()