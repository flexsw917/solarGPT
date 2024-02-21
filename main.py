from flask import Flask, request, jsonify

app = Flask(__name__)

# Constants
AVERAGE_PANEL_EFFICIENCY = 0.20  # 20% efficiency
AVERAGE_IRRADIANCE = 5  # Average kWh/m2
PANEL_COST_PER_SQM = 2500  # Cost per square meter in USD
INSTALLATION_COST_PER_SQM = 75  # Installation cost per sqm in USD
PANEL_AREA_SQM = 1.6  # Average area of a solar panel in square meters
USAGE_FACTOR = 0.2  # Factor to adjust for realistic panel usage on roof


def calculate_realistic_panel_count(roof_size):
  max_panel_count = roof_size / PANEL_AREA_SQM
  realistic_panel_count = int(max_panel_count * USAGE_FACTOR)
  return realistic_panel_count


def calculate_energy_output(panel_count):
  total_panel_area = panel_count * PANEL_AREA_SQM
  return total_panel_area * AVERAGE_IRRADIANCE * AVERAGE_PANEL_EFFICIENCY * 30


def calculate_costs(panel_count):
  total_panel_area = panel_count * PANEL_AREA_SQM
  panel_cost = PANEL_COST_PER_SQM * total_panel_area
  installation_cost = INSTALLATION_COST_PER_SQM * total_panel_area
  total_cost = panel_cost + installation_cost
  return panel_cost, installation_cost, total_cost


def calculate_savings(energy_output, current_bill):
  # Assuming a rate of $0.12 per kWh (adjust if needed)
  cost_per_kWh = 0.12
  estimated_monthly_solar_bill = energy_output * cost_per_kWh
  monthly_savings = current_bill - estimated_monthly_solar_bill
  return monthly_savings


def calculate_payback_period(total_cost, monthly_savings):
  if monthly_savings <= 0:
    return "Payback period cannot be calculated with current savings"
  annual_savings = monthly_savings * 12
  return total_cost / annual_savings


@app.route('/calculate', methods=['GET'])
def calculate():
  roof_size = request.args.get('roof_size', default=0, type=float)
  current_bill = request.args.get('current_bill', default=0, type=float)

  print("Received roof_size:", roof_size)  # Debugging line
  print("Received current_bill:", current_bill)  # Debugging line

  if roof_size <= 0 or current_bill <= 0:
    return jsonify(
        {"error": "Invalid input. Please provide positive numbers."}), 400

  panel_count = calculate_realistic_panel_count(roof_size)
  energy_output = calculate_energy_output(panel_count)
  panel_cost, installation_cost, total_cost = calculate_costs(panel_count)
  monthly_savings = calculate_savings(energy_output, current_bill)
  payback_period = calculate_payback_period(total_cost, monthly_savings)

  result = {
      "roof_size_sqm": roof_size,
      "realistic_panel_count": panel_count,
      "monthly_energy_output_kWh": energy_output,
      "panel_cost_usd": panel_cost,
      "installation_cost_usd": installation_cost,
      "total_cost_usd": total_cost,
      "monthly_savings_usd": monthly_savings,
      "estimated_payback_period_years": payback_period
  }

  return jsonify(result)


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
