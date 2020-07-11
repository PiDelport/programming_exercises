# A FizzBuzz program.
# I picked a slightly different way to do this to stick with extensible design.
# Adding more conditions just requires inserting them into the dictionary.
# Output is to a list then printed; further processing is possible.

conditions_dict = {3: "Fizz", 5: "Buzz"}
numeric_order = True # False to use the insertion order of conditions_dict
start_value = 1
end_value = 100


def Fizz_or_Buzz(this_number: int, conditions_dict: dict, conditions_list: list) -> str:
    # If it meets the criteria return the word(s) else return the digit as string
    result_string = ''
    for this_value in conditions_list:
        if not this_number % this_value:
            result_string = result_string + conditions_dict[this_value]
    if not result_string:
        result_string = str(this_number)
    return result_string


def main(conditions_dict: dict, start_value: int, end_value: int, numeric_order: bool) -> None:
    output_list = []
    conditions_list = list(conditions_dict.keys())
    if numeric_order:
        conditions_list.sort()
    for this_number in range(start_value, end_value + 1):
        #print(Fizz_or_Buzz(this_number,conditions_dict, conditions_list))
        output_list.append(Fizz_or_Buzz(this_number, conditions_dict, conditions_list))
    print("\n".join(output_list))

main(conditions_dict, start_value, end_value, numeric_order)