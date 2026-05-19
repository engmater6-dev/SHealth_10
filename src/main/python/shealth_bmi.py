from shealth import SHealth


def main():
    shealth = SHealth()
    shealth.calculate_bmi("shealth.dat")

    for age in range(20, 80, 10):
        print(
            f"{age} - underweight = {shealth.get_bmi_ratio(age, 100):.6f}, "
            f"normal = {shealth.get_bmi_ratio(age, 200):.6f}, "
            f"overweight = {shealth.get_bmi_ratio(age, 300):.6f}, "
            f"obesity = {shealth.get_bmi_ratio(age, 400):.6f}"
        )


if __name__ == "__main__":
    main()
